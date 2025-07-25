#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
基于主题发现的用户匹配系统 - 实际使用示例

这个示例展示了如何在你的实际场景中使用主题发现匹配系统：
1. 使用现有用户数据训练模型
2. 批量处理用户生成向量
3. 实时匹配新用户
4. 评估匹配效果
"""

import json
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from backend.models.topic_modeling import LDATopicModel
from backend.models.vector_matching import TopicVectorizer, VectorUserMatcher
from typing import List, Dict, Any

class ProductionMatchingSystem:
    """生产环境匹配系统"""
    
    def __init__(self, model_path: str = "data/models/production_model"):
        self.model_path = model_path
        self.vectorizer = None
        self.matcher = None
        self.is_trained = False
        
        # 确保目录存在
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        os.makedirs("data/user_vectors", exist_ok=True)
    
    def train_from_existing_users(self, users_data: List[Dict[str, Any]]) -> None:
        """从现有用户数据训练模型"""
        
        print("🔄 开始训练主题模型...")
        
        # 提取所有用户文本用于训练
        training_texts = [user['text'] for user in users_data if user.get('text')]
        
        if len(training_texts) < 10:
            print("⚠️  警告：训练数据太少，建议至少50个用户文本")
        
        # 根据数据量调整主题数
        n_topics = min(max(len(training_texts) // 10, 5), 30)
        
        print(f"📊 训练数据：{len(training_texts)} 个文本，主题数：{n_topics}")
        
        # 使用LDA方法（效果最佳）
        self.vectorizer = TopicVectorizer(
            method='lda',
            n_topics=n_topics,
            max_features=min(1000, len(training_texts) * 5),
            max_iter=20
        )
        
        # 训练模型
        self.vectorizer.train(training_texts)
        
        # 保存模型
        self.vectorizer.save_model(self.model_path)
        self.is_trained = True
        
        print("✅ 模型训练完成并已保存")
    
    def load_trained_model(self) -> bool:
        """加载已训练的模型"""
        try:
            self.vectorizer = TopicVectorizer(method='lda')
            self.vectorizer.load_model(self.model_path)
            self.is_trained = True
            print("✅ 已加载预训练模型")
            return True
        except Exception as e:
            print(f"❌ 加载模型失败: {e}")
            return False
    
    def process_all_users(self, users_data: List[Dict[str, Any]]) -> None:
        """批量处理所有用户"""
        
        if not self.is_trained:
            raise ValueError("模型尚未训练，请先调用train_from_existing_users()或load_trained_model()")
        
        print("🔄 批量处理用户向量...")
        
        # 创建匹配器
        self.matcher = VectorUserMatcher(self.vectorizer)
        
        # 批量添加用户
        self.matcher.add_users(users_data)
        
        # 保存用户向量
        self.matcher.save_user_vectors("data/user_vectors/all_users.json")
        
        print(f"✅ 已处理 {len(users_data)} 个用户")
    
    def find_matches_for_user(self, user_id: str, top_k: int = 10) -> List[tuple]:
        """为指定用户查找匹配"""
        if not self.matcher:
            # 尝试加载用户向量
            self.matcher = VectorUserMatcher(self.vectorizer)
            self.matcher.load_user_vectors("data/user_vectors/all_users.json")
        
        return self.matcher.find_similar_users(user_id, top_k=top_k, min_similarity=0.2)
    
    def add_new_user_and_find_matches(self, new_user: Dict[str, Any], top_k: int = 10) -> List[tuple]:
        """添加新用户并查找匹配"""
        
        if not self.matcher:
            self.matcher = VectorUserMatcher(self.vectorizer)
            self.matcher.load_user_vectors("data/user_vectors/all_users.json")
        
        # 添加新用户
        self.matcher.add_users([new_user])
        
        # 查找匹配
        matches = self.matcher.find_similar_users(
            new_user['user_id'], 
            top_k=top_k, 
            min_similarity=0.2
        )
        
        return matches
    
    def get_similarity_analysis(self, request_type: str = None) -> Dict[str, Any]:
        """获取相似度分析报告"""
        
        if not self.matcher:
            self.matcher = VectorUserMatcher(self.vectorizer)
            self.matcher.load_user_vectors("data/user_vectors/all_users.json")
        
        # 获取相似度矩阵
        similarity_matrix, user_ids = self.matcher.get_similarity_matrix(request_type)
        
        # 统计分析
        import numpy as np
        
        # 排除对角线（自己和自己的相似度）
        mask = ~np.eye(similarity_matrix.shape[0], dtype=bool)
        similarities = similarity_matrix[mask]
        
        analysis = {
            'total_users': len(user_ids),
            'average_similarity': float(np.mean(similarities)),
            'max_similarity': float(np.max(similarities)),
            'min_similarity': float(np.min(similarities)),
            'high_similarity_pairs': int(np.sum(similarities > 0.7)),
            'medium_similarity_pairs': int(np.sum((similarities > 0.3) & (similarities <= 0.7))),
            'low_similarity_pairs': int(np.sum(similarities <= 0.3))
        }
        
        return analysis

def demonstration_with_real_data():
    """使用实际数据的完整演示"""
    
    print("🎯 基于主题发现的用户匹配系统 - 实际使用演示")
    print("=" * 60)
    
    # 1. 模拟现有用户数据（从你的数据库获取）
    existing_users = [
        {
            "user_id": "tech_founder_001",
            "request_type": "找队友", 
            "text": "资深全栈工程师，10年开发经验，擅长Python、React、云架构。想找产品合伙人一起做SaaS产品，专注企业数字化转型。有过两次创业经历，希望找到有商业视野的合作伙伴。"
        },
        {
            "user_id": "product_manager_001",
            "request_type": "找队友",
            "text": "8年产品经验，曾在腾讯、字节担任高级产品经理。深度理解B端产品和用户增长，熟悉SaaS商业模式。正在寻找技术合伙人，希望做一款面向中小企业的智能客服产品。"
        },
        {
            "user_id": "designer_001", 
            "request_type": "找队友",
            "text": "UI/UX设计师，5年互联网设计经验，擅长产品设计和用户体验。参与过多个0到1的产品设计，对创业有浓厚兴趣，希望加入早期团队负责产品设计。"
        },
        {
            "user_id": "ai_researcher_001",
            "request_type": "找队友", 
            "text": "AI算法工程师，博士学历，专研机器学习和NLP。在顶级期刊发表多篇论文，想将AI技术商业化落地。寻找有商业化经验的合伙人一起做AI应用产品。"
        },
        {
            "user_id": "love_seeker_001",
            "request_type": "找对象",
            "text": "28岁程序员，性格内向但很温暖，平时喜欢读书、听音乐、看电影。工作稳定，在一线互联网公司做后端开发。希望找个善良温柔、有共同话题的女生，一起在北京生活。"
        },
        {
            "user_id": "love_seeker_002",
            "request_type": "找对象",
            "text": "26岁设计师，性格开朗外向，热爱旅行和摄影，周末经常户外运动。喜欢尝试新鲜事物，对生活充满热情。希望找个阳光积极、有生活情趣的男生，一起探索世界。"
        },
        {
            "user_id": "love_seeker_003",
            "request_type": "找对象", 
            "text": "29岁产品经理，工作和生活都很有规划，喜欢健身、美食、看书。性格成熟稳重，有自己的想法和目标。希望找个同样成熟、有上进心的人，一起规划未来。"
        },
        {
            "user_id": "love_seeker_004",
            "request_type": "找对象",
            "text": "25岁文案策划，热爱文字和创意，平时喜欢写作、看话剧、逛展览。性格文静但内心丰富，对精神世界很重视。希望找个有文化底蕴、能深度交流的人。"
        }
    ]
    
    # 2. 初始化匹配系统
    matching_system = ProductionMatchingSystem()
    
    # 3. 训练模型（第一次运行时）
    print("\n步骤1: 训练主题模型")
    matching_system.train_from_existing_users(existing_users)
    
    # 4. 处理现有用户
    print("\n步骤2: 处理现有用户")
    matching_system.process_all_users(existing_users)
    
    # 5. 为现有用户查找匹配
    print("\n步骤3: 为现有用户查找匹配")
    
    test_users = ["tech_founder_001", "love_seeker_001"]
    
    for user_id in test_users:
        print(f"\n🔍 为用户 {user_id} 查找匹配:")
        matches = matching_system.find_matches_for_user(user_id, top_k=3)
        
        if matches:
            for match_user_id, similarity in matches:
                print(f"  📍 {match_user_id}: 相似度 {similarity:.3f} ({similarity*100:.1f}%)")
        else:
            print("  ❌ 未找到合适的匹配")
    
    # 6. 模拟新用户注册
    print("\n步骤4: 新用户注册并查找匹配")
    
    new_user = {
        "user_id": "new_tech_partner",
        "request_type": "找队友",
        "text": "前端工程师，5年React经验，熟悉现代前端技术栈。有创业想法，希望做一个面向程序员的工具产品。寻找后端技术合伙人和产品合伙人，一起打造有价值的产品。"
    }
    
    print(f"新用户: {new_user['user_id']}")
    print(f"描述: {new_user['text'][:50]}...")
    
    matches = matching_system.add_new_user_and_find_matches(new_user, top_k=3)
    print("匹配结果:")
    for match_user_id, similarity in matches:
        print(f"  📍 {match_user_id}: 相似度 {similarity:.3f}")
    
    # 7. 系统分析报告
    print("\n步骤5: 系统分析报告")
    
    for request_type in ["找队友", "找对象"]:
        analysis = matching_system.get_similarity_analysis(request_type)
        print(f"\n📊 {request_type} 用户分析:")
        print(f"  用户总数: {analysis['total_users']}")
        print(f"  平均相似度: {analysis['average_similarity']:.3f}")
        print(f"  高相似度配对: {analysis['high_similarity_pairs']} 对")
        print(f"  中等相似度配对: {analysis['medium_similarity_pairs']} 对")
        print(f"  低相似度配对: {analysis['low_similarity_pairs']} 对")

def production_usage_example():
    """生产环境使用示例"""
    
    print("\n" + "="*60)
    print("💼 生产环境使用示例")
    print("="*60)
    
    # 在实际生产环境中的使用方式
    print("""
在你的实际项目中，可以这样使用：

1. 首次部署：
```python
# 从数据库获取现有用户
users_from_db = get_all_users_from_database()

# 训练模型
system = ProductionMatchingSystem()
system.train_from_existing_users(users_from_db)
system.process_all_users(users_from_db)
```

2. 日常运行：
```python
# 启动时加载预训练模型
system = ProductionMatchingSystem()
system.load_trained_model()

# 为用户查找匹配
matches = system.find_matches_for_user("user_123", top_k=10)
```

3. 新用户注册：
```python
# 新用户注册时
new_user_data = {
    "user_id": request.json['user_id'],
    "request_type": request.json['type'], 
    "text": request.json['description']
}

matches = system.add_new_user_and_find_matches(new_user_data)
```

4. 定期更新：
```python
# 每周重新训练模型（可以设置定时任务）
def weekly_model_update():
    all_users = get_all_users_from_database()
    system.train_from_existing_users(all_users)
    system.process_all_users(all_users)
```

这样就能在你的生产环境中实现基于主题发现的智能匹配！
""")

if __name__ == "__main__":
    demonstration_with_real_data()
    production_usage_example() 