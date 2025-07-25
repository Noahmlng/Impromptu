#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
基于主题发现和向量相似度的用户匹配系统

工作流程:
1. 文本预处理和特征提取
2. 训练主题模型（LDA/Doc2Vec/TF-IDF）
3. 将用户文本转换为向量表示
4. 计算用户间的cosine相似度
5. 基于相似度进行匹配推荐
"""

import json
import numpy as np
import jieba
import re
import pickle
import os
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import LatentDirichletAllocation
from gensim import corpora, models
from gensim.models import Doc2Vec
from gensim.models.doc2vec import TaggedDocument
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class UserVector:
    """用户向量表示"""
    user_id: str
    request_type: str
    text: str
    vector: np.ndarray
    topics: Optional[List[Tuple[int, float]]] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    
class ChineseTextProcessor:
    """中文文本预处理器"""
    
    def __init__(self):
        self.stopwords = set([
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个',
            '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好',
            '自己', '这', '那', '现在', '可以', '但是', '如果', '他', '她', '它', '我们',
            '他们', '什么', '怎么', '为什么', '那个', '这个', '还是', '或者', '因为',
            '所以', '虽然', '但是', '然后', '开始', '结束', '时候', '地方', '问题',
            '方法', '可能', '应该', '需要', '希望', '觉得', '认为', '知道', '看到'
        ])
    
    def clean_text(self, text: str) -> str:
        """清理文本"""
        if not text:
            return ""
        
        # 移除特殊字符，保留中文、英文、数字
        text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s]', ' ', text)
        # 移除多余空格
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def tokenize(self, text: str) -> List[str]:
        """分词并过滤停用词"""
        text = self.clean_text(text)
        if not text:
            return []
        
        tokens = []
        for word in jieba.cut(text):
            word = word.strip()
            if (len(word) >= 2 and 
                word not in self.stopwords and 
                not word.isdigit() and
                not word.isspace()):
                tokens.append(word)
        
        return tokens
    
    def preprocess_documents(self, texts: List[str]) -> List[List[str]]:
        """批量预处理文档"""
        return [self.tokenize(text) for text in texts]

class TopicVectorizer:
    """主题向量化器 - 支持多种向量化方法"""
    
    def __init__(self, method='tfidf', **kwargs):
        """
        初始化向量化器
        
        Args:
            method: 向量化方法 ('tfidf', 'lda', 'doc2vec')
            **kwargs: 各方法的参数
        """
        self.method = method
        self.text_processor = ChineseTextProcessor()
        self.is_trained = False
        
        # 初始化模型
        if method == 'tfidf':
            self.model = TfidfVectorizer(
                tokenizer=self.text_processor.tokenize,
                lowercase=False,
                max_features=kwargs.get('max_features', 1000),
                min_df=kwargs.get('min_df', 2),
                max_df=kwargs.get('max_df', 0.8)
            )
        elif method == 'lda':
            self.n_topics = kwargs.get('n_topics', 20)
            self.lda_model = LatentDirichletAllocation(
                n_components=self.n_topics,
                random_state=42,
                max_iter=kwargs.get('max_iter', 10)
            )
            self.vectorizer = TfidfVectorizer(
                tokenizer=self.text_processor.tokenize,
                lowercase=False,
                max_features=kwargs.get('max_features', 1000)
            )
        elif method == 'doc2vec':
            self.vector_size = kwargs.get('vector_size', 100)
            self.model = Doc2Vec(
                vector_size=self.vector_size,
                window=kwargs.get('window', 5),
                min_count=kwargs.get('min_count', 2),
                workers=kwargs.get('workers', 4),
                epochs=kwargs.get('epochs', 10)
            )
        else:
            raise ValueError(f"不支持的向量化方法: {method}")
    
    def train(self, texts: List[str]) -> None:
        """训练向量化模型"""
        logger.info(f"开始训练{self.method}模型，文档数量: {len(texts)}")
        
        if self.method == 'tfidf':
            self.model.fit(texts)
            
        elif self.method == 'lda':
            # 先用TF-IDF处理
            tfidf_matrix = self.vectorizer.fit_transform(texts)
            # 训练LDA
            self.lda_model.fit(tfidf_matrix)
            
        elif self.method == 'doc2vec':
            # 准备训练数据
            processed_docs = self.text_processor.preprocess_documents(texts)
            tagged_docs = [
                TaggedDocument(words=doc, tags=[f'doc_{i}']) 
                for i, doc in enumerate(processed_docs)
            ]
            
            # 构建词汇表
            self.model.build_vocab(tagged_docs)
            # 训练模型
            self.model.train(tagged_docs, total_examples=self.model.corpus_count, epochs=self.model.epochs)
        
        self.is_trained = True
        logger.info(f"{self.method}模型训练完成")
    
    def transform(self, texts: List[str]) -> np.ndarray:
        """将文本转换为向量"""
        if not self.is_trained:
            raise ValueError("模型尚未训练，请先调用train()方法")
        
        if self.method == 'tfidf':
            return self.model.transform(texts).toarray()
            
        elif self.method == 'lda':
            tfidf_matrix = self.vectorizer.transform(texts)
            return self.lda_model.transform(tfidf_matrix)
            
        elif self.method == 'doc2vec':
            vectors = []
            for text in texts:
                tokens = self.text_processor.tokenize(text)
                if tokens:
                    vector = self.model.infer_vector(tokens)
                    vectors.append(vector)
                else:
                    # 如果没有有效tokens，返回零向量
                    vectors.append(np.zeros(self.vector_size))
            return np.array(vectors)
    
    def save_model(self, model_path: str) -> None:
        """保存模型"""
        if not self.is_trained:
            raise ValueError("模型尚未训练")
        
        model_data = {
            'method': self.method,
            'is_trained': self.is_trained
        }
        
        if self.method == 'tfidf':
            with open(f"{model_path}_tfidf.pkl", 'wb') as f:
                pickle.dump(self.model, f)
                
        elif self.method == 'lda':
            with open(f"{model_path}_vectorizer.pkl", 'wb') as f:
                pickle.dump(self.vectorizer, f)
            with open(f"{model_path}_lda.pkl", 'wb') as f:
                pickle.dump(self.lda_model, f)
            model_data['n_topics'] = self.n_topics
            
        elif self.method == 'doc2vec':
            self.model.save(f"{model_path}_doc2vec.model")
            model_data['vector_size'] = self.vector_size
        
        # 保存元数据
        with open(f"{model_path}_metadata.json", 'w', encoding='utf-8') as f:
            json.dump(model_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"模型已保存到: {model_path}")
    
    def load_model(self, model_path: str) -> None:
        """加载模型"""
        # 加载元数据
        with open(f"{model_path}_metadata.json", 'r', encoding='utf-8') as f:
            model_data = json.load(f)
        
        self.method = model_data['method']
        self.is_trained = model_data['is_trained']
        
        if self.method == 'tfidf':
            with open(f"{model_path}_tfidf.pkl", 'rb') as f:
                self.model = pickle.load(f)
                
        elif self.method == 'lda':
            with open(f"{model_path}_vectorizer.pkl", 'rb') as f:
                self.vectorizer = pickle.load(f)
            with open(f"{model_path}_lda.pkl", 'rb') as f:
                self.lda_model = pickle.load(f)
            self.n_topics = model_data['n_topics']
            
        elif self.method == 'doc2vec':
            self.model = Doc2Vec.load(f"{model_path}_doc2vec.model")
            self.vector_size = model_data['vector_size']
        
        logger.info(f"模型已从 {model_path} 加载")

class VectorUserMatcher:
    """基于向量相似度的用户匹配器"""
    
    def __init__(self, vectorizer: TopicVectorizer):
        self.vectorizer = vectorizer
        self.user_vectors: Dict[str, UserVector] = {}
        self.users = self.user_vectors  # 为了兼容性添加的别名
        self.vectors_matrix: Optional[np.ndarray] = None
        self.user_ids: List[str] = []
    
    def add_users(self, users_data: List[Dict[str, Any]]) -> None:
        """添加用户并计算向量"""
        texts = [user['text'] for user in users_data]
        
        # 批量转换为向量
        vectors = self.vectorizer.transform(texts)
        
        # 存储用户向量
        for i, user in enumerate(users_data):
            user_vector = UserVector(
                user_id=user['user_id'],
                request_type=user['request_type'],
                text=user['text'],
                vector=vectors[i]
            )
            self.user_vectors[user['user_id']] = user_vector
        
        # 更新向量矩阵
        self._update_vectors_matrix()
        
        logger.info(f"已添加 {len(users_data)} 个用户")
    
    def _update_vectors_matrix(self) -> None:
        """更新向量矩阵用于批量计算相似度"""
        if not self.user_vectors:
            return
        
        self.user_ids = list(self.user_vectors.keys())
        self.vectors_matrix = np.vstack([
            self.user_vectors[user_id].vector 
            for user_id in self.user_ids
        ])
    
    def find_similar_users(self, target_user_id: str, 
                          request_type: str = None,
                          top_k: int = 10,
                          min_similarity: float = 0.1) -> List[Tuple[str, float]]:
        """为目标用户找到相似的用户"""
        
        if target_user_id not in self.user_vectors:
            raise ValueError(f"用户 {target_user_id} 不存在")
        
        target_vector = self.user_vectors[target_user_id]
        target_request_type = target_vector.request_type
        
        # 过滤相同请求类型的用户
        candidate_indices = []
        candidate_ids = []
        
        for i, user_id in enumerate(self.user_ids):
            if (user_id != target_user_id and 
                self.user_vectors[user_id].request_type == target_request_type):
                candidate_indices.append(i)
                candidate_ids.append(user_id)
        
        if not candidate_indices:
            return []
        
        # 计算相似度
        target_vec = target_vector.vector.reshape(1, -1)
        candidate_vectors = self.vectors_matrix[candidate_indices]
        
        similarities = cosine_similarity(target_vec, candidate_vectors).flatten()
        
        # 筛选和排序
        results = []
        for i, sim in enumerate(similarities):
            if sim >= min_similarity:
                results.append((candidate_ids[i], float(sim)))
        
        # 按相似度排序
        results.sort(key=lambda x: x[1], reverse=True)
        
        return results[:top_k]
    
    def get_similarity_matrix(self, request_type: str = None) -> Tuple[np.ndarray, List[str]]:
        """获取用户间的相似度矩阵"""
        # 筛选指定类型的用户
        if request_type:
            filtered_ids = [
                user_id for user_id in self.user_ids 
                if self.user_vectors[user_id].request_type == request_type
            ]
            filtered_indices = [self.user_ids.index(uid) for uid in filtered_ids]
            filtered_vectors = self.vectors_matrix[filtered_indices]
        else:
            filtered_ids = self.user_ids
            filtered_vectors = self.vectors_matrix
        
        # 计算相似度矩阵
        similarity_matrix = cosine_similarity(filtered_vectors)
        
        return similarity_matrix, filtered_ids
    
    def add_user(self, user_id: str, text: str, request_type: str = "general", tags: List[str] = None, metadata: Dict = None) -> None:
        """添加单个用户"""
        # 转换为向量
        vector = self.vectorizer.transform([text])[0]
        
        # 创建用户向量对象
        user_vector = UserVector(
            user_id=user_id,
            request_type=request_type,
            text=text,
            vector=vector,
            tags=tags or [],
            metadata=metadata or {}
        )
        
        self.user_vectors[user_id] = user_vector
        
        # 更新向量矩阵
        self._update_vectors_matrix()
    
    def build_indices(self) -> None:
        """构建索引，更新向量矩阵"""
        self._update_vectors_matrix()
    
    def save_vectors(self, filepath: str) -> None:
        """保存用户向量到文件"""
        import pickle
        data = {
            'user_vectors': self.user_vectors,
            'user_ids': self.user_ids
        }
        with open(filepath, 'wb') as f:
            pickle.dump(data, f)
    
    def load_vectors(self, filepath: str) -> None:
        """从文件加载用户向量"""
        import pickle
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
        
        self.user_vectors = data['user_vectors']
        self.users = self.user_vectors  # 更新别名
        self.user_ids = data['user_ids']
        self._update_vectors_matrix()
    
    def _calculate_detailed_similarity(self, user_a_vector: UserVector, user_b_vector: UserVector):
        """计算详细的用户相似度"""
        from dataclasses import dataclass
        
        @dataclass
        class SimilarityResult:
            overall_similarity: float
            vector_similarity: float
            profile_similarity: float
            request_similarity: float
            mutual_tags: List[str]
            overall_recommendation: str
            vector_explanation: str
        
        # 计算向量相似度
        vector_sim = cosine_similarity(
            user_a_vector.vector.reshape(1, -1),
            user_b_vector.vector.reshape(1, -1)
        )[0][0]
        
        # 计算标签相似度
        tags_a = set(user_a_vector.tags)
        tags_b = set(user_b_vector.tags)
        mutual_tags = list(tags_a.intersection(tags_b))
        
        if tags_a and tags_b:
            tag_similarity = len(mutual_tags) / len(tags_a.union(tags_b))
        else:
            tag_similarity = 0.0
        
        # 计算诉求相似度（基于文本）
        if user_a_vector.text and user_b_vector.text:
            request_sim = cosine_similarity(
                self.vectorizer.transform([user_a_vector.text]),
                self.vectorizer.transform([user_b_vector.text])
            )[0][0]
        else:
            request_sim = vector_sim
        
        # 综合评分
        overall_sim = (vector_sim * 0.5 + tag_similarity * 0.3 + request_sim * 0.2)
        
        # 生成推荐和解释
        if overall_sim > 0.7:
            recommendation = "强烈推荐"
            explanation = "用户档案高度相似，非常适合匹配"
        elif overall_sim > 0.5:
            recommendation = "推荐"
            explanation = "用户档案较为相似，值得进一步了解"
        elif overall_sim > 0.3:
            recommendation = "一般"
            explanation = "有一定相似性，可以考虑"
        else:
            recommendation = "不推荐"
            explanation = "相似度较低，匹配度不高"
        
        return SimilarityResult(
            overall_similarity=overall_sim,
            vector_similarity=vector_sim,
            profile_similarity=tag_similarity,
            request_similarity=request_sim,
            mutual_tags=mutual_tags,
            overall_recommendation=recommendation,
            vector_explanation=explanation
        )
    
    def save_user_vectors(self, filepath: str) -> None:
        """保存用户向量数据"""
        save_data = {}
        for user_id, user_vector in self.user_vectors.items():
            save_data[user_id] = {
                'user_id': user_vector.user_id,
                'request_type': user_vector.request_type,
                'text': user_vector.text,
                'vector': user_vector.vector.tolist(),
                'topics': user_vector.topics
            }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"用户向量已保存到: {filepath}")
    
    def load_user_vectors(self, filepath: str) -> None:
        """加载用户向量数据"""
        with open(filepath, 'r', encoding='utf-8') as f:
            save_data = json.load(f)
        
        self.user_vectors = {}
        for user_id, data in save_data.items():
            user_vector = UserVector(
                user_id=data['user_id'],
                request_type=data['request_type'],
                text=data['text'],
                vector=np.array(data['vector']),
                topics=data['topics']
            )
            self.user_vectors[user_id] = user_vector
        
        self._update_vectors_matrix()
        logger.info(f"已从 {filepath} 加载 {len(self.user_vectors)} 个用户向量")

def demonstration_training_pipeline():
    """演示完整的训练和匹配流程"""
    
    print("🚀 基于主题发现的用户匹配系统演示")
    print("=" * 60)
    
    # 模拟训练数据
    training_texts = [
        "我是一个程序员，喜欢编程和技术，平时爱看科技新闻",
        "产品经理，关注用户体验和商业模式，喜欢分析市场",
        "设计师，热爱创意和美学，经常关注设计趋势",
        "创业者，对商业很感兴趣，希望找到技术合伙人",
        "投资人，关注早期项目，看好AI和区块链",
        "28岁女生，喜欢旅行和摄影，希望找到志同道合的伴侣",
        "内向程序员，喜欢读书和音乐，想找个理解我的人",
        "外向销售，热爱社交和运动，希望找个开朗的女生",
        "艺术生，热爱画画和文学，想找有艺术细胞的人",
        "医生，工作忙碌但很充实，希望找个体贴的伴侣"
    ]
    
    # 模拟用户数据
    users_data = [
        {
            "user_id": "tech_001",
            "request_type": "找队友",
            "text": "5年经验的全栈工程师，擅长Python和React，想找产品合伙人一起做SaaS"
        },
        {
            "user_id": "biz_001", 
            "request_type": "找队友",
            "text": "有过两次创业经验的产品经理，熟悉B端市场，寻找技术合伙人"
        },
        {
            "user_id": "love_001",
            "request_type": "找对象",
            "text": "26岁程序员，性格内向，喜欢看书和听音乐，希望找个温柔的女生"
        },
        {
            "user_id": "love_002",
            "request_type": "找对象", 
            "text": "25岁设计师，热爱旅行和摄影，外向开朗，想找个有共同爱好的男生"
        },
        {
            "user_id": "love_003",
            "request_type": "找对象",
            "text": "29岁医生，工作稳定，喜欢运动和美食，希望找个理解我工作的人"
        }
    ]
    
    # 测试不同的向量化方法
    methods = ['tfidf', 'lda', 'doc2vec']
    
    for method in methods:
        print(f"\n📊 测试 {method.upper()} 方法")
        print("-" * 40)
        
        try:
            # 1. 训练向量化模型
            if method == 'lda':
                vectorizer = TopicVectorizer(method, n_topics=5, max_features=500)
            else:
                vectorizer = TopicVectorizer(method)
            
            print(f"1. 训练{method}模型...")
            vectorizer.train(training_texts)
            
            # 2. 创建匹配器并添加用户
            matcher = VectorUserMatcher(vectorizer)
            print("2. 添加用户并计算向量...")
            matcher.add_users(users_data)
            
            # 3. 进行相似度匹配
            print("3. 查找相似用户:")
            for user_id in ["tech_001", "love_001"]:
                similar_users = matcher.find_similar_users(user_id, top_k=3)
                print(f"\n与 {user_id} 最相似的用户:")
                for sim_user_id, similarity in similar_users:
                    print(f"  • {sim_user_id}: {similarity:.3f}")
        
        except Exception as e:
            print(f"❌ {method} 方法测试失败: {e}")
    
    print(f"\n🎯 推荐使用方案:")
    print("• TF-IDF: 简单快速，适合小规模数据")
    print("• LDA: 主题建模，适合发现潜在主题")  
    print("• Doc2Vec: 深度语义理解，适合复杂文本")

if __name__ == "__main__":
    demonstration_training_pipeline() 