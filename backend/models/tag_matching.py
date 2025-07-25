#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import jieba
import re
import numpy as np
from typing import Dict, List, Tuple, Set
from dataclasses import dataclass
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .tag_pool import TagPool, TagCategory

@dataclass
class TagMatchResult:
    """标签匹配结果"""
    matched_tags: Dict[str, float]  # {tag: confidence_score, ...}
    tag_categories: Dict[TagCategory, List[Tuple[str, float]]]  # 按分类组织的标签
    total_score: float  # 总体匹配分数
    matched_keywords: List[str]  # 匹配的关键词

class ChineseTextProcessor:
    """中文文本处理器"""
    
    def __init__(self):
        self.stopwords = set([
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个',
            '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好',
            '自己', '这', '那', '现在', '可以', '但是', '如果', '他', '她', '它'
        ])
    
    def clean_and_tokenize(self, text: str) -> List[str]:
        """清理和分词"""
        if not text:
            return []
        
        # 清理文本
        text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        # 分词
        tokens = []
        for word in jieba.cut(text):
            word = word.strip()
            if (len(word) >= 2 and 
                word not in self.stopwords and 
                not word.isdigit()):
                tokens.append(word)
        
        return tokens

class TagMatcher:
    """基于语义相似度的标签匹配器"""
    
    def __init__(self, request_type: str = "all"):
        self.request_type = request_type
        self.tag_pool = TagPool()
        self.text_processor = ChineseTextProcessor()
        
        # 获取相关标签
        self.tags = self.tag_pool.get_tag_list(request_type)
        self.tag_categories_map = self._build_tag_categories_map()
        
        # 构建标签语料库用于TF-IDF
        self.tag_corpus = [tag for tag in self.tags]
        
        # 构建TF-IDF向量器
        self.vectorizer = TfidfVectorizer(
            tokenizer=self.text_processor.clean_and_tokenize,
            lowercase=False,
            max_features=5000
        )
        
        # 预计算标签向量
        self.tag_vectors = None
        self._build_tag_vectors()
    
    def _build_tag_categories_map(self) -> Dict[str, TagCategory]:
        """构建标签到类别的映射"""
        tag_to_category = {}
        all_tags = self.tag_pool.get_all_tags(self.request_type)
        
        for category, tags in all_tags.items():
            for tag in tags:
                tag_to_category[tag] = category
        
        return tag_to_category
    
    def _build_tag_vectors(self):
        """构建标签的TF-IDF向量"""
        if not self.tags:
            return
        
        # 为了获得更好的向量表示，我们为每个标签构建更丰富的文本
        enriched_tag_texts = []
        for tag in self.tags:
            # 将标签本身和其可能的同义词组合
            enriched_text = tag + " " + self._get_tag_synonyms(tag)
            enriched_tag_texts.append(enriched_text)
        
        try:
            self.tag_vectors = self.vectorizer.fit_transform(enriched_tag_texts)
        except Exception as e:
            print(f"构建标签向量时出错: {e}")
            # 如果出错，使用简单的单词匹配
            self.tag_vectors = None
    
    def _get_tag_synonyms(self, tag: str) -> str:
        """获取标签的同义词和相关词"""
        synonyms_map = {
            # 技术相关
            "程序员": "开发者 工程师 码农 技术人员",
            "设计师": "UI UX 视觉设计 产品设计",
            "产品经理": "PM 产品 需求分析",
            "创业者": "创始人 CEO 企业家",
            
            # 性格相关
            "外向开朗": "活泼 社交 开朗 外向",
            "内向安静": "内向 安静 文静 内敛",
            "幽默风趣": "幽默 搞笑 有趣 风趣",
            
            # 兴趣相关
            "运动健身": "健身 运动 锻炼 体育",
            "音乐": "音乐 唱歌 乐器 歌曲",
            "旅行": "旅游 旅行 出游 度假",
        }
        
        return synonyms_map.get(tag, "")
    
    def match_tags(self, user_text: str, min_confidence: float = 0.3) -> TagMatchResult:
        """匹配用户文本到标签"""
        if not user_text.strip():
            return TagMatchResult(
                matched_tags={},
                tag_categories={},
                total_score=0.0,
                matched_keywords=[]
            )
        
        matched_tags = {}
        matched_keywords = []
        
        # 方法1: 关键词匹配
        keyword_matches = self._keyword_matching(user_text)
        matched_tags.update(keyword_matches)
        
        # 方法2: TF-IDF相似度匹配（如果向量构建成功）
        if self.tag_vectors is not None:
            tfidf_matches = self._tfidf_matching(user_text)
            # 合并结果，取较高分数
            for tag, score in tfidf_matches.items():
                if tag in matched_tags:
                    matched_tags[tag] = max(matched_tags[tag], score)
                else:
                    matched_tags[tag] = score
        
        # 方法3: 模式匹配
        pattern_matches = self._pattern_matching(user_text)
        for tag, score in pattern_matches.items():
            if tag in matched_tags:
                matched_tags[tag] = max(matched_tags[tag], score)
            else:
                matched_tags[tag] = score
        
        # 过滤低置信度的标签
        filtered_tags = {
            tag: score for tag, score in matched_tags.items() 
            if score >= min_confidence
        }
        
        # 按类别组织标签
        tag_categories = self._organize_by_categories(filtered_tags)
        
        # 计算总体分数
        total_score = sum(filtered_tags.values()) / len(filtered_tags) if filtered_tags else 0
        
        return TagMatchResult(
            matched_tags=filtered_tags,
            tag_categories=tag_categories,
            total_score=total_score,
            matched_keywords=matched_keywords
        )
    
    def _keyword_matching(self, text: str) -> Dict[str, float]:
        """基于关键词的直接匹配"""
        text_lower = text.lower()
        matches = {}
        
        for tag in self.tags:
            tag_lower = tag.lower()
            score = 0.0
            
            # 完全匹配
            if tag_lower in text_lower:
                score = 0.9
            # 部分匹配
            elif any(word in text_lower for word in tag_lower.split()):
                score = 0.6
            # 同义词匹配
            else:
                synonyms = self._get_tag_synonyms(tag).lower().split()
                if any(syn in text_lower for syn in synonyms if syn):
                    score = 0.7
            
            if score > 0:
                matches[tag] = score
        
        return matches
    
    def _tfidf_matching(self, text: str) -> Dict[str, float]:
        """基于TF-IDF向量相似度的匹配"""
        try:
            # 将用户文本转换为向量
            user_vector = self.vectorizer.transform([text])
            
            # 计算与所有标签的相似度
            similarities = cosine_similarity(user_vector, self.tag_vectors).flatten()
            
            matches = {}
            for i, similarity in enumerate(similarities):
                if similarity > 0.1:  # 设置最小阈值
                    tag = self.tags[i]
                    matches[tag] = float(similarity)
            
            return matches
        
        except Exception as e:
            print(f"TF-IDF匹配时出错: {e}")
            return {}
    
    def _pattern_matching(self, text: str) -> Dict[str, float]:
        """基于模式的匹配"""
        matches = {}
        text_lower = text.lower()
        
        # 定义一些匹配模式
        patterns = {
            # 年龄相关
            "18-22岁": r'1[89]|2[012]|十八|十九|二十',
            "23-27岁": r'2[3-7]|二十[三四五六七]',
            "28-32岁": r'2[89]|3[012]|二十[八九]|三十',
            
            # 职业相关
            "程序员": r'程序|代码|开发|编程|软件|IT',
            "设计师": r'设计|UI|UX|美工|视觉',
            "产品经理": r'产品|PM|需求|项目管理',
            
            # 性格相关
            "外向开朗": r'外向|开朗|活泼|爱说话|社交',
            "内向安静": r'内向|安静|文静|不爱说话',
            
            # 兴趣相关
            "运动健身": r'运动|健身|锻炼|跑步|游泳|篮球|足球',
            "音乐": r'音乐|唱歌|乐器|钢琴|吉他',
            "旅行": r'旅行|旅游|出游|度假|旅行',
        }
        
        for tag, pattern in patterns.items():
            if tag in self.tags and re.search(pattern, text_lower):
                matches[tag] = 0.8
        
        return matches
    
    def _organize_by_categories(self, tags: Dict[str, float]) -> Dict[TagCategory, List[Tuple[str, float]]]:
        """按类别组织标签"""
        categories = {}
        
        for tag, score in tags.items():
            if tag in self.tag_categories_map:
                category = self.tag_categories_map[tag]
                if category not in categories:
                    categories[category] = []
                categories[category].append((tag, score))
        
        # 对每个类别的标签按分数排序
        for category in categories:
            categories[category].sort(key=lambda x: x[1], reverse=True)
        
        return categories
    
    def get_top_tags(self, result: TagMatchResult, top_k: int = 10) -> List[Tuple[str, float]]:
        """获取置信度最高的前K个标签"""
        sorted_tags = sorted(
            result.matched_tags.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        return sorted_tags[:top_k]

# 使用示例
def example_usage():
    """使用示例"""
    
    # 找对象场景
    dating_matcher = TagMatcher("找对象")
    
    user_text = """
    我是一个25岁的程序员，性格比较内向，平时喜欢看书、听音乐，
    偶尔会去健身房锻炼。希望找一个理解我的工作，性格温和的女生，
    一起在北京生活。
    """
    
    result = dating_matcher.match_tags(user_text)
    
    print("匹配结果:")
    print(f"总体分数: {result.total_score:.2f}")
    print("\n按类别组织的标签:")
    for category, tags in result.tag_categories.items():
        print(f"\n{category.value}:")
        for tag, score in tags:
            print(f"  {tag}: {score:.2f}")
    
    # 找队友场景
    teamwork_matcher = TagMatcher("找队友")
    
    team_text = """
    我是一个有3年经验的全栈开发，擅长React和Python，
    想找志同道合的伙伴一起做一个AI相关的创业项目，
    希望能长期合作，远程协作也可以。
    """
    
    team_result = teamwork_matcher.match_tags(team_text)
    print("\n\n找队友匹配结果:")
    top_tags = teamwork_matcher.get_top_tags(team_result, 5)
    for tag, score in top_tags:
        print(f"{tag}: {score:.2f}")

if __name__ == "__main__":
    example_usage() 