#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
匹配功能调试测试脚本
使用数据库中第一个用户的信息进行匹配测试
"""

import requests
import json
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

API_BASE_URL = 'http://localhost:5002'

def test_api_connection():
    """测试API连接"""
    try:
        response = requests.get(f'{API_BASE_URL}/health', timeout=5)
        print(f"✅ API连接正常: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ API连接失败: {e}")
        return False

def get_all_users():
    """获取所有用户"""
    try:
        response = requests.get(f'{API_BASE_URL}/api/database/users')
        result = response.json()
        if result['success']:
            users = result['data']
            print(f"✅ 获取到 {len(users)} 个用户")
            return users
        else:
            print(f"❌ 获取用户失败: {result.get('message', '未知错误')}")
            return []
    except Exception as e:
        print(f"❌ 获取用户异常: {e}")
        return []

def test_matching_with_first_user(users):
    """使用第一个用户进行匹配测试"""
    if not users:
        print("❌ 没有用户数据可供测试")
        return
    
    first_user = users[0]
    print(f"\n🔍 使用第一个用户进行测试: {first_user.get('username', 'unknown')}")
    print(f"   年龄: {first_user.get('age', 'unknown')}")
    print(f"   性别: {first_user.get('gender', 'unknown')}")
    print(f"   城市: {first_user.get('location_city', 'unknown')}")
    
    # 获取用户的tags
    tags = first_user.get('tags', [])
    if tags:
        print(f"   标签: {[tag.get('name', tag) if isinstance(tag, dict) else tag for tag in tags[:5]]}")
    
    # 构造搜索查询（基于用户的bio和tags）
    bio = first_user.get('bio', '')
    looking_for = first_user.get('looking_for', [])
    
    # 生成测试查询
    test_queries = [
        "",  # 空查询
        "技术合作",
        "寻找伙伴",
    ]
    
    if bio:
        test_queries.append(bio[:50])  # 使用bio的前50个字符
    
    if looking_for:
        test_queries.append(looking_for[0] if looking_for else "")
    
    # 测试不同模式
    test_modes = ["找对象", "找队友"]
    
    for mode in test_modes:
        print(f"\n🔄 测试模式: {mode}")
        
        for query in test_queries:
            if not query:
                continue
                
            print(f"   查询: '{query[:30]}{'...' if len(query) > 30 else ''}'")
            
            # 找到其他用户进行匹配
            other_users = [u for u in users if u.get('id') != first_user.get('id')][:3]  # 测试前3个其他用户
            
            for candidate in other_users:
                try:
                    # 调用匹配API
                    match_data = {
                        "query": query,
                        "current_user": first_user,
                        "candidate_user": candidate,
                        "mode": mode
                    }
                    
                    response = requests.post(
                        f'{API_BASE_URL}/api/match/lda',
                        json=match_data,
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        if result.get('success'):
                            score = result.get('data', {}).get('match_score', 0) * 100
                            print(f"     ✅ {candidate.get('username', 'unknown')}: {score:.1f}%")
                        else:
                            print(f"     ❌ {candidate.get('username', 'unknown')}: API错误 - {result.get('message')}")
                    else:
                        print(f"     ❌ {candidate.get('username', 'unknown')}: HTTP {response.status_code}")
                        
                except Exception as e:
                    print(f"     ❌ {candidate.get('username', 'unknown')}: 异常 - {e}")

def test_simple_lda_matching():
    """测试简单的LDA匹配"""
    print("\n🧪 测试简单LDA匹配API")
    
    simple_test_data = {
        "query": "寻找技术合作伙伴",
        "current_user": {
            "username": "test_user",
            "age": 25,
            "gender": "male",
            "bio": "程序员，喜欢技术创新"
        },
        "candidate_user": {
            "username": "candidate_user", 
            "age": 27,
            "gender": "female",
            "bio": "设计师，热爱创意工作"
        },
        "mode": "找队友"
    }
    
    try:
        response = requests.post(
            f'{API_BASE_URL}/api/match/lda',
            json=simple_test_data,
            timeout=10
        )
        
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
        else:
            print(f"   错误响应: {response.text}")
            
    except Exception as e:
        print(f"   异常: {e}")

def main():
    """主函数"""
    print("🚀 开始匹配功能调试测试")
    print("=" * 50)
    
    # 1. 测试API连接
    if not test_api_connection():
        print("请确保API服务器在 http://localhost:5002 运行")
        return
    
    # 2. 测试简单匹配
    test_simple_lda_matching()
    
    # 3. 获取用户数据
    users = get_all_users()
    
    # 4. 使用第一个用户进行匹配测试
    if users:
        test_matching_with_first_user(users)
    else:
        print("❌ 无法获取用户数据，跳过用户匹配测试")
    
    print("\n✅ 测试完成")

if __name__ == "__main__":
    main() 