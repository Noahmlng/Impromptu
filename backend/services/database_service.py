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
    
    # 加载项目根目录的环境变量文件
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(current_dir, '..', '..')
    
    # 只从项目根目录加载环境变量文件
    load_dotenv(os.path.join(project_root, '.env.local'))
    load_dotenv(os.path.join(project_root, '.env'))
    
    print(f"环境变量加载状态:")
    print(f"SUPABASE_SERVICE_ROLE_KEY: {'已设置' if os.getenv('SUPABASE_SERVICE_ROLE_KEY') else '未设置'}")
except ImportError:
    pass  # 如果没有安装python-dotenv，继续使用系统环境变量

# Supabase配置
SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://anxbbsrnjgmotxzysqwf.supabase.co')
# 使用service role key来绕过RLS策略
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
SUPABASE_KEY = os.getenv('SUPABASE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFueGJic3Juamdtb3R4enlzcXdmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTA0MDY0OTIsImV4cCI6MjA2NTk4MjQ5Mn0.a0t-pgH-Z2Fbs6JuMNWX8_kpqkQsBag3-COAUZVF6-0')

def get_supabase() -> Client:
    """获取Supabase客户端实例 - 简化版本，无需初始化"""
    try:
        # 使用service role key来绕过RLS策略，允许后端直接操作数据库
        if SUPABASE_SERVICE_KEY:
            return create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        else:
            return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        raise e

# 为了兼容性，保留这些函数但简化实现
async def init_database():
    """保留兼容性 - 实际上Supabase客户端不需要显式初始化"""
    try:
        client = get_supabase()
        print("✅ Supabase数据库连接验证成功")
        return client
    except Exception as e:
        print(f"❌ 数据库连接验证失败: {e}")
        raise e

