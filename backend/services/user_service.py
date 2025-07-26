#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
用户服务模块
包含用户信息查询、管理等功能
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, List
import json
import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.services.database_service import user_profile_db, user_metadata_db, user_tags_db, db_service
from backend.services.auth_service import get_current_user

router = APIRouter()

# Pydantic模型
class UserResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict] = None

class UserListResponse(BaseModel):
    success: bool
    data: List[Dict]
    total: int

@router.get("/", response_model=UserListResponse)
async def get_all_users(current_user: Dict = Depends(get_current_user)):
    """获取所有用户信息"""
    try:
        # 获取所有用户基本信息（排除当前用户）
        profiles = await user_profile_db.get_all(exclude_user_id=current_user['user_id'])
        
        users = []
        for profile in profiles:
            user_id = profile['id']
            
            # 获取用户元数据
            metadata_list = await user_metadata_db.get_by_user_id(user_id)
            
            # 获取用户标签
            user_tags = await user_tags_db.get_by_user_id(user_id)
            
            # 组织元数据
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
                
                organized_metadata[section_type][section_key] = content
            
            # 从元数据中提取信息
            personal_info = organized_metadata.get('profile', {}).get('personal', {})
            professional_info = organized_metadata.get('profile', {}).get('professional', {})
            user_request = organized_metadata.get('user_request', {})
            
            # 解析年龄
            age_range = personal_info.get('age_range', '')
            age = None
            if age_range:
                import re
                age_match = re.search(r'(\d+)', age_range)
                if age_match:
                    age = int(age_match.group(1))
            
            # 简单的性别推测
            gender = 'unknown'
            display_name = profile.get('display_name', '')
            female_names = ['sophia', 'luna', 'iris', 'jenny', 'alice', 'emma', 'lucy', 'amy', 'maya', 'mia', 'grace', 'stella', 'helena', 'crystal', 'vivian', 'coco', 'xiaoya', 'kiki']
            if any(name in display_name.lower() for name in female_names):
                gender = 'female'
            else:
                gender = 'male'
            
            # 构建用户数据
            user_data = {
                'id': user_id,
                'username': display_name or user_id,
                'display_name': display_name,
                'email': profile.get('email'),
                'age': age,
                'gender': gender,
                'location_city': personal_info.get('location', ''),
                'bio': user_request.get('description', '') or f"{professional_info.get('current_role', '用户')}",
                'occupation': professional_info.get('current_role', ''),
                'avatar_url': profile.get('avatar_url'),
                'created_at': profile.get('created_at'),
                'is_active': profile.get('is_active', True),
                'credits': profile.get('credits', 0),
                'subscription_type': profile.get('subscription_type', 'free'),
                'tags': [{'name': tag['tag_name'], 'category': tag['tag_category'], 'confidence': tag['confidence_score']} for tag in user_tags],
                'metadata': organized_metadata
            }
            users.append(user_data)
        
        return UserListResponse(
            success=True,
            data=users,
            total=len(users)
        )
        
    except Exception as e:
        print(f"获取用户列表错误: {e}")
        raise HTTPException(status_code=500, detail=f"获取用户列表失败: {str(e)}")

@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(user_id: str, current_user: Dict = Depends(get_current_user)):
    """获取指定用户信息"""
    try:
        # 获取用户基本信息
        profile = await user_profile_db.get_by_id(user_id)
        if not profile:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # 获取用户元数据
        metadata_list = await user_metadata_db.get_by_user_id(user_id)
        
        # 获取用户标签
        user_tags = await user_tags_db.get_by_user_id(user_id)
        
        # 组织元数据
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
            
            organized_metadata[section_type][section_key] = content
        
        user_data = {
            'id': profile['id'],
            'username': profile['display_name'],
            'display_name': profile['display_name'],
            'email': profile['email'],
            'avatar_url': profile.get('avatar_url'),
            'created_at': profile['created_at'],
            'updated_at': profile['updated_at'],
            'is_active': profile.get('is_active', True),
            'credits': profile.get('credits', 0),
            'subscription_type': profile.get('subscription_type', 'free'),
            'tags': [{'name': tag['tag_name'], 'category': tag['tag_category'], 'confidence': tag['confidence_score']} for tag in user_tags],
            'metadata': organized_metadata
        }
        
        return UserResponse(
            success=True,
            message="获取用户信息成功",
            data=user_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"获取用户信息错误: {e}")
        raise HTTPException(status_code=500, detail=f"获取用户信息失败: {str(e)}")

