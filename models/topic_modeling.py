#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import numpy as np
import jieba
import re
from typing import Dict, List, Tuple, Set, Any
from dataclasses import dataclass
from sklearn.feature_extraction.text import TfidfVectorizer
from gensim import corpora, models
from gensim.parsing.preprocessing import STOPWORDS
from config import TopicModelingConfig
from models.tag_pool import TagPool, TagCategory

@dataclass
class TopicResult:
    """主题建模结果"""
    topics: List[Tuple[int, float]]  # [(topic_id, weight), ...]
    extracted_tags: Dict[str, float]  # {tag: confidence, ...}
    topic_keywords: Dict[int, List[Tuple[str, float]]]  # {topic_id: [(word, weight), ...]}
    text_vector: List[float]  # 文本向量表示

class ChineseTextPreprocessor:
    """中文文本预处理器"""
    
    def __init__(self):
        # 中文停用词（减少停用词数量，避免过度过滤）
        self.stopwords = set([
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个',
            '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好',
            '自己', '这', '那', '现在', '可以', '但是', '如果',
            '他', '她', '它', '我们', '他们', '什么', '怎么', '为什么'
        ])
        
        # 只保留常见的英文停用词
        common_english_stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        self.stopwords.update(common_english_stopwords)
    
    def clean_text(self, text: str) -> str:
        """清理文本"""
        if not text:
            return ""
        
        # 移除特殊字符，保留中文、英文、数字和空格
        text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s+\-/]', ' ', text)
        # 移除多余空格
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def tokenize(self, text: str) -> List[str]:
        """分词"""
        text = self.clean_text(text)
        if not text
            return []
        
        print(f"分词前文本: {text[:100]}...")
        
        # 中文分词
        tokens = []
        for word in jieba.cut(text):
            word = word.strip()
            if (len(word) >= 1 and  # 长度大于等于1（放宽条件）
                word not in self.stopwords and  # 不是停用词
                not word.isdigit() and  # 不是纯数字
                word.isalpha() or len(word) > 1):  # 是字母或长度大于1
                tokens.append(word)
        
        print(f"分词结果: {tokens[:20]}...")
        return tokens
    
    def preprocess_documents(self, texts: List[str]) -> List[List[str]]:
        """预处理文档集合"""
        processed = []
        for i, text in enumerate(texts):
            tokens = self.tokenize(text)
            print(f"文档 {i+1} 分词得到 {len(tokens)} 个词汇")
            processed.append(tokens)
        return processed

