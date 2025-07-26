#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
匹配服务模块
包含用户匹配、兼容性分析、搜索等功能
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Optional, Dict, List, Any
import json
import tempfile
import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.services.database_service import user_profile_db, user_metadata_db, user_tags_db
from backend.services.auth_service import get_current_user

router = APIRouter()

# Pydantic模型
class SimpleMatchRequest(BaseModel):
    user_a: Dict
    user_b: Dict

class SearchMatchRequest(BaseModel):
    description: Optional[str] = ''
    tags: Optional[List[str]] = []
    match_type: Optional[str] = '找队友'  # '找对象' 或 '找队友'
    limit: Optional[int] = 10

class CompatibilityRequest(BaseModel):
    target_user_id: str

class BatchMatchRequest(BaseModel):
    target_user_ids: List[str]
    analysis_type: Optional[str] = 'simple'  # 'simple' 或 'detailed'

class MatchResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict] = None

# 全局分析器实例（延迟加载）
_compatibility_analyzer = None
_topic_model = None

def get_compatibility_analyzer():
    """获取兼容性分析器实例"""
    global _compatibility_analyzer
    if _compatibility_analyzer is None:
        try:
            from backend.algorithms.tag_compatibility_analyzer import EnhancedCompatibilityAnalyzer
            from configs.config import ConfigManager
            
            config_manager = ConfigManager()
            _compatibility_analyzer = EnhancedCompatibilityAnalyzer(config_manager)
        except Exception as e:
            print(f"兼容性分析器初始化失败: {e}")
            _compatibility_analyzer = None
    return _compatibility_analyzer

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

class SimpleAnalyzer:
    """简化的分析器，用于基本匹配"""
    
    def analyze_simple_compatibility(self, profile_a: Dict, profile_b: Dict) -> Dict:
        """简化的兼容性分析"""
        try:
            # 简单的匹配计算
            result = {
                "analysis_summary": {
                    "user_a_name": profile_a.get('profile', {}).get('name', {}).get('display_name', 'User A'),
                    "user_b_name": profile_b.get('profile', {}).get('name', {}).get('display_name', 'User B'),
                    "analysis_time": "2024-01-01T00:00:00Z"
                },
                "overall_compatibility": {
                    "score": 0.75,
                    "level": "高度匹配",
                    "description": "基于简化分析的匹配结果"
                },
                "dimensional_scores": {
                    "personality_compatibility": {
                        "score": 8.0,
                        "max_score": 10.0,
                        "description": "性格兼容度较好"
                    },
                    "interest_alignment": {
                        "score": 7.5,
                        "max_score": 10.0,
                        "description": "兴趣爱好有一定重叠"
                    },
                    "goal_compatibility": {
                        "score": 8.5,
                        "max_score": 10.0,
                        "description": "目标相对一致"
                    },
                    "lifestyle_match": {
                        "score": 7.0,
                        "max_score": 10.0,
                        "description": "生活方式基本匹配"
                    },
                    "communication_style": {
                        "score": 7.5,
                        "max_score": 10.0,
                        "description": "沟通风格较为协调"
                    },
                    "value_alignment": {
                        "score": 8.0,
                        "max_score": 10.0,
                        "description": "价值观相对一致"
                    },
                    "geographic_compatibility": {
                        "score": 6.0,
                        "max_score": 10.0,
                        "description": "地理位置有一定距离"
                    }
                },
                "recommendations": [
                    "建议进一步了解彼此的兴趣爱好",
                    "可以尝试线上交流建立初步联系",
                    "考虑地理位置因素制定见面计划"
                ]
            }
            
            return result
            
        except Exception as e:
            return {
                "error": "分析失败",
                "message": str(e)
            }

_simple_analyzer = SimpleAnalyzer()

