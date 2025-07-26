#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
元数据服务模块
包含用户档案元数据的CRUD操作
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, List, Any
import json
import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.services.database_service import user_metadata_db
from backend.services.auth_service import get_current_user

router = APIRouter()

# Pydantic模型
class MetadataRequest(BaseModel):
    section_type: str  # 如: 'profile', 'user_request'
    section_key: str   # 如: 'personal', 'professional'
    content: Any       # metadata内容
    data_type: Optional[str] = 'nested_object'
    display_order: Optional[int] = 1
    metadata: Optional[Dict] = {}

class BatchMetadataRequest(BaseModel):
    metadata_entries: List[MetadataRequest]

class MetadataResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    data: Optional[Any] = None

@router.post("/", response_model=MetadataResponse)
async def create_or_update_metadata(
    request: MetadataRequest,
    current_user: Dict = Depends(get_current_user)
):
    """创建或更新单个元数据"""
    try:
        user_id = current_user['user_id']
        
        result = await user_metadata_db.upsert_metadata(
            user_id=user_id,
            section_type=request.section_type,
            section_key=request.section_key,
            content=request.content
        )
        
        if result:
            return MetadataResponse(
                success=True,
                message="元数据保存成功",
                data=result
            )
        else:
            raise HTTPException(status_code=500, detail="元数据保存失败")
            
    except Exception as e:
        print(f"元数据操作错误: {e}")
        raise HTTPException(status_code=500, detail=f"元数据操作失败: {str(e)}")

@router.post("/batch", response_model=MetadataResponse)
async def batch_update_metadata(
    request: BatchMetadataRequest,
    current_user: Dict = Depends(get_current_user)
):
    """批量创建或更新元数据"""
    try:
        user_id = current_user['user_id']
        results = []
        errors = []
        
        for entry in request.metadata_entries:
            try:
                result = await user_metadata_db.upsert_metadata(
                    user_id=user_id,
                    section_type=entry.section_type,
                    section_key=entry.section_key,
                    content=entry.content
                )
                
                if result:
                    results.append(result)
                else:
                    errors.append(f"保存失败: {entry.section_type}.{entry.section_key}")
                    
            except Exception as e:
                errors.append(f"处理条目失败: {entry.section_type}.{entry.section_key} - {str(e)}")
        
        return MetadataResponse(
            success=len(results) > 0,
            message=f"成功处理{len(results)}条记录" + (f"，{len(errors)}条失败" if errors else ""),
            data={
                "success_count": len(results),
                "error_count": len(errors),
                "results": results,
                "errors": errors
            }
        )
        
    except Exception as e:
        print(f"批量更新元数据错误: {e}")
        raise HTTPException(status_code=500, detail=f"批量更新元数据失败: {str(e)}")

@router.get("/", response_model=MetadataResponse)
async def get_user_metadata(current_user: Dict = Depends(get_current_user)):
    """获取当前用户的所有元数据"""
    try:
        user_id = current_user['user_id']
        metadata_list = await user_metadata_db.get_by_user_id(user_id)
        
        # 按section_type和section_key组织数据
        organized_metadata = {}
        for item in metadata_list:
            section_type = item['section_type']
            section_key = item['section_key']
            
            if section_type not in organized_metadata:
                organized_metadata[section_type] = {}
            
            # 解析content
            content = item['content']
            if isinstance(content, str):
                try:
                    content = json.loads(content)
                except json.JSONDecodeError:
                    pass
            
            organized_metadata[section_type][section_key] = {
                'content': content,
                'data_type': item['data_type'],
                'display_order': item['display_order'],
                'created_at': item['created_at'],
                'updated_at': item['updated_at']
            }
        
        return MetadataResponse(
            success=True,
            message="获取元数据成功",
            data=organized_metadata
        )
        
    except Exception as e:
        print(f"获取元数据错误: {e}")
        raise HTTPException(status_code=500, detail=f"获取元数据失败: {str(e)}")

@router.get("/{section_type}", response_model=MetadataResponse)
async def get_metadata_by_section(
    section_type: str,
    current_user: Dict = Depends(get_current_user)
):
    """获取指定类型的元数据"""
    try:
        user_id = current_user['user_id']
        metadata_list = await user_metadata_db.get_by_user_id(user_id)
        
        # 过滤指定类型的数据
        section_metadata = {}
        for item in metadata_list:
            if item['section_type'] == section_type:
                section_key = item['section_key']
                
                # 解析content
                content = item['content']
                if isinstance(content, str):
                    try:
                        content = json.loads(content)
                    except json.JSONDecodeError:
                        pass
                
                section_metadata[section_key] = {
                    'content': content,
                    'data_type': item['data_type'],
                    'display_order': item['display_order'],
                    'created_at': item['created_at'],
                    'updated_at': item['updated_at']
                }
        
        return MetadataResponse(
            success=True,
            message=f"获取{section_type}类型元数据成功",
            data={section_type: section_metadata}
        )
        
    except Exception as e:
        print(f"获取指定类型元数据错误: {e}")
        raise HTTPException(status_code=500, detail=f"获取指定类型元数据失败: {str(e)}")

