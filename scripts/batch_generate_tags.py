#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
批量生成用户标签脚本
从数据库读取用户数据，调用标签生成算法，保存到user_tags表
"""

import json
import os
import sys
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import traceback
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# 导入Supabase客户端
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    print("Warning: supabase package not available.")
    SUPABASE_AVAILABLE = False

# 导入标签生成相关模块
from src.models.topic_modeling import topic_model
from src.algorithms.user_profile_analyzer import UserProfileAnalyzer

@dataclass
class TagGenerationResult:
    """标签生成结果"""
    user_id: str
    lda_tags: Dict[str, float]
    lda_metadata: Dict[str, Any]
    profile_analyzer_tags: Dict[str, float]
    profile_analyzer_metadata: Dict[str, Any]
    total_tags: int
    generation_time: float

@dataclass
class BatchStats:
    """批量处理统计"""
    total_users: int = 0
    processed_users: int = 0
    failed_users: int = 0
    total_tags_generated: int = 0
    errors: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []

class UserDataReader:
    """用户数据读取器"""
    
    def __init__(self, supabase: Client):
        self.supabase = supabase
    
    def get_all_users(self) -> List[str]:
        """获取所有用户ID"""
        result = self.supabase.table("user_profile").select("user_id").execute()
        return [row["user_id"] for row in result.data]
    
    def get_user_data(self, user_id: str) -> Dict[str, Any]:
        """获取单个用户的完整数据"""
        # 获取用户基本信息
        profile_result = self.supabase.table("user_profile").select("*").eq("user_id", user_id).execute()
        if not profile_result.data:
            raise ValueError(f"用户 {user_id} 不存在")
        
        user_profile = profile_result.data[0]
        
        # 获取用户元数据
        metadata_result = self.supabase.table("user_metadata").select("*").eq("user_id", user_id).execute()
        user_metadata = metadata_result.data
        
        return {
            "user_profile": user_profile,
            "user_metadata": user_metadata
        }
    
    def build_user_text(self, user_data: Dict[str, Any]) -> tuple[str, str]:
        """从数据库数据构建用户文本描述"""
        user_profile = user_data["user_profile"]
        user_metadata = user_data["user_metadata"]
        
        # 构建完整的用户描述文本
        text_parts = []
        request_type = "all"
        
        # 添加基本信息
        text_parts.append(f"用户: {user_profile.get('display_name', '')}")
        text_parts.append(f"昵称: {user_profile.get('nickname', '')}")
        
        # 从元数据中提取信息
        for item in user_metadata:
            section_type = item.get("section_type", "")
            section_key = item.get("section_key", "")
            content = item.get("content", {})
            
            if isinstance(content, str):
                try:
                    content = json.loads(content)
                except:
                    continue
            
            # 处理不同类型的内容
            if section_type == "profile":
                if section_key == "name":
                    greeting = content.get("greeting", "")
                    if greeting:
                        text_parts.append(f"问候语: {greeting}")
                
                elif section_key == "professional":
                    current_role = content.get("current_role", "")
                    responsibilities = content.get("responsibilities", [])
                    industry = content.get("industry", "")
                    if current_role:
                        text_parts.append(f"职业: {current_role}")
                    if industry:
                        text_parts.append(f"行业: {industry}")
                    if responsibilities:
                        text_parts.append(f"职责: {', '.join(responsibilities)}")
                
                elif section_key == "personal":
                    age_range = content.get("age_range", "")
                    location = content.get("location", "")
                    living_situation = content.get("living_situation", "")
                    if age_range:
                        text_parts.append(f"年龄: {age_range}")
                    if location:
                        text_parts.append(f"地点: {location}")
                    if living_situation:
                        text_parts.append(f"居住状况: {living_situation}")
                
                elif section_key == "personality":
                    mbti_type = content.get("mbti_type", "")
                    personality_traits = content.get("personality_traits", [])
                    interests = content.get("interests", [])
                    values = content.get("values", [])
                    if mbti_type:
                        text_parts.append(f"MBTI: {mbti_type}")
                    if personality_traits:
                        text_parts.append(f"性格特点: {', '.join(personality_traits)}")
                    if interests:
                        text_parts.append(f"兴趣爱好: {', '.join(interests)}")
                    if values:
                        text_parts.append(f"价值观: {', '.join(values)}")
                
                elif section_key == "qa_responses":
                    question = content.get("question", "")
                    answer = content.get("answer", "")
                    if question and answer:
                        text_parts.append(f"问: {question} 答: {answer}")
                
                elif section_key == "content":
                    post_content = content.get("content", "")
                    if post_content:
                        text_parts.append(f"发布内容: {post_content}")
            
            elif section_type == "user_request":
                req_type = content.get("request_type", "")
                description = content.get("description", "")
                if req_type:
                    request_type = req_type
                if description:
                    text_parts.append(f"用户需求: {description}")
        
        user_text = ". ".join(text_parts)
        return user_text, request_type

class TagGenerator:
    """标签生成器"""
    
    def __init__(self):
        self.profile_analyzer = UserProfileAnalyzer()
    
    def generate_tags(self, user_id: str, user_text: str, request_type: str) -> TagGenerationResult:
        """为单个用户生成标签"""
        start_time = datetime.now()
        
        # 1. 使用LDA主题建模生成标签
        lda_result = topic_model.extract_topics_and_tags(user_text, request_type)
        lda_tags = lda_result.extracted_tags
        lda_metadata = {
            "topics": [(int(tid), float(weight)) for tid, weight in lda_result.topics],
            "topic_keywords": {
                int(tid): [(word, float(weight)) for word, weight in words] 
                for tid, words in lda_result.topic_keywords.items()
            },
            "text_vector": [float(x) for x in lda_result.text_vector],
            "source_text_length": len(user_text)
        }
        
        # 2. 使用用户画像分析器生成标签
        try:
            profile_result = self.profile_analyzer.analyze_user(user_id, user_text, request_type)
            profile_tags = profile_result.extracted_tags
            profile_metadata = {
                "tag_categories": profile_result.tag_categories,
                "total_score": profile_result.total_score,
                "profile_completeness": profile_result.profile_completeness,
                "request_type": profile_result.request_type
            }
        except Exception as e:
            print(f"  警告: 用户画像分析器处理 {user_id} 时出错: {e}")
            profile_tags = {}
            profile_metadata = {"error": str(e)}
        
        generation_time = (datetime.now() - start_time).total_seconds()
        
        return TagGenerationResult(
            user_id=user_id,
            lda_tags=lda_tags,
            lda_metadata=lda_metadata,
            profile_analyzer_tags=profile_tags,
            profile_analyzer_metadata=profile_metadata,
            total_tags=len(lda_tags) + len(profile_tags),
            generation_time=generation_time
        )

class TagStorage:
    """标签存储器"""
    
    def __init__(self, supabase: Client):
        self.supabase = supabase
    
    def save_tags(self, result: TagGenerationResult) -> bool:
        """保存标签到数据库"""
        try:
            tags_to_insert = []
            
            # 保存LDA标签
            for tag_name, confidence in result.lda_tags.items():
                tags_to_insert.append({
                    "user_id": result.user_id,
                    "tag_source": "topic_modeling",
                    "tag_category": self._categorize_tag(tag_name),
                    "tag_name": tag_name,
                    "tag_value": tag_name,
                    "confidence_score": float(confidence),
                    "model_version": "v1.0",
                    "generation_context": json.dumps({
                        "generation_time": result.generation_time,
                        "algorithm": "LDA"
                    }, ensure_ascii=False),
                    "extraction_metadata": json.dumps(result.lda_metadata, ensure_ascii=False)
                })
            
            # 保存用户画像分析器标签
            for tag_name, confidence in result.profile_analyzer_tags.items():
                tags_to_insert.append({
                    "user_id": result.user_id,
                    "tag_source": "user_profile_analyzer",
                    "tag_category": self._categorize_tag(tag_name),
                    "tag_name": tag_name,
                    "tag_value": tag_name,
                    "confidence_score": float(confidence),
                    "model_version": "v1.0",
                    "generation_context": json.dumps({
                        "generation_time": result.generation_time,
                        "algorithm": "ProfileAnalyzer"
                    }, ensure_ascii=False),
                    "extraction_metadata": json.dumps(result.profile_analyzer_metadata, ensure_ascii=False)
                })
            
            # 分批插入，避免数据过大
            if tags_to_insert:
                batch_size = 50  # 每批最多50个标签
                for i in range(0, len(tags_to_insert), batch_size):
                    batch = tags_to_insert[i:i + batch_size]
                    self.supabase.table("user_tags").insert(batch).execute()
                    print(f"    插入了 {len(batch)} 个标签")
            
            return True
            
        except Exception as e:
            print(f"  ❌ 保存标签失败: {e}")
            return False
    
    def _categorize_tag(self, tag_name: str) -> str:
        """简单的标签分类逻辑"""
        tag_lower = tag_name.lower()
        
        # 性格相关
        personality_keywords = ["内向", "外向", "开朗", "阳光", "冷静", "理性", "感性", "MBTI", "性格"]
        if any(keyword in tag_lower for keyword in personality_keywords):
            return "personality"
        
        # 兴趣相关
        interest_keywords = ["健身", "运动", "音乐", "读书", "旅行", "摄影", "游戏", "电影"]
        if any(keyword in tag_lower for keyword in interest_keywords):
            return "interests"
        
        # 职业相关
        professional_keywords = ["工程师", "设计师", "教练", "老师", "医生", "创业", "技术", "管理"]
        if any(keyword in tag_lower for keyword in professional_keywords):
            return "professional"
        
        # 生活方式
        lifestyle_keywords = ["健康", "早睡", "规律", "生活", "居住", "饮食"]
        if any(keyword in tag_lower for keyword in lifestyle_keywords):
            return "lifestyle"
        
        # 价值观
        values_keywords = ["诚实", "成长", "创新", "坚持", "帮助", "积极"]
        if any(keyword in tag_lower for keyword in values_keywords):
            return "values"
        
        # 默认分类
        return "other"

class BatchTagGenerator:
    """批量标签生成器"""
    
    def __init__(self, supabase_url: str, supabase_key: str):
        if not SUPABASE_AVAILABLE:
            raise ImportError("supabase package is required")
        
        self.supabase = create_client(supabase_url, supabase_key)
        self.data_reader = UserDataReader(self.supabase)
        self.tag_generator = TagGenerator()
        self.tag_storage = TagStorage(self.supabase)
        self.stats = BatchStats()
    
    def clear_existing_tags(self) -> bool:
        """清除现有的所有标签（可选）"""
        try:
            result = self.supabase.table("user_tags").delete().neq("id", "").execute()
            print(f"清除了现有标签")
            return True
        except Exception as e:
            print(f"清除现有标签失败: {e}")
            return False
    
    def process_single_user(self, user_id: str) -> bool:
        """处理单个用户"""
        try:
            print(f"\n正在处理用户: {user_id}")
            
            # 1. 获取用户数据
            user_data = self.data_reader.get_user_data(user_id)
            
            # 2. 构建用户文本
            user_text, request_type = self.data_reader.build_user_text(user_data)
            print(f"  - 用户文本长度: {len(user_text)}")
            print(f"  - 请求类型: {request_type}")
            print(f"  - 文本预览: {user_text[:200]}...")
            
            # 3. 生成标签
            result = self.tag_generator.generate_tags(user_id, user_text, request_type)
            print(f"  - LDA标签: {len(result.lda_tags)}个")
            print(f"  - 画像分析标签: {len(result.profile_analyzer_tags)}个")
            print(f"  - 生成用时: {result.generation_time:.2f}秒")
            
            # 4. 保存标签
            if self.tag_storage.save_tags(result):
                print(f"  ✅ 成功处理: {user_id} (总计{result.total_tags}个标签)")
                self.stats.total_tags_generated += result.total_tags
                return True
            else:
                print(f"  ❌ 保存失败: {user_id}")
                return False
                
        except Exception as e:
            error_msg = f"处理用户 {user_id} 时出错: {str(e)}"
            print(f"  ❌ {error_msg}")
            self.stats.errors.append(error_msg)
            return False
    
    def process_all_users(self, clear_existing: bool = False) -> BatchStats:
        """处理所有用户"""
        print("🚀 开始批量生成用户标签...")
        
        # 可选：清除现有标签
        if clear_existing:
            print("清除现有标签...")
            self.clear_existing_tags()
        
        # 获取所有用户
        try:
            user_ids = self.data_reader.get_all_users()
            self.stats.total_users = len(user_ids)
            print(f"找到 {self.stats.total_users} 个用户")
        except Exception as e:
            self.stats.errors.append(f"获取用户列表失败: {str(e)}")
            return self.stats
        
        # 逐个处理用户
        for user_id in user_ids:
            try:
                if self.process_single_user(user_id):
                    self.stats.processed_users += 1
                else:
                    self.stats.failed_users += 1
            except Exception as e:
                self.stats.failed_users += 1
                self.stats.errors.append(f"处理用户 {user_id} 时出现未知错误: {str(e)}")
        
        # 打印统计结果
        print(f"\n📊 批量处理完成!")
        print(f"总用户数: {self.stats.total_users}")
        print(f"成功处理: {self.stats.processed_users}")
        print(f"处理失败: {self.stats.failed_users}")
        print(f"生成标签总数: {self.stats.total_tags_generated}")
        
        if self.stats.errors:
            print(f"\n❌ 错误详情:")
            for error in self.stats.errors[:10]:  # 只显示前10个错误
                print(f"  - {error}")
            if len(self.stats.errors) > 10:
                print(f"  ... 还有 {len(self.stats.errors) - 10} 个错误")
        
        return self.stats

def main():
    """主函数"""
    # 从环境变量获取Supabase配置
    supabase_url = os.getenv("SUPABASE_URL") or "https://anxbbsrnjgmotxzysqwf.supabase.co"
    supabase_key = os.getenv("SUPABASE_ANON_KEY") or "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFueGJic3Juamdtb3R4enlzcXdmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTA0MDY0OTIsImV4cCI6MjA2NTk4MjQ5Mn0.a0t-pgH-Z2Fbs6JuMNWX8_kpqkQsBag3-COAUZVF6-0"
    
    try:
        # 创建批量生成器
        generator = BatchTagGenerator(supabase_url, supabase_key)
        
        # 处理所有用户（设置为True会清除现有标签）
        stats = generator.process_all_users(clear_existing=True)
        
        # 返回状态码
        return 0 if stats.failed_users == 0 else 1
        
    except Exception as e:
        print(f"❌ 批量处理初始化失败: {e}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main()) 