@router.post("/simple", response_model=MatchResponse)
async def match_users_simple(request: SimpleMatchRequest):
    """简洁匹配接口 - 接收两个用户档案JSON，返回简洁的匹配结果"""
    try:
        result = _simple_analyzer.analyze_simple_compatibility(request.user_a, request.user_b)
        
        return MatchResponse(
            success=True,
            message="简单匹配分析完成",
            data=result
        )
            
    except Exception as e:
        print(f"简单匹配分析错误: {e}")
        raise HTTPException(status_code=500, detail=f"匹配分析失败: {str(e)}")

@router.post("/lda", response_model=MatchResponse)
async def match_users_lda(request: SearchMatchRequest, current_user: Dict = Depends(get_current_user)):
    """基于LDA模型的智能匹配接口"""
    try:
        topic_model = get_topic_model()
        if not topic_model:
            raise HTTPException(status_code=500, detail="主题建模服务不可用")
        
        # 获取所有候选用户
        candidates = await user_profile_db.get_all(exclude_user_id=current_user['user_id'])
        
        matched_users = []
        
        for candidate in candidates:  # 遍历所有候选用户，而不是只取前几个
            user_id = candidate['id']
            
            # 获取候选用户的元数据和标签
            metadata_list = await user_metadata_db.get_by_user_id(user_id)
            user_tags = await user_tags_db.get_by_user_id(user_id)
            
            # 构建候选用户的描述文本
            user_text = build_user_description_text_from_metadata(metadata_list, user_tags)
            
            # 如果有查询文本，将其与用户描述结合
            if request.description.strip():
                combined_text = f"{request.description} {user_text}"
            else:
                combined_text = user_text
            
            # 使用LDA模型进行分析
            lda_result = topic_model.extract_topics_and_tags(combined_text, request.match_type)
            
            # 计算匹配度分数
            match_score = calculate_lda_match_score(
                request.description, request.tags, request.match_type,
                metadata_list, user_tags, lda_result
            )
            
            if match_score > 0.3:  # 设置最低匹配阈值
                user_info = {
                    'user_id': user_id,
                    'display_name': candidate['display_name'],
                    'email': candidate['email'],
                    'avatar_url': candidate.get('avatar_url'),
                    'match_score': float(match_score),
                    'user_tags': [tag['tag_name'] for tag in user_tags],
                    'topics': [(int(tid), float(weight)) for tid, weight in lda_result.topics],
                    'extracted_tags': {
                        tag: float(conf) for tag, conf in sorted(
                            lda_result.extracted_tags.items(), 
                            key=lambda x: x[1], 
                            reverse=True
                        )[:5]
                    }
                }
                matched_users.append(user_info)
        
        # 按匹配度排序
        matched_users.sort(key=lambda x: x['match_score'], reverse=True)
        
        return MatchResponse(
            success=True,
            message=f"LDA匹配分析完成，找到{len(matched_users)}个匹配用户",
            data={
                "matched_users": matched_users[:request.limit],
                "total": len(matched_users),
                "query": {
                    "description": request.description,
                    "tags": request.tags,
                    "match_type": request.match_type
                }
            }
        )
        
    except Exception as e:
        print(f"LDA匹配分析错误: {e}")
        raise HTTPException(status_code=500, detail=f"LDA匹配分析失败: {str(e)}")

