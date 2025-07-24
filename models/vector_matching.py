#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import faiss
import json
import os
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from config import VectorMatchingConfig
from models.tag_pool import TagPool
from models.topic_modeling import TopicResult

@dataclass
class UserVector:
    """用户向量表示"""
    user_id: str
    profile_vector: np.ndarray  # 用户档案向量
    request_vector: np.ndarray  # 诉求向量
    combined_vector: np.ndarray  # 组合向量
    request_type: str  # 诉求类型
    tags: Dict[str, float]  # 提取的标签
    metadata: Dict[str, Any]  # 元数据

@dataclass 
class MatchResult:
    """匹配结果"""
    user_a_id: str
    user_b_id: str
    similarity_score: float
    profile_similarity: float
    request_similarity: float
    mutual_tags: List[str]  # 共同标签
    complementary_tags: List[str]  # 互补标签
    explanation: str

class TagVectorizer:
    """标签向量化器"""
    
    def __init__(self, tag_pool: TagPool):
        self.tag_pool = tag_pool
        self.tag_to_index = {}
        self.index_to_tag = {}
        self._build_tag_mapping()
    
    def _build_tag_mapping(self):
        """建立标签到索引的映射"""
        # 使用全部标签列表建立映射
        all_tags = self.tag_pool.get_tag_list("all")
        for i, tag in enumerate(all_tags):
            self.tag_to_index[tag] = i
            self.index_to_tag[i] = tag
    
    def tags_to_vector(self, tags: Dict[str, float], 
                      request_type: str = "all") -> np.ndarray:
        """将标签字典转换为向量"""
        # 总是使用全部标签列表以确保向量维度一致
        all_tags = self.tag_pool.get_tag_list("all")
        vector_size = len(all_tags)
        vector = np.zeros(vector_size)
        
        # 建立临时索引映射
        temp_tag_to_index = {tag: i for i, tag in enumerate(all_tags)}
        
        for tag, confidence in tags.items():
            if tag in temp_tag_to_index:
                vector[temp_tag_to_index[tag]] = confidence
        
        return vector
    
    def vector_to_tags(self, vector: np.ndarray, 
                      request_type: str = "all", 
                      threshold: float = 0.1) -> Dict[str, float]:
        """将向量转换为标签字典"""
        # 总是使用全部标签列表以确保向量维度一致
        all_tags = self.tag_pool.get_tag_list("all")
        tags = {}
        
        for i, confidence in enumerate(vector):
            if i < len(all_tags) and confidence > threshold:
                tags[all_tags[i]] = float(confidence)
        
        return tags

