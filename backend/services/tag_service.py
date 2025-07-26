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

from backend.services.database_service import user_metadata_db, user_tags_db, conversation_db
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
    include_conversation: Optional[bool] = False  # 是否包含对话记录

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
            import os
            
            print("🤖 [TagService] 初始化主题建模实例...")
            config_manager = ConfigManager()
            _topic_model = LDATopicModel(config_manager.topic_config)
            
            # 检查并加载生产模型
            production_model_path = "data/models/production_model"
            if (os.path.exists(f"{production_model_path}_lda") and 
                os.path.exists(f"{production_model_path}_dict") and 
                os.path.exists(f"{production_model_path}_tag_mapping.json")):
                try:
                    _topic_model.load_model(production_model_path)
                    print("✅ 标签服务已加载生产LDA模型")
                except Exception as load_e:
                    print(f"⚠️ 标签服务加载生产模型失败: {load_e}")
                    print("🔄 [TagService] 将使用临时训练模式")
                    _initialize_temp_model(_topic_model)
            else:
                print("⚠️ 生产模型文件不完整，将使用临时训练模式")
                _initialize_temp_model(_topic_model)
                
        except Exception as e:
            print(f"❌ 主题模型初始化失败: {e}")
            import traceback
            print(f"详细错误: {traceback.format_exc()}")
            _topic_model = None
    return _topic_model

def _initialize_temp_model(topic_model):
    """初始化临时模型用于标签生成"""
    try:
        print("🔧 [TagService] 初始化临时主题模型...")
        # 创建一些基本的训练文档
        temp_docs = [
            "我是一个AI人工智能工程师，喜欢技术创新和产品开发，希望找到志同道合的创业伙伴",
            "我从事产品管理工作，热爱用户体验设计，寻找技术合作伙伴一起创业做有意义的产品"
        ]
        
        topic_model.train(temp_docs)
        print("✅ [TagService] 临时主题模型训练完成")
        
    except Exception as e:
        print(f"⚠️ [TagService] 临时模型初始化失败: {e}")
        # 即使失败也不抛出异常，让系统继续运行

@router.post("/generate", response_model=TagResponse)
async def generate_user_tags(
    request: GenerateTagsRequest,
    current_user: Dict = Depends(get_current_user)
):
    """基于用户元数据生成标签"""
    return await generate_user_tags_with_conversation(request, current_user)