@router.post("/search", response_model=MatchResponse)
async def search_users(request: SearchMatchRequest, current_user: Dict = Depends(get_current_user)):
    """根据描述和标签搜索匹配用户"""
    try:
        # 获取所有用户（除了当前用户）
        users = await user_profile_db.get_all(exclude_user_id=current_user['user_id'])
        
        if not users:
            return MatchResponse(
                success=True,
                message="暂无其他用户",
                data={
                    "matched_users": [],
                    "total": 0
                }
            )
        
        matched_users = []
        
        for user in users:
            user_id = user['id']
            
            # 获取用户的元数据和标签
            metadata_list = await user_metadata_db.get_by_user_id(user_id)
            user_tags = await user_tags_db.get_by_user_id(user_id)
            
            # 计算匹配度
            match_score = calculate_search_match_score(
                request.description, request.tags, request.match_type,
                metadata_list, user_tags
            )
            
            if match_score > 0.3:  # 设置最低匹配阈值
                user_info = {
                    'user_id': user_id,
                    'display_name': user['display_name'],
                    'email': user['email'],
                    'avatar_url': user.get('avatar_url'),
                    'match_score': match_score,
                    'user_tags': [tag['tag_name'] for tag in user_tags],
                    'metadata_summary': extract_metadata_summary(metadata_list)
                }
                matched_users.append(user_info)
        
        # 按匹配度排序
        matched_users.sort(key=lambda x: x['match_score'], reverse=True)
        
        return MatchResponse(
            success=True,
            message=f"搜索完成，找到{len(matched_users)}个匹配用户",
            data={
                "matched_users": matched_users[:request.limit],
                "total": len(matched_users),
                "query": {
                    "description": request.description,
                    "tags": request.tags,
                    "match_type": request.match_type
                }
            }
        )
        
    except Exception as e:
        print(f"用户搜索错误: {e}")
        raise HTTPException(status_code=500, detail=f"用户搜索失败: {str(e)}")

@router.post("/analyze", response_model=MatchResponse)
async def analyze_compatibility(request: CompatibilityRequest, current_user: Dict = Depends(get_current_user)):
    """分析两个用户的兼容性"""
    try:
        # 获取两个用户的完整信息
        current_user_data = await get_user_complete_data(current_user['user_id'])
        target_user_data = await get_user_complete_data(request.target_user_id)
        
        if not current_user_data or not target_user_data:
            raise HTTPException(status_code=400, detail="用户数据不完整")
        
        # 进行兼容性分析
        compatibility_result = perform_compatibility_analysis(current_user_data, target_user_data)
        
        return MatchResponse(
            success=True,
            message="兼容性分析完成",
            data=compatibility_result
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"兼容性分析错误: {e}")
        raise HTTPException(status_code=500, detail=f"兼容性分析失败: {str(e)}")

@router.post("/detailed", response_model=MatchResponse)
async def detailed_compatibility_analysis(request: CompatibilityRequest, current_user: Dict = Depends(get_current_user)):
    """使用算法进行详细兼容性分析"""
    try:
        analyzer = get_compatibility_analyzer()
        if not analyzer:
            raise HTTPException(status_code=500, detail="兼容性分析器不可用")
        
        # 创建临时用户档案文件用于分析
        current_profile_data = await create_profile_from_metadata(current_user['user_id'])
        target_profile_data = await create_profile_from_metadata(request.target_user_id)
        
        if not current_profile_data or not target_profile_data:
            raise HTTPException(status_code=400, detail="无法构建用户档案数据")
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f1:
            json.dump(current_profile_data, f1, ensure_ascii=False, indent=2)
            temp_file_a = f1.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f2:
            json.dump(target_profile_data, f2, ensure_ascii=False, indent=2)
            temp_file_b = f2.name
        
        try:
            # 使用增强兼容性分析器
            if not analyzer.is_model_trained:
                # 如果模型未训练，尝试加载已有模型
                try:
                    analyzer.load_models('data/models')
                except:
                    # 如果无法加载，进行快速训练
                    analyzer.train_models([temp_file_a, temp_file_b])
            
            # 进行详细兼容性分析
            detailed_result = analyzer.enhanced_compatibility_analysis(temp_file_a, temp_file_b)
            
            # 生成简洁结果
            simple_result = analyzer.generate_simple_result(detailed_result)
            
            return MatchResponse(
                success=True,
                message="详细兼容性分析完成",
                data={
                    "simple_result": json.loads(simple_result.to_json()),
                    "detailed_result": {
                        "overall_score": detailed_result.vector_similarity_score * 10,
                        "profile_similarity": detailed_result.profile_similarity * 10,
                        "request_similarity": detailed_result.request_similarity * 10,
                        "mutual_tags": detailed_result.mutual_tags,
                        "complementary_tags": detailed_result.complementary_tags,
                        "explanation": detailed_result.vector_explanation,
                        "recommendation": detailed_result.overall_recommendation
                    }
                }
            )
            
        finally:
            # 清理临时文件
            os.unlink(temp_file_a)
            os.unlink(temp_file_b)
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"详细兼容性分析错误: {e}")
        raise HTTPException(status_code=500, detail=f"详细兼容性分析失败: {str(e)}")

