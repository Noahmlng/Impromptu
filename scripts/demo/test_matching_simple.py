#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简单测试匹配功能
直接测试搜索API，不需要用户认证
"""

import sys
import os
import requests
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

API_URL = "http://localhost:8000"

def test_search_without_auth():
    """测试搜索功能（不需要认证）"""
    print("🧪 测试匹配搜索功能...")
    
    # 测试数据
    search_data = {
        "description": "寻找技术合作伙伴，擅长前端开发",
        "tags": ["编程", "技术", "前端"],
        "match_type": "找队友",
        "limit": 5
    }
    
    try:
        url = f"{API_URL}/api/match/search"
        headers = {
            "Content-Type": "application/json",
            # 使用一个假的token，看看API如何处理
            "Authorization": "Bearer fake_token_for_testing"
        }
        
        print(f"📡 请求URL: {url}")
        print(f"📦 请求数据: {json.dumps(search_data, ensure_ascii=False, indent=2)}")
        
        response = requests.post(url, json=search_data, headers=headers, timeout=10)
        
        print(f"📊 响应状态码: {response.status_code}")
        print(f"📄 响应内容: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 搜索功能正常工作")
            if result.get('data') and result['data'].get('matched_users'):
                users = result['data']['matched_users']
                print(f"🔍 找到 {len(users)} 个匹配用户:")
                for i, user in enumerate(users[:3], 1):
                    print(f"  {i}. {user.get('display_name', 'N/A')} - 匹配度: {user.get('match_score', 0):.2f}")
            else:
                print("📭 没有找到匹配用户")
        else:
            print(f"❌ 搜索失败: {response.text}")
            
    except Exception as e:
        print(f"❌ 测试搜索功能失败: {e}")

def test_api_health():
    """测试API健康状态"""
    print("🏥 检查API健康状态...")
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API服务正常运行")
            return True
        else:
            print(f"❌ API健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 无法连接到API服务: {e}")
        return False

if __name__ == "__main__":
    print("🚀 开始测试匹配功能")
    print("=" * 50)
    
    # 检查API健康状态
    if test_api_health():
        # 测试搜索功能
        test_search_without_auth()
    else:
        print("💡 请确保后端API服务正在运行:")
        print("   cd /Users/zeming/Documents/Impromptu")
        print("   python backend/services/main_api.py")
    
    print("=" * 50)
    print("🏁 测试完成") 