async def generate_user_tags_with_conversation(
    request: GenerateTagsRequest,
    current_user: Dict
) -> TagResponse:
    """基于用户元数据和对话记录生成标签"""
    try:
        user_id = current_user['user_id']
        print(f"🏷️ [TagService] 开始为用户 {user_id} 生成标签，请求类型: {request.request_type}")
        print(f"🏷️ [TagService] 包含对话记录: {request.include_conversation}")
        
        # 获取主题建模实例
        topic_model = get_topic_model()
        if not topic_model:
            print("❌ [TagService] 主题建模实例为空")
            raise HTTPException(status_code=500, detail="主题建模服务不可用")
        
        print("✅ [TagService] 主题建模实例已获取")
        
        # 获取用户的所有元数据
        metadata_list = await user_metadata_db.get_by_user_id(user_id)
        print(f"📊 [TagService] 获取到 {len(metadata_list) if metadata_list else 0} 条元数据")
        
        # 构建用户文本描述
        text_parts = []
        
        # 1. 处理元数据
        if metadata_list:
            for i, item in enumerate(metadata_list):
                print(f"📄 [TagService] 处理元数据项 {i+1}: {item.get('section_type', 'unknown')}.{item.get('section_key', 'unknown')}")
                content = item['content']
                
                if isinstance(content, str):
                    try:
                        content = json.loads(content)
                        print(f"📝 [TagService] 成功解析JSON内容")
                    except json.JSONDecodeError:
                        text_parts.append(content)
                        print(f"📝 [TagService] 添加字符串内容: {content[:50]}...")
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
        
        # 2. 处理对话记录（如果请求包含）
        conversation_text = ""
        if request.include_conversation:
            print("💬 [TagService] 开始提取对话记录...")
            theme_mode = request.request_type if request.request_type in ['romantic', 'team'] else None
            conversation_text = await conversation_db.extract_conversation_text(user_id, theme_mode)
            
            if conversation_text:
                text_parts.append(conversation_text)
                print(f"💬 [TagService] 添加对话文本: {len(conversation_text)} 字符")
            else:
                print("💬 [TagService] 未找到相关对话记录")
        
        user_text = ' '.join(text_parts)
        print(f"📝 [TagService] 合并后文本长度: {len(user_text)} 字符")
        print(f"📝 [TagService] 文本预览: {user_text[:200]}...")
        
        if not user_text.strip():
            print("❌ [TagService] 提取的文本为空")
            error_msg = "无法从元数据中提取有效文本"
            if request.include_conversation:
                error_msg += "，且未找到对话记录"
            raise HTTPException(status_code=400, detail=error_msg)
        
        # 使用主题建模生成标签
        print("🤖 [TagService] 开始主题建模分析...")
        try:
            topic_result = topic_model.extract_topics_and_tags(user_text, request.request_type)
            print(f"✅ [TagService] 主题建模完成，提取到 {len(topic_result.extracted_tags)} 个标签")
            print(f"🏷️ [TagService] 提取的标签: {list(topic_result.extracted_tags.keys())[:10]}")
        except Exception as topic_error:
            print(f"❌ [TagService] 主题建模失败: {topic_error}")
            raise HTTPException(status_code=500, detail=f"主题建模处理失败: {str(topic_error)}")
        
        # 先删除所有现有的generated标签
        print("🧹 [TagService] 清理现有生成的标签...")
        existing_tags = await user_tags_db.get_by_user_id(user_id)
        removed_count = 0
        for tag in existing_tags:
            if tag.get('tag_source') == 'topic_modeling' or tag.get('tag_category') == 'generated':
                await user_tags_db.remove_tag(user_id, tag['tag_name'])
                removed_count += 1
        print(f"🧹 [TagService] 已删除 {removed_count} 个旧标签")
        
        # 保存生成的标签到数据库
        print("💾 [TagService] 保存新生成的标签...")
        saved_tags = []
        tag_source = 'topic_modeling_with_chat' if request.include_conversation and conversation_text else 'topic_modeling'
        
        for tag_name, confidence in topic_result.extracted_tags.items():
            try:
                result = await user_tags_db.add_tag(
                    user_id=user_id,
                    tag_name=tag_name,
                    tag_category='generated',
                    confidence_score=confidence,
                    tag_source=tag_source
                )
                if result:
                    saved_tags.append(result)
                    print(f"💾 [TagService] 已保存标签: {tag_name} (置信度: {confidence:.2f})")
            except Exception as save_error:
                print(f"⚠️ [TagService] 保存标签失败 {tag_name}: {save_error}")
        
        print(f"✅ [TagService] 成功保存 {len(saved_tags)} 个标签")
        
        return TagResponse(
            success=True,
            message=f"成功生成{len(saved_tags)}个标签" + ("（包含对话记录分析）" if request.include_conversation and conversation_text else ""),
            data={
                "generated_tags": saved_tags,
                "topics": [(int(tid), float(weight)) for tid, weight in topic_result.topics],
                "user_text_length": len(user_text),
                "conversation_text_length": len(conversation_text) if conversation_text else 0,
                "request_type": request.request_type,
                "included_conversation": request.include_conversation and bool(conversation_text),
                "tag_source": tag_source
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

@router.post("/generate/with-conversation", response_model=TagResponse)
async def generate_tags_with_conversation(
    request: GenerateTagsRequest,
    current_user: Dict = Depends(get_current_user)
):
    """基于用户元数据和对话记录生成标签的专用接口"""
    # 强制启用对话记录包含
    request.include_conversation = True
    return await generate_user_tags_with_conversation(request, current_user)

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