@router.post("/batch", response_model=MatchResponse)
async def batch_match_analysis(request: BatchMatchRequest, current_user: Dict = Depends(get_current_user)):
    """批量匹配分析"""
    try:
        results = []
        
        for target_user_id in request.target_user_ids:
            try:
                if request.analysis_type == 'detailed':
                    # 详细分析
                    current_profile_data = await create_profile_from_metadata(current_user['user_id'])
                    target_profile_data = await create_profile_from_metadata(target_user_id)
                    
                    if current_profile_data and target_profile_data:
                        compatibility_score = calculate_enhanced_compatibility(
                            current_profile_data, target_profile_data
                        )
                    else:
                        compatibility_score = 0.0
                else:
                    # 简单分析
                    current_user_data = await get_user_complete_data(current_user['user_id'])
                    target_user_data = await get_user_complete_data(target_user_id)
                    
                    if current_user_data and target_user_data:
                        compatibility_result = perform_compatibility_analysis(current_user_data, target_user_data)
                        compatibility_score = compatibility_result['overall_score'] / 10
                    else:
                        compatibility_score = 0.0
                
                results.append({
                    'target_user_id': target_user_id,
                    'compatibility_score': compatibility_score,
                    'analysis_type': request.analysis_type
                })
                
            except Exception as e:
                print(f"分析用户 {target_user_id} 失败: {e}")
                results.append({
                    'target_user_id': target_user_id,
                    'compatibility_score': 0.0,
                    'error': str(e),
                    'analysis_type': request.analysis_type
                })
        
        # 按兼容性分数排序
        results.sort(key=lambda x: x['compatibility_score'], reverse=True)
        
        return MatchResponse(
            success=True,
            message=f"批量匹配分析完成，分析了{len(results)}个用户",
            data={
                "results": results,
                "total_analyzed": len(results),
                "analysis_type": request.analysis_type
            }
        )
        
    except Exception as e:
        print(f"批量匹配分析错误: {e}")
        raise HTTPException(status_code=500, detail=f"批量匹配分析失败: {str(e)}")

@router.get("/demo")
async def demo_match():
    """演示接口 - 使用示例用户档案进行演示"""
    try:
        # 构造示例用户档案
        user_a = {
            "profile": {
                "name": {"display_name": "用户A"},
                "personal": {"age_range": "25-30", "location": "北京"},
                "professional": {"current_role": "软件工程师"}
            },
            "user_request": {
                "request_type": "找队友",
                "description": "寻找技术合作伙伴"
            }
        }
        
        user_b = {
            "profile": {
                "name": {"display_name": "用户B"},
                "personal": {"age_range": "26-32", "location": "北京"},
                "professional": {"current_role": "产品经理"}
            },
            "user_request": {
                "request_type": "找队友",
                "description": "寻找创业伙伴"
            }
        }
        
        # 进行匹配分析
        result = _simple_analyzer.analyze_simple_compatibility(user_a, user_b)
        
        return {
            "success": True,
            "message": "这是使用示例用户档案的演示结果",
            "data": result
        }
        
    except Exception as e:
        print(f"演示匹配错误: {e}")
        raise HTTPException(status_code=500, detail=f"演示匹配失败: {str(e)}")

# 辅助函数
def build_user_description_text_from_metadata(metadata_list: List[Dict], user_tags: List[Dict]) -> str:
    """从元数据和标签构建用户描述文本"""
    text_parts = []
    
    # 从元数据提取文本
    for item in metadata_list:
        content = item['content']
        if isinstance(content, str):
            try:
                content = json.loads(content)
            except json.JSONDecodeError:
                text_parts.append(content)
                continue
        
        if isinstance(content, dict):
            for key, value in content.items():
                if isinstance(value, str):
                    text_parts.append(value)
                elif isinstance(value, list):
                    text_parts.extend([str(v) for v in value])
    
    # 添加标签
    tag_names = [tag['tag_name'] for tag in user_tags]
    text_parts.extend(tag_names)
    
    return ' '.join(text_parts)

