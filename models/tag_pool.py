#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dataclasses import dataclass
from typing import Dict, List, Set
from enum import Enum

class TagCategory(Enum):
    """标签分类"""
    # 找对象相关
    AGE = "age"
    PROFESSION = "profession"  
    PERSONALITY = "personality"
    INTERESTS = "interests"
    LIFESTYLE = "lifestyle"
    VALUES = "values"
    RELATIONSHIP_GOALS = "relationship_goals"
    LOCATION = "location"
    
    # 找队友相关
    SKILLS = "skills"
    INDUSTRY = "industry"
    PROJECT_TYPE = "project_type"
    COLLABORATION_STYLE = "collaboration_style"
    EXPERIENCE_LEVEL = "experience_level"
    AVAILABILITY = "availability"
    GOALS = "goals"

@dataclass
class TagPool:
    """标签池管理"""
    
    # 找对象标签池
    DATING_TAGS = {
        TagCategory.AGE: [
            "18-22岁", "23-27岁", "28-32岁", "33-37岁", "38-42岁", "43-47岁", "48岁以上"
        ],
        
        TagCategory.PROFESSION: [
            "程序员", "设计师", "产品经理", "市场营销", "销售", "教师", "医生", "律师", 
            "金融分析师", "咨询师", "创业者", "自由职业者", "艺术家", "记者", "公务员",
            "工程师", "研究员", "学生"
        ],
        
        TagCategory.PERSONALITY: [
            "外向开朗", "内向安静", "幽默风趣", "温和体贴", "理性冷静", "感性浪漫",
            "独立自主", "依赖性强", "冒险精神", "稳重踏实", "创意思维", "逻辑思维",
            "社交达人", "宅家一族", "完美主义", "随性自由"
        ],
        
        TagCategory.INTERESTS: [
            "运动健身", "音乐", "电影", "读书", "旅行", "摄影", "美食", "游戏",
            "艺术", "舞蹈", "唱歌", "绘画", "写作", "手工", "园艺", "宠物",
            "科技", "投资理财", "时尚", "化妆", "瑜伽", "冥想"
        ],
        
        TagCategory.LIFESTYLE: [
            "早睡早起", "夜猫子", "居家型", "社交型", "节俭", "消费主义",
            "健康饮食", "美食爱好者", "规律作息", "自由散漫", "计划性强", "随性而为",
            "独居", "合租", "与家人同住", "有宠物", "无宠物"
        ],
        
        TagCategory.VALUES: [
            "家庭至上", "事业优先", "自由平等", "传统保守", "物质追求", "精神富足",
            "环保意识", "社会责任", "个人成长", "团队合作", "诚实守信", "包容开放",
            "追求刺激", "安全稳定", "创新进取", "知足常乐"
        ],
        
        TagCategory.RELATIONSHIP_GOALS: [
            "寻找真爱", "结婚生子", "长期关系", "短期交往", "开放关系", "灵魂伴侣",
            "生活伴侣", "精神伴侣", "共同成长", "相互支持", "浪漫恋爱", "理性恋爱"
        ],
        
        TagCategory.LOCATION: [
            "北京", "上海", "广州", "深圳", "杭州", "南京", "成都", "重庆",
            "西安", "武汉", "天津", "青岛", "大连", "厦门", "苏州", "无锡",
            "海外", "小城市", "愿意异地", "不愿意异地"
        ]
    }
    
    # 找队友标签池
    TEAMWORK_TAGS = {
        TagCategory.SKILLS: [
            "前端开发", "后端开发", "全栈开发", "移动开发", "数据科学", "机器学习",
            "产品设计", "UI/UX设计", "产品管理", "项目管理", "市场营销", "商务拓展",
            "内容创作", "文案写作", "视频制作", "平面设计", "3D建模", "动画制作",
            "财务管理", "法务咨询", "运营管理", "人力资源", "客服支持"
        ],
        
        TagCategory.INDUSTRY: [
            "互联网", "移动应用", "游戏", "电商", "金融科技", "教育科技", "医疗健康",
            "人工智能", "区块链", "物联网", "新能源", "生物科技", "传媒娱乐",
            "旅游", "餐饮", "零售", "房地产", "汽车", "制造业", "咨询服务"
        ],
        
        TagCategory.PROJECT_TYPE: [
            "创业项目", "副业项目", "开源项目", "学习项目", "竞赛项目", "实验项目",
            "商业项目", "公益项目", "艺术项目", "研究项目", "APP开发", "网站建设",
            "内容创作", "社区运营", "产品设计", "技术咨询", "培训教育"
        ],
        
        TagCategory.COLLABORATION_STYLE: [
            "远程协作", "面对面合作", "灵活时间", "固定时间", "高频沟通", "低频沟通",
            "详细规划", "敏捷开发", "独立工作", "团队协作", "领导型", "执行型",
            "创意型", "技术型", "商务型", "支持型"
        ],
        
        TagCategory.EXPERIENCE_LEVEL: [
            "初学者", "有一些经验", "中级水平", "高级专家", "行业资深", "跨界经验",
            "学生", "职场新人", "有创业经验", "有管理经验", "有投资经验", "国际经验"
        ],
        
        TagCategory.AVAILABILITY: [
            "全职投入", "兼职参与", "周末项目", "晚间时间", "碎片时间", "长期合作",
            "短期项目", "阶段性参与", "高强度", "低强度", "灵活安排", "固定时间"
        ],
        
        TagCategory.GOALS: [
            "技能提升", "赚取收入", "积累经验", "扩展人脉", "追求兴趣", "解决问题",
            "创造价值", "学习成长", "建立作品集", "找到合伙人", "验证想法", "获得认可"
        ]
    }
    
    @classmethod
    def get_all_tags(cls, request_type: str = "all") -> Dict[TagCategory, List[str]]:
        """获取所有标签"""
        if request_type == "找对象":
            return cls.DATING_TAGS
        elif request_type == "找队友":
            return cls.TEAMWORK_TAGS
        else:
            # 合并所有标签
            all_tags = {}
            all_tags.update(cls.DATING_TAGS)
            all_tags.update(cls.TEAMWORK_TAGS)
            return all_tags
    
    @classmethod
    def get_tag_list(cls, request_type: str = "all") -> List[str]:
        """获取标签列表（用于向量化）"""
        tags = cls.get_all_tags(request_type)
        tag_list = []
        for category_tags in tags.values():
            tag_list.extend(category_tags)
        return tag_list
    
    @classmethod
    def get_tag_categories(cls, request_type: str = "all") -> List[TagCategory]:
        """获取标签分类"""
        tags = cls.get_all_tags(request_type)
        return list(tags.keys())
    
    @classmethod
    def find_matching_tags(cls, text: str, request_type: str = "all") -> Set[str]:
        """从文本中找到匹配的标签（简单关键词匹配）"""
        text = text.lower()
        matching_tags = set()
        
        for tag in cls.get_tag_list(request_type):
            if tag.lower() in text:
                matching_tags.add(tag)
        
        return matching_tags

# 单例标签池
tag_pool = TagPool() 