class FaissVectorMatcher:
    """基于Faiss的向量匹配器"""
    
    def __init__(self, config: VectorMatchingConfig = None):
        self.config = config or VectorMatchingConfig()
        self.tag_vectorizer = TagVectorizer(TagPool())
        
        # Faiss索引
        self.profile_index = None
        self.request_index = None
        self.combined_index = None
        
        # 用户数据
        self.users: Dict[str, UserVector] = {}
        self.user_ids: List[str] = []
        
    def _create_faiss_index(self, dimension: int) -> faiss.Index:
        """创建Faiss索引"""
        if self.config.index_type == "IndexFlatIP":
            # 内积索引（适用于余弦相似度）
            index = faiss.IndexFlatIP(dimension)
        elif self.config.index_type == "IndexFlatL2":
            # L2距离索引
            index = faiss.IndexFlatL2(dimension)
        else:
            # 默认使用内积索引
            index = faiss.IndexFlatIP(dimension)
        
        return index
    
    def add_user(self, user_id: str, profile_tags: Dict[str, float], 
                request_tags: Dict[str, float], request_type: str,
                metadata: Dict[str, Any] = None) -> None:
        """添加用户向量"""
        
        # 转换标签为向量
        profile_vector = self.tag_vectorizer.tags_to_vector(profile_tags, "all")
        request_vector = self.tag_vectorizer.tags_to_vector(request_tags, request_type)
        
        # 标准化向量
        profile_vector = self._normalize_vector(profile_vector)
        request_vector = self._normalize_vector(request_vector)
        
        # 组合向量（加权组合）
        # 需要确保两个向量维度一致
        if len(profile_vector) != len(request_vector):
            # 如果维度不一致，使用较短的长度
            min_len = min(len(profile_vector), len(request_vector))
            profile_vector = profile_vector[:min_len]
            request_vector = request_vector[:min_len]
        
        combined_vector = (self.config.user_profile_weight * profile_vector + 
                          self.config.user_request_weight * request_vector)
        combined_vector = self._normalize_vector(combined_vector)
        
        user_vector = UserVector(
            user_id=user_id,
            profile_vector=profile_vector,
            request_vector=request_vector,
            combined_vector=combined_vector,
            request_type=request_type,
            tags={**profile_tags, **request_tags},
            metadata=metadata or {}
        )
        
        self.users[user_id] = user_vector
        if user_id not in self.user_ids:
            self.user_ids.append(user_id)
    
    def _normalize_vector(self, vector: np.ndarray) -> np.ndarray:
        """向量标准化（L2范数）"""
        norm = np.linalg.norm(vector)
        if norm == 0:
            return vector
        return vector / norm
    
    def build_indices(self) -> None:
        """构建Faiss索引"""
        if not self.users:
            raise ValueError("没有用户数据，请先添加用户")
        
        print(f"构建Faiss索引，用户数量: {len(self.users)}")
        
        # 收集所有向量
        profile_vectors = []
        request_vectors = []
        combined_vectors = []
        
        for user_id in self.user_ids:
            user = self.users[user_id]
            profile_vectors.append(user.profile_vector)
            request_vectors.append(user.request_vector)
            combined_vectors.append(user.combined_vector)
        
        # 转换为numpy数组
        profile_matrix = np.array(profile_vectors, dtype=np.float32)
        request_matrix = np.array(request_vectors, dtype=np.float32)
        combined_matrix = np.array(combined_vectors, dtype=np.float32)
        
        print(f"向量维度 - Profile: {profile_matrix.shape}, Request: {request_matrix.shape}, Combined: {combined_matrix.shape}")
        
        # 创建索引
        self.profile_index = self._create_faiss_index(profile_matrix.shape[1])
        self.request_index = self._create_faiss_index(request_matrix.shape[1])
        self.combined_index = self._create_faiss_index(combined_matrix.shape[1])
        
        # 添加向量到索引
        self.profile_index.add(profile_matrix)
        self.request_index.add(request_matrix)
        self.combined_index.add(combined_matrix)
        
        print("Faiss索引构建完成")
    
    def find_matches(self, user_id: str, top_k: int = None) -> List[MatchResult]:
        """为指定用户找到匹配的用户"""
        if user_id not in self.users:
            raise ValueError(f"用户 {user_id} 不存在")
        
        if not self.combined_index:
            raise ValueError("索引尚未构建，请先调用build_indices()")
        
        top_k = top_k or self.config.top_k_matches
        user = self.users[user_id]
        
        # 使用组合向量进行搜索
        query_vector = user.combined_vector.reshape(1, -1).astype(np.float32)
        similarities, indices = self.combined_index.search(query_vector, top_k + 1)  # +1 因为包含自己
        
        matches = []
        for i, (similarity, index) in enumerate(zip(similarities[0], indices[0])):
            candidate_id = self.user_ids[index]
            
            # 跳过自己
            if candidate_id == user_id:
                continue
            
            candidate = self.users[candidate_id]
            
            # 计算详细相似度
            match_result = self._calculate_detailed_similarity(user, candidate, float(similarity))
            
            # 过滤低相似度匹配
            if match_result.similarity_score >= self.config.similarity_threshold:
                matches.append(match_result)
        
        return matches[:top_k]
    
    def _calculate_detailed_similarity(self, user_a: UserVector, user_b: UserVector, 
                                     combined_similarity: float) -> MatchResult:
        """计算详细的相似度信息"""
        
        # 计算档案相似度
        profile_similarity = float(np.dot(user_a.profile_vector, user_b.profile_vector))
        
        # 计算诉求相似度
        request_similarity = float(np.dot(user_a.request_vector, user_b.request_vector))
        
        # 找到共同标签
        user_a_tags = set(user_a.tags.keys())
        user_b_tags = set(user_b.tags.keys())
        mutual_tags = list(user_a_tags & user_b_tags)
        
        # 找到互补标签（这里简化为差集，实际可以更复杂）
        complementary_tags = list((user_a_tags - user_b_tags) | (user_b_tags - user_a_tags))
        
        # 生成解释
        explanation = self._generate_match_explanation(
            user_a, user_b, profile_similarity, request_similarity, mutual_tags
        )
        
        return MatchResult(
            user_a_id=user_a.user_id,
            user_b_id=user_b.user_id,
            similarity_score=combined_similarity,
            profile_similarity=profile_similarity,
            request_similarity=request_similarity,
            mutual_tags=mutual_tags,
            complementary_tags=complementary_tags[:10],  # 限制数量
            explanation=explanation
        )
    
    def _generate_match_explanation(self, user_a: UserVector, user_b: UserVector,
                                  profile_sim: float, request_sim: float,
                                  mutual_tags: List[str]) -> str:
        """生成匹配解释"""
        explanation_parts = []
        
        # 诉求类型匹配
        if user_a.request_type == user_b.request_type:
            explanation_parts.append(f"诉求类型匹配（{user_a.request_type}）")
        else:
            explanation_parts.append(f"诉求类型不同（{user_a.request_type} vs {user_b.request_type}）")
        
        # 档案相似度
        if profile_sim > 0.7:
            explanation_parts.append("个人档案高度相似")
        elif profile_sim > 0.4:
            explanation_parts.append("个人档案中等相似")
        else:
            explanation_parts.append("个人档案相似度较低")
        
        # 诉求相似度
        if request_sim > 0.7:
            explanation_parts.append("诉求高度匹配")
        elif request_sim > 0.4:
            explanation_parts.append("诉求中等匹配")
        else:
            explanation_parts.append("诉求匹配度较低")
        
        # 共同标签
        if len(mutual_tags) > 5:
            explanation_parts.append(f"拥有{len(mutual_tags)}个共同标签")
        elif len(mutual_tags) > 0:
            explanation_parts.append(f"拥有少量共同标签（{len(mutual_tags)}个）")
        
        return "；".join(explanation_parts)
    
    def batch_find_all_matches(self, min_similarity: float = None) -> Dict[str, List[MatchResult]]:
        """批量为所有用户找到匹配"""
        min_similarity = min_similarity or self.config.similarity_threshold
        all_matches = {}
        
        print(f"为 {len(self.users)} 个用户计算匹配...")
        
        for user_id in self.user_ids:
            matches = self.find_matches(user_id)
            # 过滤相似度
            filtered_matches = [m for m in matches if m.similarity_score >= min_similarity]
            all_matches[user_id] = filtered_matches
        
        return all_matches
    
    def save_vectors(self, file_path: str) -> None:
        """保存用户向量数据"""
        data = {
            'user_ids': self.user_ids,
            'users': {}
        }
        
        for user_id, user_vector in self.users.items():
            data['users'][user_id] = {
                'profile_vector': user_vector.profile_vector.tolist(),
                'request_vector': user_vector.request_vector.tolist(),
                'combined_vector': user_vector.combined_vector.tolist(),
                'request_type': user_vector.request_type,
                'tags': user_vector.tags,
                'metadata': user_vector.metadata
            }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"向量数据已保存到: {file_path}")
    
    def load_vectors(self, file_path: str) -> None:
        """加载用户向量数据"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.user_ids = data['user_ids']
        self.users = {}
        
        for user_id, user_data in data['users'].items():
            self.users[user_id] = UserVector(
                user_id=user_id,
                profile_vector=np.array(user_data['profile_vector']),
                request_vector=np.array(user_data['request_vector']),
                combined_vector=np.array(user_data['combined_vector']),
                request_type=user_data['request_type'],
                tags=user_data['tags'],
                metadata=user_data['metadata']
            )
        
        print(f"向量数据已从 {file_path} 加载，用户数量: {len(self.users)}")

# 全局实例
vector_matcher = FaissVectorMatcher() 