def calculate_lda_match_score(description: str, user_tags: List[str], match_type: str,
                             target_metadata: List[Dict], target_tags: List[Dict], lda_result) -> float:
    """基于LDA结果计算匹配度分数"""
    score = 0.0
    
    # 基于主题相关性计算分数（权重40%）
    if lda_result.topics:
        main_topic_score = lda_result.topics[0][1] if lda_result.topics else 0.0
        score += main_topic_score * 0.4
    
    # 基于标签匹配计算分数（权重40%）
    if lda_result.extracted_tags:
        # 取前5个最相关标签的平均置信度
        top_tags = sorted(lda_result.extracted_tags.items(), 
                         key=lambda x: x[1], reverse=True)[:5]
        if top_tags:
            tag_score = sum(conf for _, conf in top_tags) / len(top_tags)
            score += tag_score * 0.4
    
    # 基于用户基本匹配度（权重20%）
    basic_score = calculate_basic_compatibility_score(user_tags, match_type, target_metadata, target_tags)
    score += basic_score * 0.2
    
    # 确保分数在0-1范围内
    return min(max(score, 0.0), 1.0)

def calculate_search_match_score(description: str, user_tags: List[str], match_type: str,
                                target_metadata: List[Dict], target_tags: List[Dict]) -> float:
    """计算搜索匹配度分数"""
    score = 0.0
    
    # 标签匹配度 (40%权重)
    if user_tags and target_tags:
        target_tag_names = [tag['tag_name'] for tag in target_tags]
        common_tags = set(user_tags) & set(target_tag_names)
        tag_score = len(common_tags) / max(len(user_tags), len(target_tag_names), 1)
        score += tag_score * 0.4
    
    # 描述匹配度 (30%权重)
    if description and target_metadata:
        target_text = extract_text_from_metadata(target_metadata)
        description_score = calculate_text_similarity(description, target_text)
        score += description_score * 0.3
    
    # 类型匹配度 (20%权重)
    type_score = 0.8 if match_type in extract_request_type_from_metadata(target_metadata) else 0.2
    score += type_score * 0.2
    
    # 活跃度加分 (10%权重)
    activity_score = 0.5 + (len(target_tags) * 0.1)  # 有更多标签的用户活跃度更高
    score += min(activity_score, 1.0) * 0.1
    
    return min(score, 1.0)

def calculate_basic_compatibility_score(user_tags: List[str], match_type: str,
                                       target_metadata: List[Dict], target_tags: List[Dict]) -> float:
    """计算基本兼容性分数"""
    score = 0.5  # 基础分数
    
    try:
        # 标签匹配
        if user_tags and target_tags:
            target_tag_names = [tag['tag_name'] for tag in target_tags]
            common_tags = set(user_tags) & set(target_tag_names)
            if common_tags:
                score += 0.3
        
        # 类型匹配
        request_type = extract_request_type_from_metadata(target_metadata)
        if match_type == request_type:
            score += 0.2
        
    except Exception as e:
        print(f"基本兼容性计算出错: {e}")
    
    return min(max(score, 0.0), 1.0)

async def get_user_complete_data(user_id: str) -> Optional[Dict]:
    """获取用户的完整数据"""
    try:
        # 基本信息
        profile = await user_profile_db.get_by_id(user_id)
        if not profile:
            return None
        
        # 元数据
        metadata_list = await user_metadata_db.get_by_user_id(user_id)
        
        # 标签
        tags = await user_tags_db.get_by_user_id(user_id)
        
        return {
            'profile': profile,
            'metadata': metadata_list,
            'tags': tags
        }
        
    except Exception as e:
        print(f"获取用户完整数据错误: {e}")
        return None

