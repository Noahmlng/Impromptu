#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
认证服务模块
包含用户注册、登录、token验证等功能
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Optional, Dict
import jwt
import datetime
import os
import sys
import bcrypt
import uuid

# 添加项目根目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.services.database_service import get_supabase

router = APIRouter()

# Pydantic模型
class RegisterRequest(BaseModel):
    email: str
    password: str
    display_name: str
    avatar_url: Optional[str] = None

class LoginRequest(BaseModel):
    email: str
    password: str

class AuthResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict] = None

# JWT密钥（在生产环境中应该使用环境变量）
JWT_SECRET = os.getenv('JWT_SECRET', 'your-secret-key-here')

def hash_password(password: str) -> str:
    """加密密码"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password: str, hashed_password: str) -> bool:
    """验证密码"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(user_data: Dict) -> str:
    """生成JWT访问令牌"""
    payload = {
        'sub': user_data['id'],  # user_profile.id
        'email': user_data['email'],
        'user_metadata': {
            'display_name': user_data.get('display_name'),
            'avatar_url': user_data.get('avatar_url')
        },
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7),
        'iat': datetime.datetime.utcnow(),
        'iss': 'impromptu-app'
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')

async def get_current_user(authorization: Optional[str] = Header(None)):
    """获取当前用户的依赖函数"""
    if not authorization:
        raise HTTPException(status_code=401, detail="未提供认证token")
    
    try:
        # 获取数据库服务实例
        supabase = get_supabase()
        
        # 移除 'Bearer ' 前缀
        if authorization.startswith('Bearer '):
            token = authorization[7:]
        else:
            token = authorization
        
        # 解码JWT token（使用我们自己的密钥）
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        user_id = decoded_token.get('sub')  # user_profile.id
        user_email = decoded_token.get('email')
        
        if not user_id:
            raise HTTPException(status_code=401, detail="无效的认证token")
        
        # 获取用户档案信息（只读取，不更新last_login_at）
        user_profile = supabase.table('user_profile').select('*').eq('id', user_id).execute()
        
        if not user_profile.data or len(user_profile.data) == 0:
            raise HTTPException(status_code=401, detail="用户不存在")
        
        user_data = user_profile.data[0]
        
        # 检查用户是否活跃
        if not user_data.get('is_active', True):
            raise HTTPException(status_code=401, detail="账户已被禁用")
        
        # 移除了更新last_login_at的操作，提高验证速度
        # 只在实际登录时更新last_login_at，而不是每次token验证时都更新
        
        return {
            'user_id': user_data['id'],
            'email': user_data['email'],
            'profile': user_data
        }
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token已过期")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="无效的token")
    except Exception as e:
        print(f"认证错误: {e}")
        raise HTTPException(status_code=401, detail="认证失败")

@router.post("/register", response_model=AuthResponse)
async def register(request: RegisterRequest):
    """用户注册"""
    try:
        # 获取数据库服务实例
        supabase = get_supabase()
        
        # 检查邮箱是否已存在
        existing_user = supabase.table('user_profile').select('*').eq('email', request.email.lower().strip()).execute()
        if existing_user.data and len(existing_user.data) > 0:
            raise HTTPException(status_code=400, detail="该邮箱已被注册")
        
        # 加密密码
        hashed_password = hash_password(request.password)
        
        # 创建用户档案数据 - 只包含必需字段
        profile_data = {
            'email': request.email.lower().strip(),
            'password': hashed_password,
            'display_name': request.display_name.strip(),
            'is_active': True,
            'subscription_type': 'free'
        }
        
        # 添加可选字段
        if request.avatar_url:
            profile_data['avatar_url'] = request.avatar_url
        
        # 在user_profile表中创建用户
        user_profile = supabase.table('user_profile').insert(profile_data).execute()
        
        if not user_profile.data or len(user_profile.data) == 0:
            raise HTTPException(status_code=500, detail="用户创建失败")
        
        created_user = user_profile.data[0]
        
        # 生成JWT token
        access_token = create_access_token(created_user)
        
        return AuthResponse(
            success=True,
            message="注册成功",
            data={
                "user_id": created_user['id'],
                "email": created_user['email'],
                "display_name": created_user['display_name'],
                "avatar_url": created_user.get('avatar_url'),
                "subscription_type": created_user.get('subscription_type', 'free'),
                "created_at": created_user['created_at'],
                "updated_at": created_user['updated_at'],
                "last_login_at": created_user.get('last_login_at'),
                "is_active": created_user.get('is_active', True),
                "token": access_token
            }
        )
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"注册错误: {e}")
        raise HTTPException(status_code=500, detail=f"注册失败: {str(e)}")

@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """用户登录"""
    try:
        # 获取数据库服务实例
        supabase = get_supabase()
        
        # 根据邮箱查找用户
        user_profile = supabase.table('user_profile').select('*').eq('email', request.email.lower().strip()).execute()
        if not user_profile.data or len(user_profile.data) == 0:
            raise HTTPException(status_code=401, detail="邮箱或密码错误")
        
        user_data = user_profile.data[0]
        
        # 验证密码
        if not verify_password(request.password, user_data['password']):
            raise HTTPException(status_code=401, detail="邮箱或密码错误")
        
        # 检查用户是否活跃
        if not user_data.get('is_active', True):
            raise HTTPException(status_code=401, detail="账户已被禁用")
        
        # 更新最后登录时间
        supabase.table('user_profile').update({
            'last_login_at': datetime.datetime.utcnow().isoformat()
        }).eq('id', user_data['id']).execute()
        
        # 生成JWT token
        access_token = create_access_token(user_data)
        
        return AuthResponse(
            success=True,
            message="登录成功",
            data={
                "user_id": user_data['id'],
                "email": user_data['email'],
                "display_name": user_data['display_name'],
                "avatar_url": user_data.get('avatar_url'),
                "subscription_type": user_data.get('subscription_type', 'free'),
                "created_at": user_data['created_at'],
                "updated_at": user_data['updated_at'],
                "last_login_at": user_data.get('last_login_at'),
                "is_active": user_data.get('is_active', True),
                "token": access_token
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"登录错误: {e}")
        raise HTTPException(status_code=500, detail=f"登录失败: {str(e)}")

@router.post("/logout", response_model=AuthResponse)
async def logout():
    """用户登出"""
    try:
        # 由于我们使用JWT token，登出主要是客户端删除token
        # 服务端可以记录登出事件，但token本身会在过期时间后自动失效
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

@router.get("/verify-fast")
async def verify_token_fast(authorization: Optional[str] = Header(None)):
    """快速验证token有效性 - 只检查token，不返回用户数据"""
    if not authorization:
        raise HTTPException(status_code=401, detail="未提供认证token")
    
    try:
        # 移除 'Bearer ' 前缀
        if authorization.startswith('Bearer '):
            token = authorization[7:]
        else:
            token = authorization
        
        # 只解码JWT token验证其有效性，不查询数据库
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        user_id = decoded_token.get('sub')
        user_email = decoded_token.get('email')
        
        if not user_id or not user_email:
            raise HTTPException(status_code=401, detail="无效的认证token")
        
        return {
            "valid": True,
            "user_id": user_id,
            "email": user_email
        }
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token已过期")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="无效的token")
    except Exception as e:
        print(f"快速认证验证错误: {e}")
        raise HTTPException(status_code=401, detail="认证失败")

@router.get("/verify")
async def verify_token(current_user: Dict = Depends(get_current_user)):
    """验证token有效性"""
    return {
        "valid": True,
        "user_id": current_user['user_id'],
        "email": current_user['email']
    } 