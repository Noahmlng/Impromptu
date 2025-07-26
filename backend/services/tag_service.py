#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
标签服务模块
包含标签生成、管理和查询功能
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Optional, Dict, List
import json
import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.services.database_service import user_metadata_db, user_tags_db
from backend.services.auth_service import get_current_user

router = APIRouter()

# Pydantic模型
class TagRequest(BaseModel):
    name: str
    category: Optional[str] = 'manual'
    confidence: Optional[float] = 1.0

class BatchTagRequest(BaseModel):
    tags: List[TagRequest]

class GenerateTagsRequest(BaseModel):
    request_type: Optional[str] = '找队友'  # '找对象' 或 '找队友'

class TagResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict] = None

# 初始化算法组件（延迟加载）
_topic_model = None

def get_topic_model():
    """获取主题建模实例"""
    global _topic_model
    if _topic_model is None:
        try:
            from backend.models.topic_modeling import LDATopicModel
            from configs.config import ConfigManager
            
            config_manager = ConfigManager()
            _topic_model = LDATopicModel(config_manager.topic_config)
        except Exception as e:
            print(f"主题模型初始化失败: {e}")
            _topic_model = None
    return _topic_model

@router.post("/generate", response_model=TagResponse)
async def generate_user_tags(
    request: GenerateTagsRequest,
    current_user: Dict = Depends(get_current_user)
):
    """基于用户元数据生成标签"""
    try:
        user_id = current_user['user_id']
        
        # 获取主题建模实例
        topic_model = get_topic_model()
        if not topic_model:
            raise HTTPException(status_code=500, detail="主题建模服务不可用")
        
        # 获取用户的所有元数据
        metadata_list = await user_metadata_db.get_by_user_id(user_id)
        
        if not metadata_list:
            raise HTTPException(status_code=400, detail="用户元数据为空，请先完善个人信息")
        
        # 构建用户文本描述
        text_parts = []
        for item in metadata_list:
            content = item['content']
            if isinstance(content, str):
                try:
                    content = json.loads(content)
                except json.JSONDecodeError:
                    text_parts.append(content)
                    continue
            
            # 提取文本内容
            if isinstance(content, dict):
                for key, value in content.items():
                    if isinstance(value, str):
                        text_parts.append(value)
                    elif isinstance(value, list):
                        text_parts.extend([str(v) for v in value])
            elif isinstance(content, list):
                text_parts.extend([str(item) for item in content])
        
        user_text = ' '.join(text_parts)
        
        if not user_text.strip():
            raise HTTPException(status_code=400, detail="无法从元数据中提取有效文本")
        
        # 使用主题建模生成标签
        topic_result = topic_model.extract_topics_and_tags(user_text, request.request_type)
        
        # 保存生成的标签到数据库
        saved_tags = []
        for tag_name, confidence in topic_result.extracted_tags.items():
            result = await user_tags_db.add_tag(
                user_id=user_id,
                tag_name=tag_name,
                tag_category='generated',
                confidence_score=confidence,
                tag_source='topic_modeling'
            )
            if result:
                saved_tags.append(result)
        
        return TagResponse(
            success=True,
            message=f"成功生成{len(saved_tags)}个标签",
            data={
                "generated_tags": saved_tags,
                "topics": [(int(tid), float(weight)) for tid, weight in topic_result.topics],
                "user_text_length": len(user_text),
                "request_type": request.request_type
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"标签生成错误: {e}")
        raise HTTPException(status_code=500, detail=f"标签生成失败: {str(e)}")

@router.post("/manual", response_model=TagResponse)
async def add_manual_tags(
    request: BatchTagRequest,
    current_user: Dict = Depends(get_current_user)
):
    """手动添加标签"""
    try:
        user_id = current_user['user_id']
        
        saved_tags = []
        for tag_request in request.tags:
            result = await user_tags_db.add_tag(
                user_id=user_id,
                tag_name=tag_request.name,
                tag_category=tag_request.category,
                confidence_score=tag_request.confidence,
                tag_source='manual'
            )
            if result:
                saved_tags.append(result)
        
        return TagResponse(
            success=True,
            message=f"成功添加{len(saved_tags)}个标签",
            data=saved_tags
        )
        
    except Exception as e:
        print(f"手动添加标签错误: {e}")
        raise HTTPException(status_code=500, detail=f"添加标签失败: {str(e)}")

@router.get("/", response_model=TagResponse)
async def get_user_tags(current_user: Dict = Depends(get_current_user)):
    """获取当前用户的所有标签"""
    try:
        user_id = current_user['user_id']
        tags = await user_tags_db.get_by_user_id(user_id)
        
        # 按类别分组
        tags_by_category = {}
        for tag in tags:
            category = tag['tag_category']
            if category not in tags_by_category:
                tags_by_category[category] = []
            tags_by_category[category].append(tag)
        
        return TagResponse(
            success=True,
            message="获取用户标签成功",
            data={
                "total": len(tags),
                "tags": tags,
                "tags_by_category": tags_by_category
            }
        )
        
    except Exception as e:
        print(f"获取用户标签错误: {e}")
        raise HTTPException(status_code=500, detail=f"获取标签失败: {str(e)}")

@router.delete("/{tag_name}")
async def remove_tag(tag_name: str, current_user: Dict = Depends(get_current_user)):
    """删除指定标签"""
    try:
        user_id = current_user['user_id']
        success = await user_tags_db.remove_tag(user_id, tag_name)
        
        if success:
            return {
                "success": True,
                "message": f"标签 '{tag_name}' 删除成功"
            }
        else:
            raise HTTPException(status_code=404, detail="标签不存在或删除失败")
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"删除标签错误: {e}")
        raise HTTPException(status_code=500, detail=f"删除标签失败: {str(e)}")