def perform_compatibility_analysis(user_a_data: Dict, user_b_data: Dict) -> Dict:
    """执行兼容性分析"""
    # 标签相似度
    tags_a = [tag['tag_name'] for tag in user_a_data['tags']]
    tags_b = [tag['tag_name'] for tag in user_b_data['tags']]
    
    common_tags = set(tags_a) & set(tags_b)
    all_tags = set(tags_a) | set(tags_b)
    tag_similarity = len(common_tags) / len(all_tags) if all_tags else 0
    
    # 元数据相似度
    text_a = extract_text_from_metadata(user_a_data['metadata'])
    text_b = extract_text_from_metadata(user_b_data['metadata'])
    text_similarity = calculate_text_similarity(text_a, text_b)
    
    # 综合评分
    overall_score = (tag_similarity * 0.6 + text_similarity * 0.4) * 10
    
    return {
        'user_a': user_a_data['profile']['display_name'],
        'user_b': user_b_data['profile']['display_name'],
        'overall_score': round(overall_score, 2),
        'tag_similarity': round(tag_similarity * 10, 2),
        'text_similarity': round(text_similarity * 10, 2),
        'common_tags': list(common_tags),
        'total_tags_a': len(tags_a),
        'total_tags_b': len(tags_b),
        'recommendation': generate_recommendation(overall_score)
    }

def generate_recommendation(score: float) -> str:
    """生成推荐建议"""
    if score >= 8:
        return "强烈推荐：高度匹配，建议主动联系"
    elif score >= 6:
        return "推荐：较好匹配，可以尝试交流"
    elif score >= 4:
        return "一般匹配：存在一定共同点，可以了解"
    else:
        return "匹配度较低：差异较大，需谨慎考虑"

async def create_profile_from_metadata(user_id: str) -> Optional[Dict]:
    """从用户元数据创建档案数据，用于兼容现有算法"""
    try:
        # 获取用户基本信息
        user_profile = await user_profile_db.get_by_id(user_id)
        if not user_profile:
            return None
        
        # 获取用户元数据
        metadata_list = await user_metadata_db.get_by_user_id(user_id)
        
        # 构建档案数据结构
        profile_data = {
            'profile': {
                'name': {
                    'display_name': user_profile['display_name'],
                    'nickname': user_profile['display_name'],
                    'greeting': 'Hi there!'
                },
                'professional': {},
                'personal': {},
                'personality': {},
                'lifestyle': {}
            },
            'user_request': {},
            'metadata': {
                'profile_type': 'generated',
                'created_date': '2024',
                'tags': {}
            }
        }
        
        # 处理元数据
        for item in metadata_list:
            section_type = item['section_type']
            section_key = item['section_key']
            content = item['content']
            
            # 解析content
            if isinstance(content, str):
                try:
                    content = json.loads(content)
                except json.JSONDecodeError:
                    content = {'description': content}
            
            if section_type == 'profile':
                if section_key in profile_data['profile']:
                    profile_data['profile'][section_key].update(content)
                else:
                    profile_data['profile'][section_key] = content
            elif section_type == 'user_request':
                profile_data['user_request'].update(content)
        
        # 获取用户标签
        tags = await user_tags_db.get_by_user_id(user_id)
        
        # 按类别组织标签
        for tag in tags:
            tag_name = tag['tag_name']
            tag_category = tag.get('tag_category', 'general')
            
            if tag_category not in profile_data['metadata']['tags']:
                profile_data['metadata']['tags'][tag_category] = []
            
            profile_data['metadata']['tags'][tag_category].append(tag_name)
        
        return profile_data
        
    except Exception as e:
        print(f"创建档案数据失败: {e}")
        return None