@router.get("/me/profile", response_model=UserResponse)
async def get_my_profile(current_user: Dict = Depends(get_current_user)):
    """获取当前用户的完整档案"""
    try:
        user_id = current_user['user_id']
        
        # 获取用户元数据
        metadata_list = await user_metadata_db.get_by_user_id(user_id)
        
        # 获取用户标签
        user_tags = await user_tags_db.get_by_user_id(user_id)
        
        # 组织元数据
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
        
        profile_data = {
            'basic_info': current_user['profile'],
            'metadata': organized_metadata,
            'tags': user_tags
        }
        
        return UserResponse(
            success=True,
            message="获取个人档案成功",
            data=profile_data
        )
        
    except Exception as e:
        print(f"获取个人档案错误: {e}")
        raise HTTPException(status_code=500, detail=f"获取个人档案失败: {str(e)}")

@router.get("/stats/overview")
async def get_user_stats():
    """获取用户统计概览"""
    try:
        stats = await db_service.test_connection()
        
        return {
            "success": True,
            "data": stats.get("stats", {}),
            "message": "获取统计信息成功"
        }
        
    except Exception as e:
        print(f"获取用户统计错误: {e}")
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")

@router.get("/test/database")
async def test_database_connection():
    """测试数据库连接"""
    try:
        result = await db_service.test_connection()
        
        return {
            "success": result["success"],
            "message": result["message"],
            "data": result.get("stats") or result.get("error")
        }
        
    except Exception as e:
        print(f"数据库连接测试错误: {e}")
        raise HTTPException(status_code=500, detail=f"数据库连接测试失败: {str(e)}")

# 用户搜索功能
@router.get("/search/{query}")
async def search_users(query: str, current_user: Dict = Depends(get_current_user)):
    """根据关键词搜索用户"""
    try:
        # 获取所有用户（排除当前用户）
        profiles = await user_profile_db.get_all(exclude_user_id=current_user['user_id'])
        
        # 简单的关键词匹配
        matched_users = []
        for profile in profiles:
            display_name = profile.get('display_name', '').lower()
            email = profile.get('email', '').lower()
            
            if query.lower() in display_name or query.lower() in email:
                # 获取用户标签
                user_tags = await user_tags_db.get_by_user_id(profile['id'])
                
                user_data = {
                    'id': profile['id'],
                    'display_name': profile['display_name'],
                    'email': profile['email'],
                    'avatar_url': profile.get('avatar_url'),
                    'is_active': profile.get('is_active', True),
                    'tags': [tag['tag_name'] for tag in user_tags]
                }
                matched_users.append(user_data)
        
        return {
            "success": True,
            "data": matched_users,
            "total": len(matched_users),
            "query": query
        }
        
    except Exception as e:
        print(f"用户搜索错误: {e}")
        raise HTTPException(status_code=500, detail=f"用户搜索失败: {str(e)}")

@router.put("/me/credits")
async def update_my_credits(credits_change: int, current_user: Dict = Depends(get_current_user)):
    """更新当前用户积分"""
    try:
        user_id = current_user['user_id']
        current_credits = current_user['profile'].get('credits', 0)
        new_credits = max(0, current_credits + credits_change)
        
        updated_profile = await user_profile_db.update(user_id, {'credits': new_credits})
        
        if updated_profile:
            return UserResponse(
                success=True,
                message=f"积分更新成功，当前积分: {new_credits}",
                data={
                    "old_credits": current_credits,
                    "credits_change": credits_change,
                    "new_credits": new_credits
                }
            )
        else:
            raise HTTPException(status_code=500, detail="积分更新失败")
            
    except Exception as e:
        print(f"更新积分错误: {e}")
        raise HTTPException(status_code=500, detail=f"更新积分失败: {str(e)}") 