@router.get("/pool/all")
async def get_tag_pool(request_type: str = Query(default='all', description='标签类型: all/找对象/找队友')):
    """获取标签池信息"""
    try:
        from backend.models.tag_pool import TagPool
        
        tag_pool = TagPool()
        tags = tag_pool.get_all_tags(request_type)
        
        # 转换为简单列表格式
        tag_list = []
        for category, tag_list_items in tags.items():
            tag_list.extend(tag_list_items)
        
        return {
            "success": True,
            "data": {
                "request_type": request_type,
                "total_tags": len(tag_list),
                "tags_by_category": {str(k): v for k, v in tags.items()},
                "all_tags": tag_list
            }
        }
        
    except Exception as e:
        print(f"获取标签池错误: {e}")
        raise HTTPException(status_code=500, detail=f"获取标签池失败: {str(e)}")

@router.get("/suggestions/{category}")
async def get_tag_suggestions(category: str):
    """获取指定类别的标签建议"""
    try:
        # 根据类别提供标签建议
        suggestions = {
            'personality': ['开朗', '内向', '幽默', '认真', '冒险', '稳重', '创新', '传统'],
            'interests': ['音乐', '电影', '读书', '旅行', '摄影', '美食', '运动', '游戏'],
            'skills': ['编程', '设计', '写作', '演讲', '管理', '分析', '创作', '教学'],
            'values': ['诚实', '责任', '成长', '自由', '安全', '创新', '传统', '平衡'],
            'lifestyle': ['早起', '夜猫子', '健身', '素食', '旅行', '宅家', '社交', '独处'],
            'career': ['创业', '技术', '管理', '销售', '教育', '艺术', '医疗', '金融'],
            'relationship': ['浪漫', '实用', '独立', '依赖', '传统', '开放', '稳定', '激情']
        }
        
        category_suggestions = suggestions.get(category, [])
        
        return {
            "success": True,
            "data": {
                "category": category,
                "suggestions": category_suggestions,
                "total": len(category_suggestions)
            }
        }
        
    except Exception as e:
        print(f"获取标签建议错误: {e}")
        raise HTTPException(status_code=500, detail=f"获取标签建议失败: {str(e)}")