class LDATopicModel:
    """LDA主题建模器"""
    
    def __init__(self, config: TopicModelingConfig = None):
        self.config = config or TopicModelingConfig()
        # 降低主题数量，因为我们只有2个文档
        self.config.num_topics = min(self.config.num_topics, 5)
        self.preprocessor = ChineseTextPreprocessor()
        
        self.dictionary = None
        self.corpus = None
        self.lda_model = None
        self.tag_pool = TagPool()
        
        # 标签到主题的映射
        self.tag_topic_mapping = {}
        
    def train(self, documents: List[str]) -> None:
        """训练LDA模型"""
        print(f"开始训练LDA模型，文档数量: {len(documents)}")
        
        # 预处理文档
        processed_docs = self.preprocessor.preprocess_documents(documents)
        
        # 检查是否有有效的文档
        valid_docs = [doc for doc in processed_docs if len(doc) > 0]
        if not valid_docs:
            print("警告: 没有有效的文档可以训练LDA模型")
            # 创建一个简单的假数据来避免错误
            valid_docs = [['创业', 'AI', '技术'], ['合作', '产品', '开发']]
        
        print(f"有效文档数量: {len(valid_docs)}")
        
        # 创建词典
        self.dictionary = corpora.Dictionary(valid_docs)
        
        # 放宽过滤条件
        self.dictionary.filter_extremes(
            no_below=1,  # 降低到1
            no_above=0.9,  # 提高到0.9
            keep_n=2000   # 增加到2000
        )
        
        print(f"过滤后词典大小: {len(self.dictionary)}")
        
        if len(self.dictionary) == 0:
            print("词典为空，创建最小词典")
            # 手动创建一些基本词汇
            basic_words = [['AI', '人工智能', '创业', '技术', '产品', '合作', '开发']]
            self.dictionary = corpora.Dictionary(basic_words)
        
        # 创建语料库
        self.corpus = [self.dictionary.doc2bow(doc) for doc in valid_docs]
        
        print(f"语料库大小: {len(self.corpus)}")
        print(f"词典最终大小: {len(self.dictionary)}")
        
        # 调整LDA参数以适应小数据集
        num_topics = min(self.config.num_topics, len(self.dictionary), 3)
        
        # 训练LDA模型
        self.lda_model = models.LdaModel(
            corpus=self.corpus,
            id2word=self.dictionary,
            num_topics=num_topics,
            random_state=42,
            passes=5,  # 减少训练轮数
            iterations=20,  # 减少迭代次数
            alpha='auto',
            eta='auto'
        )
        
        print(f"LDA模型训练完成，主题数量: {num_topics}")
        
        # 建立标签到主题的映射
        self._build_tag_topic_mapping()
    
    def _build_tag_topic_mapping(self):
        """建立标签到主题的映射关系"""
        if not self.lda_model:
            return
        
        print("建立标签到主题的映射关系...")
        
        # 获取所有标签
        all_tags = self.tag_pool.get_tag_list()
        
        # 为每个标签找到最相关的主题
        mapped_count = 0
        for tag in all_tags:
            # 将标签作为文档进行预处理
            tag_tokens = self.preprocessor.tokenize(tag)
            if not tag_tokens:
                continue
                
            # 转换为BOW
            tag_bow = self.dictionary.doc2bow(tag_tokens)
            if not tag_bow:
                continue
            
            # 获取主题分布
            topic_dist = self.lda_model.get_document_topics(tag_bow, minimum_probability=0)
            
            # 找到最相关的主题
            if topic_dist:
                best_topics = sorted(topic_dist, key=lambda x: x[1], reverse=True)[:3]
                self.tag_topic_mapping[tag] = best_topics
                mapped_count += 1
        
        print(f"完成标签映射，映射了 {mapped_count} 个标签")
    
    def extract_topics_and_tags(self, text: str, request_type: str = "all") -> TopicResult:
        """从文本中提取主题和标签"""
        if not self.lda_model:
            raise ValueError("模型尚未训练，请先调用train()方法")
        
        # 预处理文本
        tokens = self.preprocessor.tokenize(text)
        if not tokens:
            return TopicResult(
                topics=[],
                extracted_tags={},
                topic_keywords={},
                text_vector=[0.0] * self.lda_model.num_topics
            )
        
        # 转换为BOW
        bow = self.dictionary.doc2bow(tokens)
        
        # 获取主题分布
        topic_distribution = self.lda_model.get_document_topics(
            bow, 
            minimum_probability=0.01  # 降低阈值
        )
        
        # 获取主题关键词
        topic_keywords = {}
        for topic_id, _ in topic_distribution:
            words = self.lda_model.show_topic(topic_id, topn=10)
            topic_keywords[topic_id] = words
        
        # 基于主题分布提取标签
        extracted_tags = self._extract_tags_from_topics(
            topic_distribution, 
            request_type
        )
        
        # 如果没有提取到标签，使用简单的关键词匹配
        if not extracted_tags:
            extracted_tags = self._extract_tags_by_keywords(text, request_type)
        
        # 生成文本向量（主题概率分布）
        text_vector = [0.0] * self.lda_model.num_topics
        for topic_id, prob in topic_distribution:
            text_vector[topic_id] = prob
        
        return TopicResult(
            topics=topic_distribution,
            extracted_tags=extracted_tags,
            topic_keywords=topic_keywords,
            text_vector=text_vector
        )
    
    def _extract_tags_by_keywords(self, text: str, request_type: str) -> Dict[str, float]:
        """基于关键词匹配提取标签"""
        text_lower = text.lower()
        extracted_tags = {}
        
        # 获取相关标签池
        relevant_tags = self.tag_pool.get_tag_list(request_type)
        
        for tag in relevant_tags:
            tag_lower = tag.lower()
            # 简单的关键词匹配
            if tag_lower in text_lower or any(word in text_lower for word in tag_lower.split()):
                extracted_tags[tag] = 0.5  # 给一个中等的置信度
        
        # 手动添加一些基于内容的标签
        if 'ai' in text_lower or '人工智能' in text_lower:
            extracted_tags['人工智能'] = 0.8
        if '创业' in text_lower:
            extracted_tags['创业者'] = 0.8
        if '技术' in text_lower:
            extracted_tags['技术型'] = 0.7
        if '产品' in text_lower:
            extracted_tags['产品管理'] = 0.7
        
        return extracted_tags
    
    def _extract_tags_from_topics(self, topic_distribution: List[Tuple[int, float]], 
                                 request_type: str) -> Dict[str, float]:
        """基于主题分布提取标签"""
        extracted_tags = {}
        
        # 获取相关标签池
        relevant_tags = self.tag_pool.get_tag_list(request_type)
        
        for tag in relevant_tags:
            if tag not in self.tag_topic_mapping:
                continue
            
            # 计算标签的置信度
            confidence = 0.0
            for tag_topic_id, tag_topic_weight in self.tag_topic_mapping[tag]:
                # 找到文档中对应主题的权重
                doc_topic_weight = 0.0
                for doc_topic_id, doc_topic_prob in topic_distribution:
                    if doc_topic_id == tag_topic_id:
                        doc_topic_weight = doc_topic_prob
                        break
                
                confidence += tag_topic_weight * doc_topic_weight
            
            # 降低置信度阈值
            if confidence >= 0.1:
                extracted_tags[tag] = confidence
        
        return extracted_tags
    
    def get_topic_info(self) -> Dict[int, Dict[str, Any]]:
        """获取主题信息"""
        if not self.lda_model:
            return {}
        
        topic_info = {}
        for topic_id in range(self.lda_model.num_topics):
            words = self.lda_model.show_topic(topic_id, topn=10)
            topic_info[topic_id] = {
                'keywords': words,
                'description': ', '.join([word for word, _ in words[:5]])
            }
        
        return topic_info
    
    def save_model(self, model_path: str) -> None:
        """保存模型"""
        if self.lda_model:
            self.lda_model.save(f"{model_path}_lda")
            self.dictionary.save(f"{model_path}_dict")
            
            # 保存标签映射，处理float32类型
            serializable_mapping = {}
            for tag, topics in self.tag_topic_mapping.items():
                serializable_mapping[tag] = [(int(tid), float(weight)) for tid, weight in topics]
            
            with open(f"{model_path}_tag_mapping.json", 'w', encoding='utf-8') as f:
                json.dump(serializable_mapping, f, ensure_ascii=False, indent=2)
            
            print(f"模型已保存到: {model_path}")
    
    def load_model(self, model_path: str) -> None:
        """加载模型"""
        try:
            self.lda_model = models.LdaModel.load(f"{model_path}_lda")
            self.dictionary = corpora.Dictionary.load(f"{model_path}_dict")
            
            # 加载标签映射
            with open(f"{model_path}_tag_mapping.json", 'r', encoding='utf-8') as f:
                self.tag_topic_mapping = json.load(f)
            
            print(f"模型已从 {model_path} 加载")
        except Exception as e:
            print(f"加载模型失败: {e}")
            raise

# 全局实例
topic_model = LDATopicModel() 