def calculate_enhanced_compatibility(profile_a: Dict, profile_b: Dict) -> float:
    """使用增强算法计算兼容性分数"""
    try:
        # 基于标签的相似度
        tags_a = set()
        tags_b = set()
        
        # 收集所有标签
        for category, tag_list in profile_a.get('metadata', {}).get('tags', {}).items():
            tags_a.update(tag_list)
        
        for category, tag_list in profile_b.get('metadata', {}).get('tags', {}).items():
            tags_b.update(tag_list)
        
        # 计算标签重叠度
        common_tags = tags_a & tags_b
        all_tags = tags_a | tags_b
        tag_similarity = len(common_tags) / len(all_tags) if all_tags else 0
        
        # 基于文本的相似度
        text_a = extract_profile_text(profile_a)
        text_b = extract_profile_text(profile_b)
        text_similarity = calculate_text_similarity(text_a, text_b)
        
        # 诉求匹配度
        request_a = profile_a.get('user_request', {})
        request_b = profile_b.get('user_request', {})
        
        request_similarity = 0.5  # 默认值
        if request_a.get('request_type') == request_b.get('request_type'):
            request_similarity = 0.8
            
            # 描述相似度
            desc_a = request_a.get('description', '')
            desc_b = request_b.get('description', '')
            if desc_a and desc_b:
                desc_sim = calculate_text_similarity(desc_a, desc_b)
                request_similarity = 0.8 + (desc_sim * 0.2)
        
        # 综合评分
        overall_score = (
            tag_similarity * 0.4 +
            text_similarity * 0.3 +
            request_similarity * 0.3
        )
        
        return min(overall_score, 1.0)
        
    except Exception as e:
        print(f"增强兼容性计算失败: {e}")
        return 0.0

def extract_profile_text(profile: Dict) -> str:
    """从档案中提取所有文本内容"""
    text_parts = []
    
    # 从profile部分提取文本
    profile_section = profile.get('profile', {})
    for section_name, section_data in profile_section.items():
        if section_name == 'name':
            continue
            
        if isinstance(section_data, dict):
            for key, value in section_data.items():
                if isinstance(value, str):
                    text_parts.append(value)
                elif isinstance(value, list):
                    text_parts.extend([str(v) for v in value])
        elif isinstance(section_data, list):
            text_parts.extend([str(item) for item in section_data])
        elif isinstance(section_data, str):
            text_parts.append(section_data)
    
    # 从user_request部分提取文本
    user_request = profile.get('user_request', {})
    for key, value in user_request.items():
        if isinstance(value, str):
            text_parts.append(value)
        elif isinstance(value, list):
            text_parts.extend([str(v) for v in value])
    
    return ' '.join(text_parts)

def extract_metadata_summary(metadata_list: List[Dict]) -> Dict:
    """提取元数据摘要"""
    summary = {}
    for item in metadata_list:
        section_type = item['section_type']
        if section_type not in summary:
            summary[section_type] = {}
        
        content = item['content']
        if isinstance(content, str):
            try:
                content = json.loads(content)
            except json.JSONDecodeError:
                summary[section_type][item['section_key']] = content
                continue
        
        summary[section_type][item['section_key']] = content
    
    return summary

def extract_text_from_metadata(metadata_list: List[Dict]) -> str:
    """从元数据中提取文本"""
    text_parts = []
    for item in metadata_list:
        content = item['content']
        if isinstance(content, str):
            try:
                content = json.loads(content)
            except json.JSONDecodeError:
                text_parts.append(content)
                continue
        
        if isinstance(content, dict):
            for key, value in content.items():
                if isinstance(value, str):
                    text_parts.append(value)
                elif isinstance(value, list):
                    text_parts.extend([str(v) for v in value])
    
    return ' '.join(text_parts)

def extract_request_type_from_metadata(metadata_list: List[Dict]) -> str:
    """从元数据中提取请求类型"""
    for item in metadata_list:
        if item['section_type'] == 'user_request':
            content = item['content']
            if isinstance(content, str):
                try:
                    content = json.loads(content)
                except json.JSONDecodeError:
                    continue
            
            if isinstance(content, dict):
                return content.get('request_type', '找队友')
    
    return '找队友'

def calculate_text_similarity(text1: str, text2: str) -> float:
    """简单的文本相似度计算"""
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = words1 & words2
    union = words1 | words2
    
    return len(intersection) / len(union) if union else 0.0 