@router.get("/analytics/user")
async def get_user_tag_analytics(current_user: Dict = Depends(get_current_user)):
    """获取用户标签分析"""
    try:
        user_id = current_user['user_id']
        tags = await user_tags_db.get_by_user_id(user_id)
        
        # 分析标签分布
        category_count = {}
        source_count = {}
        confidence_distribution = {'high': 0, 'medium': 0, 'low': 0}
        
        for tag in tags:
            # 类别统计
            category = tag['tag_category']
            category_count[category] = category_count.get(category, 0) + 1
            
            # 来源统计
            source = tag['tag_source']
            source_count[source] = source_count.get(source, 0) + 1
            
            # 置信度分布
            confidence = tag['confidence_score']
            if confidence >= 0.8:
                confidence_distribution['high'] += 1
            elif confidence >= 0.5:
                confidence_distribution['medium'] += 1
            else:
                confidence_distribution['low'] += 1
        
        # 最高置信度标签
        top_confidence_tags = sorted(tags, key=lambda x: x['confidence_score'], reverse=True)[:5]
        
        return {
            "success": True,
            "data": {
                "total_tags": len(tags),
                "category_distribution": category_count,
                "source_distribution": source_count,
                "confidence_distribution": confidence_distribution,
                "top_confidence_tags": [
                    {
                        "name": tag['tag_name'],
                        "confidence": tag['confidence_score'],
                        "category": tag['tag_category']
                    } for tag in top_confidence_tags
                ]
            }
        }
        
    except Exception as e:
        print(f"获取标签分析错误: {e}")
        raise HTTPException(status_code=500, detail=f"获取标签分析失败: {str(e)}")

@router.post("/batch/update")
async def batch_update_tags(
    request: BatchTagRequest,
    current_user: Dict = Depends(get_current_user)
):
    """批量更新标签（替换所有手动标签）"""
    try:
        user_id = current_user['user_id']
        
        # 先删除所有手动标签
        current_tags = await user_tags_db.get_by_user_id(user_id)
        for tag in current_tags:
            if tag['tag_source'] == 'manual':
                await user_tags_db.remove_tag(user_id, tag['tag_name'])
        
        # 添加新的手动标签
        saved_tags = []
        for tag_request in request.tags:
            result = await user_tags_db.add_tag(
                user_id=user_id,
                tag_name=tag_request.name,
                tag_category=tag_request.category,
                confidence_score=tag_request.confidence,
                tag_source='manual'
            )
            if result:
                saved_tags.append(result)
        
        return TagResponse(
            success=True,
            message=f"成功更新{len(saved_tags)}个标签",
            data=saved_tags
        )
        
    except Exception as e:
        print(f"批量更新标签错误: {e}")
        raise HTTPException(status_code=500, detail=f"批量更新标签失败: {str(e)}")

@router.get("/trending/{category}")
async def get_trending_tags(category: str = 'all'):
    """获取热门标签（基于用户使用频率）"""
    try:
        # 这里可以实现基于数据库统计的热门标签
        # 目前返回模拟数据
        trending_tags = {
            'all': ['创新', '团队合作', '技术', '成长', '开朗', '旅行', '音乐', '阅读'],
            'personality': ['开朗', '幽默', '认真', '创新'],
            'interests': ['旅行', '音乐', '阅读', '摄影'],
            'skills': ['编程', '设计', '管理', '沟通'],
            'career': ['技术', '创业', '管理', '教育']
        }
        
        tags = trending_tags.get(category, trending_tags['all'])
        
        return {
            "success": True,
            "data": {
                "category": category,
                "trending_tags": tags,
                "total": len(tags)
            }
        }
        
    except Exception as e:
        print(f"获取热门标签错误: {e}")
        raise HTTPException(status_code=500, detail=f"获取热门标签失败: {str(e)}") 