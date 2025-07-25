#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import sys
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# 添加项目根目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from configs.config import ConfigManager
from backend.models import CompatibilityResult
from backend.models.tag_pool import TagPool
from backend.models.topic_modeling import LDATopicModel, TopicResult
from backend.models.vector_matching import VectorUserMatcher, UserVector
from backend.models.matching_result import SimpleMatchingResult, create_match_dimension, generate_score_description, calculate_complementary_score

@dataclass
class EnhancedCompatibilityResult:
    """增强的兼容性分析结果"""
    # 基础信息
    person_a: str
    person_b: str
    
    # 传统评分
    mutual_interest_score: float
    request_matching_score: float
    personality_matching_score: float
    
    # 新增向量匹配评分
    vector_similarity_score: float
    profile_similarity: float
    request_similarity: float
    
    # 标签信息
    person_a_tags: Dict[str, float]
    person_b_tags: Dict[str, float]
    mutual_tags: List[str]
    complementary_tags: List[str]
    
    # 主题信息
    person_a_topics: List[tuple]
    person_b_topics: List[tuple]
    
    # 匹配解释
    vector_explanation: str
    overall_recommendation: str
    
    # 详细分析
    detailed_analysis: str

class EnhancedCompatibilityAnalyzer:
    """增强的兼容性分析器"""
    
    def __init__(self, config: Optional[ConfigManager] = None):
        self.config_manager = config or ConfigManager()
        
        # 初始化组件
        self.tag_pool = TagPool()
        self.topic_model = LDATopicModel(self.config_manager.topic_config)
        self.vector_matcher = VectorUserMatcher(self.config_manager.vector_config)
        
        # 模型训练状态
        self.is_model_trained = False
        
    def prepare_training_data(self, profile_paths: List[str]) -> List[str]:
        """准备训练数据"""
        training_texts = []
        
        for profile_path in profile_paths:
            if not os.path.exists(profile_path):
                continue
                
            profile = self.load_profile(profile_path)
            
            # 提取所有文本内容
            text_parts = []
            
            # 个人信息
            if 'profile' in profile:
                profile_data = profile['profile']
                
                # 职业信息
                if 'professional' in profile_data:
                    prof = profile_data['professional']
                    text_parts.extend([
                        prof.get('current_role', ''),
                        ' '.join(prof.get('responsibilities', [])),
                        ' '.join(prof.get('previous_experience', [])),
                        prof.get('industry', '')
                    ])
                
                # 个性信息
                if 'personality' in profile_data:
                    pers = profile_data['personality']
                    text_parts.extend([
                        pers.get('mbti_type', ''),
                        ' '.join(pers.get('interests', [])),
                        pers.get('philosophy', ''),
                        ' '.join(pers.get('hobbies', []))
                    ])
                
                # 生活方式
                if 'lifestyle' in profile_data:
                    lifestyle = profile_data['lifestyle']
                    text_parts.extend([
                        lifestyle.get('location', ''),
                        lifestyle.get('living_situation', ''),
                        lifestyle.get('exercise_habits', ''),
                        lifestyle.get('social_life', '')
                    ])
                
                # 其他字段 - 适配Noah和Alan的档案结构
                if 'personal' in profile_data:
                    personal = profile_data['personal']
                    text_parts.extend([
                        personal.get('description', ''),
                        personal.get('life_motto', ''),
                        ' '.join(personal.get('keywords', []))
                    ])
                
                if 'career_journey' in profile_data:
                    career = profile_data['career_journey']
                    for period_key, period_data in career.items():
                        if isinstance(period_data, dict):
                            text_parts.extend([
                                period_data.get('role', ''),
                                period_data.get('description', ''),
                                ' '.join(period_data.get('achievements', [])),
                                ' '.join(period_data.get('focus_areas', []))
                            ])
                
                # 专业领域
                if 'expertise_areas' in profile_data:
                    text_parts.extend(profile_data['expertise_areas'])
            
            # 用户诉求
            if 'user_request' in profile:
                req = profile['user_request']
                text_parts.extend([
                    req.get('request_type', ''),
                    req.get('description', '')
                ])
            
            # 合并文本
            combined_text = ' '.join([t for t in text_parts if t])
            if combined_text.strip():
                training_texts.append(combined_text)
        
        return training_texts
    
    def train_models(self, profile_paths: List[str]) -> None:
        """训练主题模型"""
        print("开始训练主题建模模型...")
        
        # 准备训练数据
        training_texts = self.prepare_training_data(profile_paths)
        
        if len(training_texts) < 2:
            raise ValueError("训练数据不足，至少需要2个有效的用户档案")
        
        print(f"准备了 {len(training_texts)} 个训练文档")
        
        # 训练LDA模型
        self.topic_model.train(training_texts)
        
        print("主题建模训练完成")
        self.is_model_trained = True
    
    def load_profile(self, profile_path: str) -> Dict[str, Any]:
        """加载用户档案"""
        with open(profile_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def extract_profile_text(self, profile: Dict[str, Any]) -> str:
        """从档案中提取文本"""
        text_parts = []
        
        if 'profile' in profile:
            profile_data = profile['profile']
            
            # 提取各部分文本
            for section in ['professional', 'personality', 'lifestyle', 'personal', 'expertise_areas']:
                if section in profile_data:
                    section_data = profile_data[section]
                    if isinstance(section_data, dict):
                        for key, value in section_data.items():
                            if isinstance(value, str):
                                text_parts.append(value)
                            elif isinstance(value, list):
                                text_parts.extend([str(v) for v in value])
                    elif isinstance(section_data, list):
                        text_parts.extend([str(item) for item in section_data])
            
            # 处理复杂的嵌套结构（如career_journey）
            if 'career_journey' in profile_data:
                career = profile_data['career_journey']
                for period_key, period_data in career.items():
                    if isinstance(period_data, dict):
                        for key, value in period_data.items():
                            if isinstance(value, str):
                                text_parts.append(value)
                            elif isinstance(value, list):
                                text_parts.extend([str(v) for v in value])
        
        return ' '.join(text_parts)
    
    def extract_request_text(self, profile: Dict[str, Any]) -> str:
        """从档案中提取诉求文本"""
        if 'user_request' in profile:
            req = profile['user_request']
            return f"{req.get('request_type', '')} {req.get('description', '')}"
        return ""
    
    def analyze_single_profile(self, profile_path: str) -> Dict[str, Any]:
        """分析单个用户档案"""
        if not self.is_model_trained:
            raise ValueError("模型尚未训练，请先调用train_models()")
        
        profile = self.load_profile(profile_path)
        user_id = profile.get('profile', {}).get('name', {}).get('display_name', 
                                                os.path.basename(profile_path))
        
        # 提取文本
        profile_text = self.extract_profile_text(profile)
        request_text = self.extract_request_text(profile)
        request_type = profile.get('user_request', {}).get('request_type', '找队友')
        
        print(f"分析用户: {user_id}")
        print(f"档案文本长度: {len(profile_text)}")
        print(f"诉求文本: {request_text[:100]}...")
        
        # 主题建模分析
        profile_result = self.topic_model.extract_topics_and_tags(profile_text, request_type)
        request_result = self.topic_model.extract_topics_and_tags(request_text, request_type)
        
        print(f"提取档案标签: {len(profile_result.extracted_tags)}个")
        print(f"提取诉求标签: {len(request_result.extracted_tags)}个")
        
        # 合并标签
        all_tags = {}
        all_tags.update(profile_result.extracted_tags)
        all_tags.update(request_result.extracted_tags)
        
        # 添加到向量匹配器
        self.vector_matcher.add_user(
            user_id=user_id,
            profile_tags=profile_result.extracted_tags,
            request_tags=request_result.extracted_tags,
            request_type=request_type,
            metadata={'profile_path': profile_path, 'topics': profile_result.topics}
        )
        
        return {
            'user_id': user_id,
            'profile_tags': profile_result.extracted_tags,
            'request_tags': request_result.extracted_tags,
            'all_tags': all_tags,
            'profile_topics': profile_result.topics,
            'request_topics': request_result.topics,
            'request_type': request_type
        }
    
    def batch_analyze_profiles(self, profile_paths: List[str]) -> Dict[str, Dict[str, Any]]:
        """批量分析用户档案"""
        print(f"开始分析 {len(profile_paths)} 个用户档案...")
        
        results = {}
        for profile_path in profile_paths:
            if os.path.exists(profile_path):
                try:
                    result = self.analyze_single_profile(profile_path)
                    results[result['user_id']] = result
                    print(f"✓ 分析完成: {result['user_id']}")
                except Exception as e:
                    print(f"✗ 分析失败: {profile_path} - {e}")
        
        # 构建向量索引
        if results:
            print("构建向量索引...")
            self.vector_matcher.build_indices()
            print("向量索引构建完成")
        
        return results
    
    def enhanced_compatibility_analysis(self, profile_a_path: str, profile_b_path: str) -> EnhancedCompatibilityResult:
        """增强的兼容性分析"""
        
        # 加载档案
        profile_a = self.load_profile(profile_a_path)
        profile_b = self.load_profile(profile_b_path)
        
        user_a_id = profile_a.get('profile', {}).get('name', {}).get('display_name', 'Person A')
        user_b_id = profile_b.get('profile', {}).get('name', {}).get('display_name', 'Person B')
        
        # 如果用户不在向量匹配器中，先添加
        if user_a_id not in self.vector_matcher.users:
            self.analyze_single_profile(profile_a_path)
        if user_b_id not in self.vector_matcher.users:
            self.analyze_single_profile(profile_b_path)
            self.vector_matcher.build_indices()  # 重建索引
        
        # 获取向量匹配结果
        matches = self.vector_matcher.find_matches(user_a_id, top_k=10)
        vector_result = None
        for match in matches:
            if match.user_b_id == user_b_id:
                vector_result = match
                break
        
        if not vector_result:
            # 如果没有找到匹配，手动计算
            user_a = self.vector_matcher.users[user_a_id]
            user_b = self.vector_matcher.users[user_b_id]
            vector_result = self.vector_matcher._calculate_detailed_similarity(
                user_a, user_b, 0.0
            )
        
        # 计算传统评分（简化版）
        mutual_score = min(10.0, vector_result.similarity_score * 10)
        request_score = min(10.0, vector_result.request_similarity * 10)
        personality_score = min(10.0, vector_result.profile_similarity * 10)
        
        # 生成综合建议
        overall_recommendation = self._generate_overall_recommendation(vector_result)
        
        return EnhancedCompatibilityResult(
            person_a=user_a_id,
            person_b=user_b_id,
            mutual_interest_score=mutual_score,
            request_matching_score=request_score,
            personality_matching_score=personality_score,
            vector_similarity_score=vector_result.similarity_score,
            profile_similarity=vector_result.profile_similarity,
            request_similarity=vector_result.request_similarity,
            person_a_tags=self.vector_matcher.users[user_a_id].tags,
            person_b_tags=self.vector_matcher.users[user_b_id].tags,
            mutual_tags=vector_result.mutual_tags,
            complementary_tags=vector_result.complementary_tags,
            person_a_topics=self.vector_matcher.users[user_a_id].metadata.get('topics', []),
            person_b_topics=self.vector_matcher.users[user_b_id].metadata.get('topics', []),
            vector_explanation=vector_result.explanation,
            overall_recommendation=overall_recommendation,
            detailed_analysis=f"基于主题建模和向量匹配的详细分析：\n{vector_result.explanation}"
        )
    
    def _generate_overall_recommendation(self, similarity_score: float) -> str:
        """生成综合建议"""
        if similarity_score > 0.8:
            return "强烈推荐：两人在多个维度高度匹配，建议积极联系"
        elif similarity_score > 0.6:
            return "推荐：两人具有良好的匹配度，可以尝试深入了解"
        elif similarity_score > 0.4:
            return "中等匹配：存在一定相似性，可以作为候选考虑"
        else:
            return "匹配度较低：两人差异较大，需要谨慎考虑"
    
    def generate_simple_result(self, detailed_result: EnhancedCompatibilityResult) -> SimpleMatchingResult:
        """生成简洁的JSON格式结果"""
        
        # 计算各维度评分
        personality_score = self._calculate_personality_score(detailed_result)
        interests_score = self._calculate_interests_score(detailed_result)
        career_score = self._calculate_career_score(detailed_result)
        values_score = self._calculate_values_score(detailed_result)
        request_score = detailed_result.request_similarity * 10
        complementary_score = calculate_complementary_score(
            detailed_result.person_a_tags, 
            detailed_result.person_b_tags
        )
        
        # 计算总体评分
        overall_score = (personality_score + interests_score + career_score + 
                        values_score + request_score + complementary_score) / 6
        
        return SimpleMatchingResult(
            person_a=detailed_result.person_a,
            person_b=detailed_result.person_b,
            overall_match=create_match_dimension(
                overall_score,
                generate_score_description(overall_score, "总体"),
                self._generate_overall_details(detailed_result)
            ),
            personality_match=create_match_dimension(
                personality_score,
                generate_score_description(personality_score, "性格"),
                self._generate_personality_details(detailed_result)
            ),
            interests_match=create_match_dimension(
                interests_score,
                generate_score_description(interests_score, "兴趣"),
                self._generate_interests_details(detailed_result)
            ),
            career_match=create_match_dimension(
                career_score,
                generate_score_description(career_score, "职业"),
                self._generate_career_details(detailed_result)
            ),
            values_match=create_match_dimension(
                values_score,
                generate_score_description(values_score, "价值观"),
                self._generate_values_details(detailed_result)
            ),
            request_match=create_match_dimension(
                request_score,
                generate_score_description(request_score, "诉求"),
                self._generate_request_details(detailed_result)
            ),
            complementary_match=create_match_dimension(
                complementary_score,
                generate_score_description(complementary_score, "互补性"),
                self._generate_complementary_details(detailed_result)
            )
        )
    
    def _calculate_personality_score(self, result: EnhancedCompatibilityResult) -> float:
        """计算性格匹配评分"""
        personality_tags = ["外向开朗", "内向安静", "幽默风趣", "温和体贴", "理性冷静", "感性浪漫"]
        return self._calculate_tag_similarity(result.person_a_tags, result.person_b_tags, personality_tags) * 10
    
    def _calculate_interests_score(self, result: EnhancedCompatibilityResult) -> float:
        """计算兴趣匹配评分"""
        interest_tags = ["运动健身", "音乐", "电影", "读书", "旅行", "摄影", "美食", "游戏", "艺术"]
        return self._calculate_tag_similarity(result.person_a_tags, result.person_b_tags, interest_tags) * 10
    
    def _calculate_career_score(self, result: EnhancedCompatibilityResult) -> float:
        """计算职业匹配评分"""
        career_tags = ["程序员", "设计师", "产品经理", "创业者", "有创业经验", "技术型"]
        return self._calculate_tag_similarity(result.person_a_tags, result.person_b_tags, career_tags) * 10
    
    def _calculate_values_score(self, result: EnhancedCompatibilityResult) -> float:
        """计算价值观匹配评分"""
        values_tags = ["事业优先", "个人成长", "团队合作", "创新进取", "创造价值"]
        return self._calculate_tag_similarity(result.person_a_tags, result.person_b_tags, values_tags) * 10
    
    def _calculate_tag_similarity(self, tags_a: Dict[str, float], tags_b: Dict[str, float], 
                                 relevant_tags: List[str]) -> float:
        """计算特定标签的相似度"""
        a_relevant = {tag: score for tag, score in tags_a.items() if tag in relevant_tags}
        b_relevant = {tag: score for tag, score in tags_b.items() if tag in relevant_tags}
        
        if not a_relevant and not b_relevant:
            return 0.5  # 都没有相关标签，给中等评分
        
        common_tags = set(a_relevant.keys()) & set(b_relevant.keys())
        if common_tags:
            similarity = sum(min(a_relevant[tag], b_relevant[tag]) for tag in common_tags) / len(common_tags)
            return min(similarity, 1.0)
        
        return 0.2  # 没有共同标签
    
    def _generate_overall_details(self, result: EnhancedCompatibilityResult) -> str:
        """生成总体匹配详情"""
        return f"共同标签{len(result.mutual_tags)}个，诉求类型匹配，向量相似度{result.vector_similarity_score:.2f}"
    
    def _generate_personality_details(self, result: EnhancedCompatibilityResult) -> str:
        """生成性格匹配详情"""
        personality_tags = [tag for tag in result.mutual_tags if any(p in tag for p in ["外向", "内向", "性格", "MBTI"])]
        if personality_tags:
            return f"共同性格特征：{', '.join(personality_tags[:3])}"
        return "性格特征差异较大，但可能形成互补"
    
    def _generate_interests_details(self, result: EnhancedCompatibilityResult) -> str:
        """生成兴趣匹配详情"""
        interest_tags = [tag for tag in result.mutual_tags if tag in ["运动健身", "音乐", "电影", "读书", "旅行", "摄影"]]
        if interest_tags:
            return f"共同兴趣：{', '.join(interest_tags[:3])}"
        return "兴趣爱好不同，但可以互相学习"
    
    def _generate_career_details(self, result: EnhancedCompatibilityResult) -> str:
        """生成职业匹配详情"""
        career_tags = [tag for tag in result.mutual_tags if "经验" in tag or "开发" in tag or "创业" in tag]
        if career_tags:
            return f"职业相关：{', '.join(career_tags[:3])}"
        return "职业背景不同，具有互补潜力"
    
    def _generate_values_details(self, result: EnhancedCompatibilityResult) -> str:
        """生成价值观匹配详情"""
        values_tags = [tag for tag in result.mutual_tags if any(v in tag for v in ["价值", "成长", "创新", "合作"])]
        if values_tags:
            return f"共同价值观：{', '.join(values_tags[:3])}"
        return "价值观可能存在差异，需要进一步了解"
    
    def _generate_request_details(self, result: EnhancedCompatibilityResult) -> str:
        """生成诉求匹配详情"""
        return f"诉求相似度{result.request_similarity:.2f}，都在寻找合作伙伴"
    
    def _generate_complementary_details(self, result: EnhancedCompatibilityResult) -> str:
        """生成互补性详情"""
        return "技能和经验背景存在互补性，可能形成良好的合作关系"
    
    def analyze_and_output_simple_result(self, profile_a_path: str, profile_b_path: str) -> str:
        """分析并输出简洁的JSON结果"""
        
        # 先训练模型（如果未训练）
        if not self.is_model_trained:
            self.train_models([profile_a_path, profile_b_path])
        
        # 进行详细分析
        detailed_result = self.enhanced_compatibility_analysis(profile_a_path, profile_b_path)
        
        # 生成简洁结果
        simple_result = self.generate_simple_result(detailed_result)
        
        # 返回JSON字符串
        return simple_result.to_json()
    
    def save_models(self, model_dir: str = "data/models") -> None:
        """保存训练的模型"""
        os.makedirs(model_dir, exist_ok=True)
        
        if self.is_model_trained:
            # 保存LDA模型
            lda_path = os.path.join(model_dir, "lda_model")
            self.topic_model.save_model(lda_path)
            
            # 保存向量数据
            vector_path = os.path.join(model_dir, "user_vectors.json")
            self.vector_matcher.save_vectors(vector_path)
            
            print(f"模型已保存到: {model_dir}")
    
    def load_models(self, model_dir: str = "data/models") -> None:
        """加载训练的模型"""
        try:
            # 加载LDA模型
            lda_path = os.path.join(model_dir, "lda_model")
            self.topic_model.load_model(lda_path)
            
            # 加载向量数据
            vector_path = os.path.join(model_dir, "user_vectors.json")
            self.vector_matcher.load_vectors(vector_path)
            
            # 重建向量索引
            self.vector_matcher.build_indices()
            
            self.is_model_trained = True
            print(f"模型已从 {model_dir} 加载")
        except Exception as e:
            print(f"加载模型失败: {e}")
            raise

# 示例使用函数
def main():
    """示例主函数"""
    print("=== 增强兼容性分析系统 ===")
    
    # 初始化分析器
    analyzer = EnhancedCompatibilityAnalyzer()
    
    # 用户档案路径
    profile_paths = [
        "data/profiles/noah_profile.json",
        "data/profiles/kyrie_profile.json", 
        "data/profiles/alan_profile.json",
        "data/profiles/example_dating_profile.json"
    ]
    
    # 过滤存在的档案
    existing_profiles = [p for p in profile_paths if os.path.exists(p)]
    
    if len(existing_profiles) < 2:
        print("错误：需要至少2个用户档案进行分析")
        return
    
    try:
        print(f"\n1. 训练主题模型（基于 {len(existing_profiles)} 个档案）...")
        analyzer.train_models(existing_profiles)
        
        print("\n2. 进行增强兼容性分析...")
        results = analyzer.batch_enhanced_analysis(existing_profiles)
        
        print(f"\n3. 分析结果（{len(results)} 个配对）:")
        for result in results:
            print(f"\n{result.person_a} ↔ {result.person_b}:")
            print(f"  向量相似度: {result.vector_similarity_score:.3f}")
            print(f"  档案相似度: {result.profile_similarity:.3f}")
            print(f"  诉求相似度: {result.request_similarity:.3f}")
            print(f"  共同标签: {len(result.mutual_tags)}个")
            print(f"  推荐: {result.overall_recommendation}")
            print(f"  解释: {result.vector_explanation}")
        
        print("\n4. 保存模型...")
        analyzer.save_models()
        
        print("\n✓ 分析完成！")
        
    except Exception as e:
        print(f"分析过程中出错: {e}")

if __name__ == "__main__":
    main() 