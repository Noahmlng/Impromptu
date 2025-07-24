#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dataclasses import dataclass
from typing import List

@dataclass
class CompatibilityResult:
    """兼容性分析结果数据结构"""
    
    person_a: str
    person_b: str
    mutual_interest_score: float
    a_to_b_interest: float
    b_to_a_interest: float
    request_matching_score: float
    personality_matching_score: float
    compatibility_factors: List[str]
    potential_conflicts: List[str]
    request_analysis: str
    recommendation: str
    detailed_analysis: str 