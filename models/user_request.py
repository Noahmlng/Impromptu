#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dataclasses import dataclass

@dataclass
class UserRequest:
    """用户诉求数据结构"""
    
    request_type: str  # "找对象" 或 "找队友"
    description: str   # 诉求描述：背景信息、目标和目标画像
    
    def __post_init__(self):
        if self.request_type not in ["找对象", "找队友"]:
            raise ValueError("诉求类型必须是'找对象'或'找队友'") 