#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
用户画像分析器 - 基于预定义标签池的文本分析系统

这个系统的核心理念是：
1. 不需要复杂的LDA训练过程
2. 直接基于预定义标签池进行匹配
3. 使用多种匹配策略提高准确率
4. 适用于你的"找对象"和"找队友"场景
"""

import json
import os
from typing import Dict, List, Any
from dataclasses import dataclass, asdict
from models.tag_matching import TagMatcher, TagMatchResult

@dataclass
class UserProfile:
    """用户画像"""
    user_id: str
    request_type: str  # "找对象" 或 "找队友"
    original_text: str
    extracted_tags: Dict[str, float]
    tag_categories: Dict[str, List[tuple]]  # 序列化友好的格式
    total_score: float
    profile_completeness: float  # 画像完整度 0-1

class UserProfileAnalyzer:
    """用户画像分析器"""
    
    def __init__(self):
        # 为不同场景创建专门的匹配器
        self.dating_matcher = TagMatcher("找对象")
        self.teamwork_matcher = TagMatcher("找队友")
        
        # 存储路径
        self.profiles_dir = "data/user_profiles"
        self._ensure_directories()
    
    def _ensure_directories(self):
        """确保目录存在"""
        os.makedirs(self.profiles_dir, exist_ok=True)
    
    def analyze_user(self, user_id: str, user_text: str, request_type: str) -> UserProfile:
        """分析单个用户并生成画像"""
        
        # 选择对应的匹配器
        if request_type == "找对象":
            matcher = self.dating_matcher
        elif request_type == "找队友":
            matcher = self.teamwork_matcher
        else:
            raise ValueError(f"不支持的请求类型: {request_type}")
        
        # 进行标签匹配
        result = matcher.match_tags(user_text, min_confidence=0.3)
        
        # 计算画像完整度
        completeness = self._calculate_completeness(result, request_type)
        
        # 转换tag_categories为可序列化格式
        serializable_categories = {}
        for category, tags in result.tag_categories.items():
            serializable_categories[category.value] = tags
        
        # 创建用户画像
        profile = UserProfile(
            user_id=user_id,
            request_type=request_type,
            original_text=user_text,
            extracted_tags=result.matched_tags,
            tag_categories=serializable_categories,
            total_score=result.total_score,
            profile_completeness=completeness
        )
        
        return profile
    
    def _calculate_completeness(self, result: TagMatchResult, request_type: str) -> float:
        """计算画像完整度"""
        if request_type == "找对象":
            # 找对象需要的关键维度
            required_categories = ["age", "profession", "personality", "interests", "location"]
        else:
            # 找队友需要的关键维度
            required_categories = ["skills", "experience_level", "project_type", "availability"]
        
        covered_categories = set()
        for category_name in result.tag_categories.keys():
            if category_name.value in required_categories:
                covered_categories.add(category_name.value)
        
        return len(covered_categories) / len(required_categories)
    
    def batch_analyze_users(self, users_data: List[Dict[str, Any]]) -> List[UserProfile]:
        """批量分析用户"""
        profiles = []
        
        for user_data in users_data:
            user_id = user_data["user_id"]
            user_text = user_data["text"]
            request_type = user_data["request_type"]
            
            try:
                profile = self.analyze_user(user_id, user_text, request_type)
                profiles.append(profile)
                print(f"✅ 成功分析用户 {user_id}")
            except Exception as e:
                print(f"❌ 分析用户 {user_id} 时出错: {e}")
        
        return profiles
    
    def save_profile(self, profile: UserProfile) -> None:
        """保存用户画像到文件"""
        filename = f"{profile.user_id}_{profile.request_type}_profile.json"
        filepath = os.path.join(self.profiles_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(asdict(profile), f, ensure_ascii=False, indent=2)
        
        print(f"画像已保存: {filepath}")
    
    def load_profile(self, user_id: str, request_type: str) -> UserProfile:
        """从文件加载用户画像"""
        filename = f"{user_id}_{request_type}_profile.json"
        filepath = os.path.join(self.profiles_dir, filename)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return UserProfile(**data)
    
    def find_similar_users(self, target_profile: UserProfile, 
                          candidate_profiles: List[UserProfile], 
                          top_k: int = 5) -> List[tuple]:
        """找到相似的用户"""
        similarities = []
        
        for candidate in candidate_profiles:
            if candidate.request_type != target_profile.request_type:
                continue
            
            # 计算标签重叠相似度
            similarity = self._calculate_tag_similarity(
                target_profile.extracted_tags, 
                candidate.extracted_tags
            )
            
            similarities.append((candidate.user_id, similarity, candidate))
        
        # 按相似度排序
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]
    
    def _calculate_tag_similarity(self, tags1: Dict[str, float], 
                                 tags2: Dict[str, float]) -> float:
        """计算两个标签集合的相似度"""
        if not tags1 or not tags2:
            return 0.0
        
        # 计算标签交集的权重和
        common_tags = set(tags1.keys()) & set(tags2.keys())
        if not common_tags:
            return 0.0
        
        # 使用余弦相似度
        dot_product = sum(tags1[tag] * tags2[tag] for tag in common_tags)
        norm1 = sum(score ** 2 for score in tags1.values()) ** 0.5
        norm2 = sum(score ** 2 for score in tags2.values()) ** 0.5
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def generate_profile_summary(self, profile: UserProfile) -> str:
        """生成画像摘要"""
        summary = f"""
