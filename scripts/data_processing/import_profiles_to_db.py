#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
批量导入用户档案到数据库脚本
从 data/raw/profiles/ 文件夹读取所有JSON文件并导入到Supabase数据库
"""

import json
import os
import sys
import uuid
import random
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import re

# 添加项目根目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# 导入Supabase客户端
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    print("Warning: supabase package not available. Will only generate SQL.")
    SUPABASE_AVAILABLE = False

@dataclass
class ImportStats:
    """导入统计"""
    total_files: int = 0
    success_count: int = 0
    error_count: int = 0
    errors: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []

class ProfileImporter:
    """用户档案导入器"""
    
    def __init__(self, supabase_url: str = None, supabase_key: str = None):
        self.supabase = None
        if SUPABASE_AVAILABLE and supabase_url and supabase_key:
            self.supabase = create_client(supabase_url, supabase_key)
        
        # 模拟数据生成器
        self.fake_emails = [
            "example{}@gmail.com", "test{}@outlook.com", "user{}@qq.com",
            "demo{}@163.com", "sample{}@sina.com"
        ]
        
        self.fake_phones = [
            "138{}8888", "139{}9999", "150{}0000", "188{}1111", "199{}2222"
        ]
        
        self.stats = ImportStats()
    
    def generate_fake_data(self, user_id: str) -> Dict[str, Any]:
        """为缺失字段生成模拟数据"""
        # 从user_id提取数字用于生成一致的假数据
        user_num = re.findall(r'\d+', user_id)
        seed = int(user_num[0]) if user_num else random.randint(1, 1000)
        
        # 使用种子确保同一用户生成相同的假数据
        random.seed(seed)
        
        return {
            "email": self.fake_emails[seed % len(self.fake_emails)].format(seed),
            "phone": self.fake_phones[seed % len(self.fake_phones)].format(str(seed).zfill(4)[:4]),
            "auth_user_id": str(uuid.uuid4()),
            "avatar_url": f"https://api.dicebear.com/7.x/avataaars/svg?seed={user_id}"
        }
    
    def extract_user_profile_data(self, user_id: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """从JSON档案提取user_profile表需要的数据"""
        name_data = profile_data.get("profile", {}).get("name", {})
        
        # 生成假数据
        fake_data = self.generate_fake_data(user_id)
        
        return {
            "user_id": user_id,
            "display_name": name_data.get("display_name", user_id),
            "nickname": name_data.get("nickname", user_id.split("_")[-1]),
            "email": fake_data["email"],
            "phone": fake_data["phone"],
            "auth_user_id": None,  # 设为NULL，之后可以关联到真实认证用户
            "avatar_url": fake_data["avatar_url"],
            "status": "active",
            "profile_version": 1
        }
    
    def extract_metadata_entries(self, user_id: str, profile_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """从JSON档案提取user_metadata表需要的数据"""
        entries = []
        profile_section = profile_data.get("profile", {})
        
        # 处理不同的section_type
        sections_mapping = {
            "name": ("profile", "name", "nested_object"),
            "professional": ("profile", "professional", "nested_object"),
            "personal": ("profile", "personal", "nested_object"),
            "personality": ("profile", "personality", "nested_object"),
            "education": ("profile", "education", "nested_object"),
            "projects": ("profile", "projects", "nested_object"),
            "career_journey": ("profile", "career_journey", "nested_object"),
            "expertise_areas": ("profile", "expertise_areas", "nested_object"),
            "lifestyle": ("profile", "lifestyle", "nested_object"),
        }
        
        # 处理基础sections
        for section_key, (section_type, db_section_key, data_type) in sections_mapping.items():
            if section_key in profile_section:
                entries.append({
                    "user_id": user_id,
                    "section_type": section_type,
                    "section_key": db_section_key,
                    "data_type": data_type,
                    "content": json.dumps(profile_section[section_key], ensure_ascii=False),
                    "display_order": len(entries) + 1,
                    "is_active": True,
                    "metadata": "{}"
                })
        
        # 处理社交媒体
        if "social_media" in profile_section:
            social_data = profile_section["social_media"]
            for platform, platform_data in social_data.items():
                entries.append({
                    "user_id": user_id,
                    "section_type": "profile",
                    "section_key": "social_media",
                    "data_type": "social_link",
                    "content": json.dumps({
                        "platform": platform,
                        **platform_data
                    }, ensure_ascii=False),
                    "display_order": len(entries) + 1,
                    "is_active": True,
                    "metadata": json.dumps({"platform": platform}, ensure_ascii=False)
                })
        
        # 处理内容发布
        if "content" in profile_section:
            content_data = profile_section["content"]
            if "posts" in content_data:
                for i, post in enumerate(content_data["posts"]):
                    entries.append({
                        "user_id": user_id,
                        "section_type": "profile", 
                        "section_key": "content",
                        "data_type": "content_post",
                        "content": json.dumps(post, ensure_ascii=False),
                        "display_order": i + 1,
                        "is_active": True,
                        "metadata": json.dumps({"platform": post.get("platform", "unknown")}, ensure_ascii=False)
                    })
        
        # 处理QA问答
        if "qa_responses" in profile_section:
            for i, qa in enumerate(profile_section["qa_responses"]):
                entries.append({
                    "user_id": user_id,
                    "section_type": "profile",
                    "section_key": "qa_responses", 
                    "data_type": "qa_pair",
                    "content": json.dumps(qa, ensure_ascii=False),
                    "display_order": i + 1,
                    "is_active": True,
                    "metadata": "{}"
                })
        
        # 处理联系偏好
        if "contact_preferences" in profile_section:
            entries.append({
                "user_id": user_id,
                "section_type": "profile",
                "section_key": "contact_preferences",
                "data_type": "nested_object",
                "content": json.dumps(profile_section["contact_preferences"], ensure_ascii=False),
                "display_order": len(entries) + 1,
                "is_active": True,
                "metadata": "{}"
            })
        
        # 处理用户请求
        if "user_request" in profile_data:
            entries.append({
                "user_id": user_id,
                "section_type": "user_request",
                "section_key": "main_request", 
                "data_type": "nested_object",
                "content": json.dumps(profile_data["user_request"], ensure_ascii=False),
                "display_order": 1,
                "is_active": True,
                "metadata": json.dumps({"request_type": profile_data["user_request"].get("request_type", "未知")}, ensure_ascii=False)
            })
        
        # 处理元数据
        if "metadata" in profile_data:
            entries.append({
                "user_id": user_id,
                "section_type": "metadata",
                "section_key": "profile_metadata",
                "data_type": "nested_object", 
                "content": json.dumps(profile_data["metadata"], ensure_ascii=False),
                "display_order": 1,
                "is_active": True,
                "metadata": "{}"
            })
        
        return entries
    
    def load_profile_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """加载单个档案文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.stats.errors.append(f"Failed to load {file_path}: {str(e)}")
            return None
    
    def insert_user_profile(self, profile_data: Dict[str, Any]) -> bool:
        """插入用户基本信息"""
        try:
            if self.supabase:
                print(f"  - 插入用户档案: {profile_data.get('user_id')}")
                result = self.supabase.table("user_profile").insert(profile_data).execute()
                print(f"  - 插入成功，响应: {len(result.data) if result.data else 0} 条记录")
                return True
            else:
                # 生成SQL
                columns = ", ".join(profile_data.keys())
                values = ", ".join([f"'{v}'" if isinstance(v, str) else str(v) for v in profile_data.values()])
                print(f"INSERT INTO user_profile ({columns}) VALUES ({values});")
                return True
        except Exception as e:
            error_msg = f"Failed to insert user_profile for {profile_data.get('user_id')}: {str(e)}"
            print(f"  ❌ {error_msg}")
            self.stats.errors.append(error_msg)
            return False
    
    def insert_user_metadata(self, metadata_entries: List[Dict[str, Any]]) -> bool:
        """插入用户元数据"""
        try:
            if self.supabase:
                if metadata_entries:
                    print(f"  - 插入元数据: {len(metadata_entries)} 条记录")
                    result = self.supabase.table("user_metadata").insert(metadata_entries).execute()
                    print(f"  - 元数据插入成功，响应: {len(result.data) if result.data else 0} 条记录")
                return True
            else:
                # 生成SQL
                for entry in metadata_entries:
                    columns = ", ".join(entry.keys())
                    values = ", ".join([f"'{v}'" if isinstance(v, str) else str(v) for v in entry.values()])
                    print(f"INSERT INTO user_metadata ({columns}) VALUES ({values});")
                return True
        except Exception as e:
            user_id = metadata_entries[0].get('user_id', 'unknown') if metadata_entries else 'unknown'
            error_msg = f"Failed to insert user_metadata for {user_id}: {str(e)}"
            print(f"  ❌ {error_msg}")
            self.stats.errors.append(error_msg)
            return False
    
    def import_single_profile(self, file_path: str) -> bool:
        """导入单个用户档案"""
        # 从文件名提取user_id
        filename = os.path.basename(file_path)
        user_id = filename.replace('.json', '')
        
        print(f"正在处理: {user_id}")
        
        # 加载文件
        profile_data = self.load_profile_file(file_path)
        if not profile_data:
            return False
        
        # 提取数据
        user_profile_data = self.extract_user_profile_data(user_id, profile_data)
        metadata_entries = self.extract_metadata_entries(user_id, profile_data)
        
        # 插入数据库
        profile_success = self.insert_user_profile(user_profile_data)
        metadata_success = self.insert_user_metadata(metadata_entries)
        
        if profile_success and metadata_success:
            print(f"✅ 成功导入: {user_id} (档案 + {len(metadata_entries)}条元数据)")
            return True
        else:
            print(f"❌ 导入失败: {user_id}")
            return False
    
    def import_all_profiles(self, profiles_dir: str = "data/raw/profiles") -> ImportStats:
        """批量导入所有用户档案"""
        print(f"开始批量导入用户档案...")
        print(f"目录: {profiles_dir}")
        
        if not os.path.exists(profiles_dir):
            self.stats.errors.append(f"目录不存在: {profiles_dir}")
            return self.stats
        
        # 获取所有JSON文件
        json_files = [f for f in os.listdir(profiles_dir) if f.endswith('.json')]
        self.stats.total_files = len(json_files)
        
        print(f"找到 {self.stats.total_files} 个JSON文件")
        
        # 逐个处理文件
        for filename in sorted(json_files):
            file_path = os.path.join(profiles_dir, filename)
            
            try:
                if self.import_single_profile(file_path):
                    self.stats.success_count += 1
                else:
                    self.stats.error_count += 1
            except Exception as e:
                self.stats.error_count += 1
                self.stats.errors.append(f"Unexpected error processing {filename}: {str(e)}")
        
        # 打印统计结果
        print(f"\n📊 导入完成!")
        print(f"总文件数: {self.stats.total_files}")
        print(f"成功: {self.stats.success_count}")
        print(f"失败: {self.stats.error_count}")
        
        if self.stats.errors:
            print(f"\n❌ 错误详情:")
            for error in self.stats.errors:
                print(f"  - {error}")
        
        return self.stats

def main():
    """主函数"""
    # 从环境变量获取Supabase配置
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")
    
    if not supabase_url or not supabase_key:
        print("Warning: SUPABASE_URL 或 SUPABASE_ANON_KEY 环境变量未设置")
        print("将以SQL生成模式运行...")
    
    # 创建导入器
    importer = ProfileImporter(supabase_url, supabase_key)
    
    # 执行导入
    stats = importer.import_all_profiles()
    
    # 返回状态码
    return 0 if stats.error_count == 0 else 1

if __name__ == "__main__":
    exit(main()) 