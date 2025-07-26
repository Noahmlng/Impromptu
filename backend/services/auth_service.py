#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
认证服务模块
包含用户注册、登录、token验证等功能
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict
import jwt
import datetime
import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.services.database_service import get_supabase, user_profile_db

router = APIRouter()

# Pydantic模型
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    display_name: str
    avatar_url: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class AuthResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict] = None

# JWT密钥（在生产环境中应该使用环境变量）
JWT_SECRET = os.getenv('JWT_SECRET', 'your-secret-key-here')

async def get_current_user(authorization: Optional[str] = Header(None)):
    """获取当前用户的依赖函数"""
    if not authorization:
        raise HTTPException(status_code=401, detail="未提供认证token")
    
    try:
        # 移除 'Bearer ' 前缀
        if authorization.startswith('Bearer '):
            token = authorization[7:]
        else:
            token = authorization
        
        # 解码JWT token
        decoded_token = jwt.decode(token, options={"verify_signature": False})
        auth_user_id = decoded_token.get('sub')
        user_email = decoded_token.get('email')
        
        if not auth_user_id:
            raise HTTPException(status_code=401, detail="无效的认证token")
        
        # 获取用户档案信息
        user_profile = await user_profile_db.get_by_auth_id(auth_user_id)
        
        if not user_profile:
            # 自动创建用户档案
            display_name = decoded_token.get('user_metadata', {}).get('display_name') or user_email.split('@')[0]
            avatar_url = decoded_token.get('user_metadata', {}).get('avatar_url')
            
            profile_data = {
                'auth_user_id': auth_user_id,
                'email': user_email,
                'display_name': display_name,
                'avatar_url': avatar_url,
                'last_login_at': datetime.datetime.utcnow().isoformat(),
                'is_active': True,
                'credits': 1000,
                'subscription_type': 'free'
            }
            
            user_profile = await user_profile_db.create(profile_data)
            if not user_profile:
                raise HTTPException(status_code=500, detail="用户档案创建失败")
        else:
            # 更新最后登录时间
            await user_profile_db.update(user_profile['id'], {
                'last_login_at': datetime.datetime.utcnow().isoformat()
            })
        
        return {
            'user_id': user_profile['id'],
            'auth_user_id': auth_user_id,
            'email': user_email,
            'profile': user_profile
        }
        
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="无效的token")
    except Exception as e:
        print(f"认证错误: {e}")
        raise HTTPException(status_code=401, detail="认证失败")

@router.post("/register", response_model=AuthResponse)
async def register(request: RegisterRequest):
    """用户注册"""
    try:
        supabase = get_supabase()
        
        # 使用Supabase Auth注册用户
        auth_response = supabase.auth.sign_up({
            "email": request.email.lower().strip(),
            "password": request.password,
            "options": {
                "data": {
                    "display_name": request.display_name.strip(),
                    "avatar_url": request.avatar_url
                }
            }
        })
        
        if auth_response.user:
            return AuthResponse(
                success=True,
                message="注册成功",
                data={
                    "user_id": auth_response.user.id,
                    "email": auth_response.user.email,
                    "display_name": request.display_name,
                    "token": auth_response.session.access_token if auth_response.session else None,
                    "needs_confirmation": not auth_response.user.email_confirmed_at
                }
            )
        else:
            raise HTTPException(status_code=400, detail="注册失败，Supabase响应异常")
            
    except Exception as e:
        print(f"注册错误: {e}")
        error_message = str(e)
        if hasattr(e, 'message'):
            error_message = e.message
        elif hasattr(e, 'args') and e.args:
            error_message = str(e.args[0])
        
        raise HTTPException(status_code=500, detail=f"注册失败: {error_message}")

@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """用户登录"""
    try:
        supabase = get_supabase()
        
        # 使用Supabase Auth登录
        auth_response = supabase.auth.sign_in_with_password({
            "email": request.email.lower().strip(),
            "password": request.password
        })
        
        if auth_response.user and auth_response.session:
            # 获取用户档案信息
            user_profile = await user_profile_db.get_by_auth_id(auth_response.user.id)
            
            return AuthResponse(
                success=True,
                message="登录成功",
                data={
                    "user_id": user_profile['id'] if user_profile else auth_response.user.id,
                    "email": auth_response.user.email,
                    "display_name": user_profile['display_name'] if user_profile else auth_response.user.user_metadata.get('display_name'),
                    "avatar_url": user_profile['avatar_url'] if user_profile else auth_response.user.user_metadata.get('avatar_url'),
                    "token": auth_response.session.access_token
                }
            )
        else:
            raise HTTPException(status_code=401, detail="登录失败，请检查邮箱和密码")
        
    except Exception as e:
        print(f"登录错误: {e}")
        error_message = str(e)
        if hasattr(e, 'message'):
            error_message = e.message
        elif hasattr(e, 'args') and e.args:
            error_message = str(e.args[0])
        
        raise HTTPException(status_code=500, detail=f"登录失败: {error_message}")

@router.post("/logout", response_model=AuthResponse)
async def logout():
    """用户登出"""
    try:
        supabase = get_supabase()
        supabase.auth.sign_out()
        
        return AuthResponse(
            success=True,
            message="登出成功"
        )
    except Exception as e:
        print(f"登出错误: {e}")
        raise HTTPException(status_code=500, detail=f"登出失败: {str(e)}")

@router.get("/user", response_model=AuthResponse)
async def get_current_user_info(current_user: Dict = Depends(get_current_user)):
    """获取当前用户信息"""
    try:
        return AuthResponse(
            success=True,
            message="获取用户信息成功",
            data={
                "user_id": current_user['user_id'],
                "email": current_user['email'],
                "display_name": current_user['profile']['display_name'],
                "avatar_url": current_user['profile'].get('avatar_url'),
                "created_at": current_user['profile']['created_at'],
                "updated_at": current_user['profile']['updated_at'],
                "is_active": current_user['profile'].get('is_active', True),
                "credits": current_user['profile'].get('credits', 0),
                "subscription_type": current_user['profile'].get('subscription_type', 'free')
            }
        )
    except Exception as e:
        print(f"获取用户信息错误: {e}")
        raise HTTPException(status_code=500, detail=f"获取用户信息失败: {str(e)}")

@router.get("/verify")
async def verify_token(current_user: Dict = Depends(get_current_user)):
    """验证token有效性"""
    return {
        "valid": True,
        "user_id": current_user['user_id'],
        "email": current_user['email']
    } 