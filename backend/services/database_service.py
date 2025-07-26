#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据库服务模块
统一管理Supabase连接和基础数据库操作
"""

import os
from typing import Optional, Dict, List, Any
from supabase import create_client, Client
import json
import datetime

# 加载环境变量
try:
    from dotenv import load_dotenv
    import os
    
    # 尝试从多个位置加载.env.local文件
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(current_dir, '..', '..')
    
    # 优先加载项目根目录的.env.local
    load_dotenv(os.path.join(project_root, '.env.local'))
    load_dotenv(os.path.join(current_dir, '..', '.env.local'))  # backend目录
    load_dotenv('.env.local')  # 当前目录
    load_dotenv()  # 默认.env文件
    
    print(f"环境变量加载状态:")
    print(f"SUPABASE_SERVICE_ROLE_KEY: {'已设置' if os.getenv('SUPABASE_SERVICE_ROLE_KEY') else '未设置'}")
except ImportError:
    pass  # 如果没有安装python-dotenv，继续使用系统环境变量

# Supabase配置
SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://anxbbsrnjgmotxzysqwf.supabase.co')
# 使用service role key来绕过RLS策略
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
SUPABASE_KEY = os.getenv('SUPABASE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFueGJic3Juamdtb3R4enlzcXdmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTA0MDY0OTIsImV4cCI6MjA2NTk4MjQ5Mn0.a0t-pgH-Z2Fbs6JuMNWX8_kpqkQsBag3-COAUZVF6-0')

# 全局Supabase客户端
supabase: Optional[Client] = None

async def init_database():
    """初始化数据库连接"""
    global supabase
    try:
        # 使用service role key来绕过RLS策略，允许后端直接操作数据库
        if SUPABASE_SERVICE_KEY:
            supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
            print("✅ 使用Service Role Key连接数据库")
        else:
            supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
            print("⚠️ 使用Anon Key连接数据库（建议使用Service Role Key）")
        print("✅ Supabase数据库连接初始化成功")
    except Exception as e:
        print(f"❌ 数据库连接初始化失败: {e}")
        raise e

async def close_database():
    """关闭数据库连接"""
    # Supabase客户端无需显式关闭
    print("✅ 数据库连接已关闭")

def get_supabase() -> Client:
    """获取Supabase客户端实例"""
    if supabase is None:
        raise Exception("数据库未初始化，请先调用 init_database()")
    return supabase

class DatabaseService:
    """数据库服务基类"""
    
    def __init__(self):
        self.client = get_supabase()
    
    async def test_connection(self) -> Dict[str, Any]:
        """测试数据库连接"""
        try:
            # 测试基本查询
            profiles_response = self.client.table('user_profile').select('id', count='exact').execute()
            metadata_response = self.client.table('user_metadata').select('id', count='exact').execute()
            tags_response = self.client.table('user_tags').select('id', count='exact').execute()
            
            return {
                "success": True,
                "message": "数据库连接正常",
                "stats": {
                    "profiles_count": len(profiles_response.data) if profiles_response.data else 0,
                    "metadata_count": len(metadata_response.data) if metadata_response.data else 0,
                    "tags_count": len(tags_response.data) if tags_response.data else 0
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": "数据库连接失败",
                "message": str(e)
            }

class UserProfileDB:
    """用户档案数据库操作"""
    
    def __init__(self):
        self.client = get_supabase()
        self.table = 'user_profile'
    
    async def get_by_auth_id(self, auth_user_id: str) -> Optional[Dict]:
        """根据认证用户ID获取用户档案"""
        try:
            response = self.client.table(self.table).select('*').eq('auth_user_id', auth_user_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"获取用户档案失败: {e}")
            return None
    
    async def get_by_id(self, user_id: str) -> Optional[Dict]:
        """根据用户ID获取用户档案"""
        try:
            response = self.client.table(self.table).select('*').eq('id', user_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"获取用户档案失败: {e}")
            return None
    
    async def get_by_email(self, email: str) -> Optional[Dict]:
        """根据邮箱获取用户档案"""
        try:
            response = self.client.table(self.table).select('*').eq('email', email.lower().strip()).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"根据邮箱获取用户档案失败: {e}")
            return None
    
    async def create(self, profile_data: Dict) -> Optional[Dict]:
        """创建用户档案"""
        try:
            profile_data['created_at'] = datetime.datetime.utcnow().isoformat()
            profile_data['updated_at'] = datetime.datetime.utcnow().isoformat()
            
            response = self.client.table(self.table).insert(profile_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"创建用户档案失败: {e}")
            return None
    
    async def update(self, user_id: str, update_data: Dict) -> Optional[Dict]:
        """更新用户档案"""
        try:
            update_data['updated_at'] = datetime.datetime.utcnow().isoformat()
            
            response = self.client.table(self.table).update(update_data).eq('id', user_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"更新用户档案失败: {e}")
            return None
    
    async def get_all(self, exclude_user_id: Optional[str] = None) -> List[Dict]:
        """获取所有用户档案"""
        try:
            query = self.client.table(self.table).select('*')
            if exclude_user_id:
                query = query.neq('id', exclude_user_id)
            
            response = query.execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"获取所有用户档案失败: {e}")
            return []

class UserMetadataDB:
    """用户元数据数据库操作"""
    
    def __init__(self):
        self.client = get_supabase()
        self.table = 'user_metadata'
    
    async def get_by_user_id(self, user_id: str) -> List[Dict]:
        """获取用户的所有元数据"""
        try:
            response = self.client.table(self.table).select('*').eq('user_id', user_id).execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"获取用户元数据失败: {e}")
            return []
    
    async def upsert_metadata(self, user_id: str, section_type: str, section_key: str, content: Any) -> Optional[Dict]:
        """插入或更新元数据"""
        try:
            # 检查是否已存在
            existing = self.client.table(self.table).select('id').eq('user_id', user_id).eq('section_type', section_type).eq('section_key', section_key).execute()
            
            metadata_entry = {
                'user_id': user_id,
                'section_type': section_type,
                'section_key': section_key,
                'content': json.dumps(content, ensure_ascii=False) if isinstance(content, (dict, list)) else content,
                'updated_at': datetime.datetime.utcnow().isoformat()
            }
            
            if existing.data:
                # 更新
                response = self.client.table(self.table).update(metadata_entry).eq('id', existing.data[0]['id']).execute()
            else:
                # 插入
                metadata_entry['created_at'] = datetime.datetime.utcnow().isoformat()
                response = self.client.table(self.table).insert(metadata_entry).execute()
            
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"插入/更新元数据失败: {e}")
            return None

class UserTagsDB:
    """用户标签数据库操作"""
    
    def __init__(self):
        self.client = get_supabase()
        self.table = 'user_tags'
    
    async def get_by_user_id(self, user_id: str) -> List[Dict]:
        """获取用户的所有标签"""
        try:
            response = self.client.table(self.table).select('*').eq('user_id', user_id).order('confidence_score', desc=True).execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"获取用户标签失败: {e}")
            return []
    
    async def add_tag(self, user_id: str, tag_name: str, tag_category: str = 'manual', 
                     confidence_score: float = 1.0, tag_source: str = 'manual') -> Optional[Dict]:
        """添加用户标签"""
        try:
            # 删除旧的同名标签
            self.client.table(self.table).delete().eq('user_id', user_id).eq('tag_name', tag_name).execute()
            
            tag_entry = {
                'user_id': user_id,
                'tag_name': tag_name,
                'tag_category': tag_category,
                'confidence_score': confidence_score,
                'tag_source': tag_source,
                'created_at': datetime.datetime.utcnow().isoformat()
            }
            
            response = self.client.table(self.table).insert(tag_entry).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"添加用户标签失败: {e}")
            return None
    
    async def remove_tag(self, user_id: str, tag_name: str) -> bool:
        """删除用户标签"""
        try:
            self.client.table(self.table).delete().eq('user_id', user_id).eq('tag_name', tag_name).execute()
            return True
        except Exception as e:
            print(f"删除用户标签失败: {e}")
            return False
    
    async def batch_add_tags(self, user_id: str, tags: List[Dict]) -> List[Dict]:
        """批量添加用户标签"""
        saved_tags = []
        for tag_info in tags:
            tag_name = tag_info.get('name') or tag_info.get('tag_name')
            if not tag_name:
                continue
            
            tag_category = tag_info.get('category', 'manual')
            confidence_score = float(tag_info.get('confidence', 1.0))
            tag_source = tag_info.get('source', 'manual')
            
            result = await self.add_tag(user_id, tag_name, tag_category, confidence_score, tag_source)
            if result:
                saved_tags.append(result)
        
        return saved_tags

# 数据库服务实例 - 延迟初始化
db_service = None
user_profile_db = None
user_metadata_db = None
user_tags_db = None

def get_database_services():
    """获取数据库服务实例，如果不存在则创建"""
    global db_service, user_profile_db, user_metadata_db, user_tags_db
    
    if db_service is None:
        db_service = DatabaseService()
        user_profile_db = UserProfileDB()
        user_metadata_db = UserMetadataDB()
        user_tags_db = UserTagsDB()
    
    return db_service, user_profile_db, user_metadata_db, user_tags_db 