用户画像摘要 - {profile.user_id}
================================
请求类型: {profile.request_type}
画像完整度: {profile.profile_completeness:.1%}
总体匹配分数: {profile.total_score:.2f}

提取的标签:
"""
        
        for category_name, tags in profile.tag_categories.items():
            if tags:
                summary += f"\n【{category_name}】\n"
                for tag, score in tags[:3]:  # 显示前3个最相关的标签
                    summary += f"  • {tag} (置信度: {score:.2f})\n"
        
        return summary

def demonstration_example():
    """演示如何使用用户画像分析器"""
    
    print("🎯 用户画像分析器演示")
    print("=" * 50)
    
    analyzer = UserProfileAnalyzer()
    
    # 模拟用户数据
    sample_users = [
        {
            "user_id": "user_001",
            "request_type": "找对象",
            "text": """
            我是一个28岁的产品经理，在北京工作。性格比较外向，
            喜欢和朋友聚会，周末经常去健身房锻炼，也喜欢旅行和摄影。
            希望找一个有共同兴趣爱好，性格开朗的女生一起生活。
            """
        },
        {
            "user_id": "user_002", 
            "request_type": "找队友",
            "text": """
            我是一个有5年经验的全栈开发工程师，擅长React、Node.js和Python。
            想找技术合伙人一起做一个SaaS产品，主要面向中小企业。
            希望能够长期合作，可以远程工作，但最好在上海。
            """
        },
        {
            "user_id": "user_003",
            "request_type": "找对象", 
            "text": """
            25岁程序员，比较内向，喜欢看书、打游戏、听音乐。
            工作在深圳，希望找一个理解我工作性质的女生，
            一起追剧、偶尔出去旅行就很满足了。
            """
        }
    ]
    
    # 批量分析用户
    print("🔍 开始批量分析用户...")
    profiles = analyzer.batch_analyze_users(sample_users)
    
    # 展示分析结果
    for i, profile in enumerate(profiles, 1):
        print(f"\n📊 用户 {i} 分析结果:")
        print(analyzer.generate_profile_summary(profile))
        
        # 保存画像（可选）
        # analyzer.save_profile(profile)
    
    # 演示找相似用户
    if len(profiles) >= 2:
        print("\n🔗 寻找相似用户:")
        target_user = profiles[0]
        other_users = profiles[1:]
        
        similar_users = analyzer.find_similar_users(target_user, other_users, top_k=2)
        
        print(f"与用户 {target_user.user_id} 最相似的用户:")
        for user_id, similarity, _ in similar_users:
            print(f"  • {user_id}: 相似度 {similarity:.3f}")

if __name__ == "__main__":
    demonstration_example() 