@router.get("/{section_type}/{section_key}", response_model=MetadataResponse)
async def get_specific_metadata(
    section_type: str,
    section_key: str,
    current_user: Dict = Depends(get_current_user)
):
    """获取特定的元数据项"""
    try:
        user_id = current_user['user_id']
        metadata_list = await user_metadata_db.get_by_user_id(user_id)
        
        # 查找特定的元数据项
        for item in metadata_list:
            if item['section_type'] == section_type and item['section_key'] == section_key:
                # 解析content
                content = item['content']
                if isinstance(content, str):
                    try:
                        content = json.loads(content)
                    except json.JSONDecodeError:
                        pass
                
                return MetadataResponse(
                    success=True,
                    message="获取元数据项成功",
                    data={
                        'content': content,
                        'data_type': item['data_type'],
                        'display_order': item['display_order'],
                        'created_at': item['created_at'],
                        'updated_at': item['updated_at']
                    }
                )
        
        raise HTTPException(status_code=404, detail="未找到指定的元数据项")
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"获取特定元数据错误: {e}")
        raise HTTPException(status_code=500, detail=f"获取特定元数据失败: {str(e)}")

# 便捷接口：用户档案相关
@router.post("/profile/personal", response_model=MetadataResponse)
async def update_personal_info(
    personal_data: Dict,
    current_user: Dict = Depends(get_current_user)
):
    """更新个人信息"""
    try:
        user_id = current_user['user_id']
        
        result = await user_metadata_db.upsert_metadata(
            user_id=user_id,
            section_type='profile',
            section_key='personal',
            content=personal_data
        )
        
        if result:
            return MetadataResponse(
                success=True,
                message="个人信息更新成功",
                data=result
            )
        else:
            raise HTTPException(status_code=500, detail="个人信息更新失败")
            
    except Exception as e:
        print(f"更新个人信息错误: {e}")
        raise HTTPException(status_code=500, detail=f"更新个人信息失败: {str(e)}")

@router.post("/profile/professional", response_model=MetadataResponse)
async def update_professional_info(
    professional_data: Dict,
    current_user: Dict = Depends(get_current_user)
):
    """更新职业信息"""
    try:
        user_id = current_user['user_id']
        
        result = await user_metadata_db.upsert_metadata(
            user_id=user_id,
            section_type='profile',
            section_key='professional',
            content=professional_data
        )
        
        if result:
            return MetadataResponse(
                success=True,
                message="职业信息更新成功",
                data=result
            )
        else:
            raise HTTPException(status_code=500, detail="职业信息更新失败")
            
    except Exception as e:
        print(f"更新职业信息错误: {e}")
        raise HTTPException(status_code=500, detail=f"更新职业信息失败: {str(e)}")

@router.post("/profile/personality", response_model=MetadataResponse)
async def update_personality_info(
    personality_data: Dict,
    current_user: Dict = Depends(get_current_user)
):
    """更新性格信息"""
    try:
        user_id = current_user['user_id']
        
        result = await user_metadata_db.upsert_metadata(
            user_id=user_id,
            section_type='profile',
            section_key='personality',
            content=personality_data
        )
        
        if result:
            return MetadataResponse(
                success=True,
                message="性格信息更新成功",
                data=result
            )
        else:
            raise HTTPException(status_code=500, detail="性格信息更新失败")
            
    except Exception as e:
        print(f"更新性格信息错误: {e}")
        raise HTTPException(status_code=500, detail=f"更新性格信息失败: {str(e)}")

@router.post("/user_request", response_model=MetadataResponse)
async def update_user_request(
    request_data: Dict,
    current_user: Dict = Depends(get_current_user)
):
    """更新用户需求"""
    try:
        user_id = current_user['user_id']
        
        result = await user_metadata_db.upsert_metadata(
            user_id=user_id,
            section_type='user_request',
            section_key='main',
            content=request_data
        )
        
        if result:
            return MetadataResponse(
                success=True,
                message="用户需求更新成功",
                data=result
            )
        else:
            raise HTTPException(status_code=500, detail="用户需求更新失败")
            
    except Exception as e:
        print(f"更新用户需求错误: {e}")
        raise HTTPException(status_code=500, detail=f"更新用户需求失败: {str(e)}")

# 元数据模板和验证
@router.get("/templates/profile")
async def get_profile_template():
    """获取用户档案模板"""
    template = {
        "profile": {
            "personal": {
                "age_range": "25-30",
                "location": "北京",
                "education": "本科",
                "height": "170cm",
                "relationship_status": "单身"
            },
            "professional": {
                "current_role": "软件工程师",
                "company": "科技公司",
                "experience_years": 3,
                "industry": "互联网",
                "skills": ["Python", "React", "数据分析"]
            },
            "personality": {
                "mbti": "INFP",
                "traits": ["开朗", "幽默", "有责任心"],
                "hobbies": ["读书", "旅行", "摄影"],
                "values": ["诚实", "成长", "创新"]
            }
        },
        "user_request": {
            "request_type": "找对象",
            "description": "希望找到志同道合的伴侣",
            "preferences": {
                "age_range": "25-35",
                "location_preference": "同城",
                "education_preference": "本科以上"
            }
        }
    }
    
    return {
        "success": True,
        "message": "获取用户档案模板成功",
        "data": template
    }

@router.get("/validation/schema")
async def get_validation_schema():
    """获取元数据验证模式"""
    schema = {
        "required_sections": ["profile", "user_request"],
        "profile_required_keys": ["personal", "professional"],
        "validation_rules": {
            "personal": {
                "required": ["age_range", "location"],
                "optional": ["education", "height", "relationship_status"]
            },
            "professional": {
                "required": ["current_role"],
                "optional": ["company", "experience_years", "industry", "skills"]
            },
            "user_request": {
                "required": ["request_type", "description"],
                "optional": ["preferences"]
            }
        }
    }
    
    return {
        "success": True,
        "message": "获取验证模式成功",
        "data": schema
    } 