async def close_database():
    """保留兼容性 - Supabase客户端无需显式关闭"""
    print("✅ 数据库连接已关闭")

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
    
    async def get_all(self, exclude_user_id: Optional[str] = None, limit: Optional[int] = None) -> List[Dict]:
        """获取所有用户档案，支持限制数量以提高性能"""
        try:
            query = self.client.table(self.table).select('*')
            if exclude_user_id:
                query = query.neq('id', exclude_user_id)
            if limit:
                query = query.limit(limit)
            
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
    
    async def get_by_user_ids(self, user_ids: List[str]) -> Dict[str, List[Dict]]:
        """批量获取多个用户的元数据"""
        try:
            response = self.client.table(self.table).select('*').in_('user_id', user_ids).execute()
            data = response.data if response.data else []
            
            # 按用户ID分组
            result = {}
            for item in data:
                user_id = item['user_id']
                if user_id not in result:
                    result[user_id] = []
                result[user_id].append(item)
            
            # 确保所有用户ID都在结果中
            for user_id in user_ids:
                if user_id not in result:
                    result[user_id] = []
            
            return result
        except Exception as e:
            print(f"批量获取用户元数据失败: {e}")
            return {user_id: [] for user_id in user_ids}
    
    async def upsert_metadata(self, user_id: str, section_type: str, section_key: str, content: Any) -> Optional[Dict]:
        """插入或更新元数据"""
        try:
            print(f"📝 [UserMetadataDB] 更新元数据: {user_id} - {section_type}.{section_key}")
            
            # 验证用户是否存在
            user_profile = self.client.table('user_profile').select('id').eq('id', user_id).single().execute()
            if not user_profile.data:
                print(f"❌ [UserMetadataDB] 找不到用户档案: {user_id}")
                return None
            
            print(f"✅ [UserMetadataDB] 用户验证成功: {user_id}")
            
            # 检查是否已存在
            existing = self.client.table(self.table).select('id').eq('user_id', user_id).eq('section_type', section_type).eq('section_key', section_key).execute()
            
            # 确保content是正确的格式：JSONB字段应该直接存储对象
            if isinstance(content, str):
                try:
                    # 如果传入的是JSON字符串，尝试解析为对象
                    content = json.loads(content)
                except json.JSONDecodeError:
                    # 如果不是有效的JSON，包装成对象
                    content = {"value": content}
            elif not isinstance(content, (dict, list)):
                # 如果不是dict或list，包装成对象
                content = {"value": content}
            
            metadata_entry = {
                'user_id': user_id,
                'section_type': section_type,
                'section_key': section_key,
                'content': content,  # 直接存储对象，不转换为JSON字符串
                'data_type': 'nested_object',
                'display_order': 1,
                'updated_at': datetime.datetime.utcnow().isoformat()
            }
            
            print(f"📊 [UserMetadataDB] 元数据条目: {metadata_entry}")
            
            if existing.data:
                # 更新
                print(f"🔄 [UserMetadataDB] 更新现有元数据: {existing.data[0]['id']}")
                response = self.client.table(self.table).update(metadata_entry).eq('id', existing.data[0]['id']).execute()
            else:
                # 插入
                print(f"➕ [UserMetadataDB] 插入新元数据")
                metadata_entry['created_at'] = datetime.datetime.utcnow().isoformat()
                response = self.client.table(self.table).insert(metadata_entry).execute()
            
            if response.data:
                print(f"✅ [UserMetadataDB] 元数据操作成功")
                return response.data[0]
            else:
                print(f"❌ [UserMetadataDB] 元数据操作失败：响应为空")
                print(f"🔍 [UserMetadataDB] 响应详情: {response}")
                return None
                
        except Exception as e:
            print(f"❌ [UserMetadataDB] 插入/更新元数据失败: {e}")
            import traceback
            print(f"详细错误: {traceback.format_exc()}")
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
    
    async def get_by_user_ids(self, user_ids: List[str]) -> Dict[str, List[Dict]]:
        """批量获取多个用户的标签"""
        try:
            response = self.client.table(self.table).select('*').in_('user_id', user_ids).order('confidence_score', desc=True).execute()
            data = response.data if response.data else []
            
            # 按用户ID分组
            result = {}
            for item in data:
                user_id = item['user_id']
                if user_id not in result:
                    result[user_id] = []
                result[user_id].append(item)
            
            # 确保所有用户ID都在结果中
            for user_id in user_ids:
                if user_id not in result:
                    result[user_id] = []
            
            return result
        except Exception as e:
            print(f"批量获取用户标签失败: {e}")
            return {user_id: [] for user_id in user_ids}
    
    async def add_tag(self, user_id: str, tag_name: str, tag_category: str = 'manual', 
                     confidence_score: float = 1.0, tag_source: str = 'manual') -> Optional[Dict]:
        """添加用户标签"""
        try:
            print(f"🏷️ [UserTagsDB] 为用户 {user_id} 添加标签: {tag_name}")
            
            # 验证用户是否存在
            user_profile = self.client.table('user_profile').select('id').eq('id', user_id).single().execute()
            if not user_profile.data:
                print(f"❌ [UserTagsDB] 找不到用户档案: {user_id}")
                return None
            
            print(f"✅ [UserTagsDB] 用户验证成功: {user_id}")
            
            # 删除旧的同名标签
            print(f"🧹 [UserTagsDB] 删除旧的同名标签: {tag_name}")
            self.client.table(self.table).delete().eq('user_id', user_id).eq('tag_name', tag_name).execute()
            
            tag_entry = {
                'user_id': user_id,
                'tag_name': tag_name,
                'tag_category': tag_category,
                'confidence_score': confidence_score,
                'tag_source': tag_source,
                'created_at': datetime.datetime.utcnow().isoformat()
            }
            
            print(f"💾 [UserTagsDB] 插入标签数据: {tag_entry}")
            response = self.client.table(self.table).insert(tag_entry).execute()
            
            if response.data:
                print(f"✅ [UserTagsDB] 标签插入成功")
                return response.data[0]
            else:
                print(f"❌ [UserTagsDB] 标签插入失败：响应为空")
                print(f"🔍 [UserTagsDB] 响应详情: {response}")
                return None
                
        except Exception as e:
            print(f"❌ [UserTagsDB] 添加用户标签失败: {e}")
            import traceback
            print(f"详细错误: {traceback.format_exc()}")
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

# 创建全局实例供其他模块使用
db_service = DatabaseService()
user_profile_db = UserProfileDB()
user_metadata_db = UserMetadataDB()
user_tags_db = UserTagsDB() 