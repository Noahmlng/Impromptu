#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
调试用户数据格式脚本
检查looking_for字段和其他关键字段的值
"""

import requests
import json

API_BASE_URL = 'http://localhost:5002'

def analyze_user_data():
    """分析用户数据格式"""
    try:
        response = requests.get(f'{API_BASE_URL}/api/database/users')
        result = response.json()
        
        if not result['success']:
            print(f"❌ 获取用户失败: {result.get('message')}")
            return
            
        users = result['data']
        print(f"📊 分析 {len(users)} 个用户的数据格式")
        print("=" * 60)
        
        # 统计字段信息
        looking_for_values = set()
        gender_values = set()
        
        for i, user in enumerate(users):
            print(f"\n👤 用户 {i+1}: {user.get('username', 'unknown')}")
            print(f"   ID: {user.get('id', 'missing')}")
            print(f"   年龄: {user.get('age', 'missing')}")
            print(f"   性别: {user.get('gender', 'missing')}")
            print(f"   城市: {user.get('location_city', 'missing')}")
            
            # 分析looking_for字段
            looking_for = user.get('looking_for', [])
            print(f"   looking_for类型: {type(looking_for)}")
            print(f"   looking_for内容: {looking_for}")
            
            if isinstance(looking_for, list):
                for goal in looking_for:
                    looking_for_values.add(goal)
            else:
                looking_for_values.add(str(looking_for))
            
            # 收集性别值
            gender = user.get('gender')
            if gender:
                gender_values.add(gender)
                
            # 分析tags字段
            tags = user.get('tags', [])
            print(f"   tags数量: {len(tags) if isinstance(tags, list) else 'not list'}")
            if tags and isinstance(tags, list):
                print(f"   前3个tags: {tags[:3]}")
        
        print(f"\n📈 数据统计")
        print("=" * 30)
        print(f"所有looking_for值:")
        for value in sorted(looking_for_values):
            print(f"  - '{value}'")
            
        print(f"\n所有gender值:")
        for value in sorted(gender_values):
            print(f"  - '{value}'")
        
        # 测试过滤逻辑
        print(f"\n🔍 测试过滤逻辑")
        print("=" * 30)
        
        alex_user = next((u for u in users if u.get('username') == 'alex_chen'), None)
        if alex_user:
            print(f"当前用户: {alex_user.get('username')} (性别: {alex_user.get('gender')})")
            
            # 测试找对象过滤
            dating_goals = ['寻找真爱', '长期关系', '结婚生子', '浪漫恋爱', '生活伴侣']
            dating_candidates = []
            for user in users:
                if user.get('id') == alex_user.get('id'):
                    continue
                if alex_user.get('gender') == 'male' and user.get('gender') != 'female':
                    continue
                if alex_user.get('gender') == 'female' and user.get('gender') != 'male':
                    continue
                    
                user_goals = user.get('looking_for', [])
                if isinstance(user_goals, list) and any(goal in dating_goals for goal in user_goals):
                    dating_candidates.append(user.get('username'))
            
            print(f"找对象模式候选人数量: {len(dating_candidates)}")
            print(f"候选人: {dating_candidates}")
            
            # 测试找队友过滤
            team_goals = ['找队友', '产品合作', '创业伙伴', '技术合作', '创意合作', '艺术合作', '教育合作']
            team_candidates = []
            for user in users:
                if user.get('id') == alex_user.get('id'):
                    continue
                    
                user_goals = user.get('looking_for', [])
                if isinstance(user_goals, list) and any(goal in team_goals for goal in user_goals):
                    team_candidates.append(user.get('username'))
            
            print(f"找队友模式候选人数量: {len(team_candidates)}")
            print(f"候选人: {team_candidates}")
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")

if __name__ == "__main__":
    analyze_user_data() 