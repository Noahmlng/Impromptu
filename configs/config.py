#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv

@dataclass
class KimiAPIConfig:
    """Kimi API configuration"""
    
    base_url: str = "https://api.moonshot.cn/v1"
    api_key: Optional[str] = None
    model: str = "moonshot-v1-8k"
    temperature: float = 0.7
    max_tokens: int = 2000
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    
    def __post_init__(self):
        if self.api_key is None:
            # 获取项目根目录路径
            project_root = os.path.join(os.path.dirname(__file__), '..')
            # 加载根目录的环境变量文件
            load_dotenv(os.path.join(project_root, '.env.local'))
            load_dotenv(os.path.join(project_root, '.env'))
            self.api_key = os.getenv('KIMI_API_KEY')
    
    @property
    def headers(self):
        if not self.api_key:
            raise ValueError("API key is required")
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    @property
    def chat_endpoint(self):
        return f"{self.base_url}/chat/completions"

@dataclass 
class AnalysisConfig:
    """Analysis configuration with scoring weights"""
    
    personality_weight: float = 0.25
    interests_weight: float = 0.20
    values_weight: float = 0.20
    lifestyle_weight: float = 0.15
    professional_weight: float = 0.15
    request_matching_weight: float = 0.05  # 诉求匹配度权重
    min_score: int = 0
    max_score: int = 10

@dataclass
class TopicModelingConfig:
    """主题建模配置"""
    
    # LDA参数
    num_topics: int = 20
    passes: int = 10
    iterations: int = 50
    alpha: str = 'auto'
    eta: str = 'auto'
    
    # 文本预处理
    min_word_count: int = 2
    max_word_count: int = 1000
    max_doc_frequency: float = 0.8
    min_doc_frequency: int = 2
    
    # 标签匹配
    topic_threshold: float = 0.1
    tag_confidence_threshold: float = 0.3

@dataclass
class VectorMatchingConfig:
    """向量匹配配置"""
    
    # Faiss索引类型
    index_type: str = "IndexFlatIP"  # Inner Product for cosine similarity
    
    # 相似度计算
    similarity_threshold: float = 0.6
    top_k_matches: int = 10
    
    # 向量维度
    vector_dimension: int = 100
    
    # 匹配权重
    user_profile_weight: float = 0.6
    user_request_weight: float = 0.4

class ConfigManager:
    """Simple configuration manager"""
    
    def __init__(self):
        self.api_config = KimiAPIConfig()
        self.analysis_config = AnalysisConfig()
        self.topic_config = TopicModelingConfig()
        self.vector_config = VectorMatchingConfig()
    
    def validate(self):
        return bool(self.api_config.api_key)

# Global default config
default_config = ConfigManager() 