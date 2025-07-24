#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dataclasses import dataclass
from typing import Dict, Any
import json

@dataclass
class SimpleMatchingResult:
    """简洁的匹配结果输出"""
    
    # 基础信息
    person_a: str
    person_b: str
    
    # 匹配评分和描述
    overall_match: Dict[str, Any]           # 总体匹配
    personality_match: Dict[str, Any]       # 性格匹配
    interests_match: Dict[str, Any]         # 兴趣匹配
    career_match: Dict[str, Any]           # 职业匹配
    values_match: Dict[str, Any]           # 价值观匹配
    request_match: Dict[str, Any]          # 诉求匹配
    complementary_match: Dict[str, Any]    # 互补性匹配
    
    def to_json(self) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "participants": {
                "person_a": self.person_a,
                "person_b": self.person_b
            },
            "matching_analysis": {
                "overall_match": self.overall_match,
                "personality_match": self.personality_match,
                "interests_match": self.interests_match,
                "career_match": self.career_match,
                "values_match": self.values_match,
                "request_match": self.request_match,
                "complementary_match": self.complementary_match
            }
        }

def create_match_dimension(score: float, description: str, details: str = "") -> Dict[str, Any]:
    """创建匹配维度数据"""
    return {
        "score": round(score, 2),
        "description": description,
        "details": details
    }

def generate_score_description(score: float, dimension: str) -> str:
    """根据评分生成描述"""
    if score >= 8.0:
        return f"{dimension}高度匹配"
    elif score >= 6.0:
        return f"{dimension}良好匹配"
    elif score >= 4.0:
        return f"{dimension}中等匹配"
    elif score >= 2.0:
        return f"{dimension}匹配度较低"
    else:
        return f"{dimension}差异较大"

def calculate_complementary_score(person_a_tags: Dict[str, float], 
                                person_b_tags: Dict[str, float]) -> float:
    """计算互补性评分"""
    # 计算技能互补度
    tech_tags = ["前端开发", "后端开发", "产品设计", "市场营销", "运营管理", "数据科学"]
    a_tech = {tag: score for tag, score in person_a_tags.items() if tag in tech_tags}
    b_tech = {tag: score for tag, score in person_b_tags.items() if tag in tech_tags}
    
    # 如果两人技能不重叠但都有专业技能，则互补性高
    a_skills = set(a_tech.keys())
    b_skills = set(b_tech.keys())
    
    if a_skills and b_skills and len(a_skills & b_skills) < len(a_skills | b_skills) * 0.3:
        return 8.0  # 高互补性
    elif a_skills and b_skills:
        return 6.0  # 中等互补性
    else:
        return 3.0  # 低互补性 