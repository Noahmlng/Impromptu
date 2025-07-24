#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API 客户端测试脚本

演示如何使用用户匹配系统的REST API
"""

import requests
import json
import os
import time

# API服务器地址
BASE_URL = "http://localhost:5000"

def test_health_check():
    """测试健康检查接口"""
    print("🏥 测试健康检查接口...")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 服务器状态: {data.get('status')}")
            print(f"📝 信息: {data.get('message')}")
            print(f"🏷️ 版本: {data.get('version')}")
            return True
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到API服务器，请确保服务器正在运行")
        return False
    except Exception as e:
        print(f"❌ 健康检查出错: {e}")
        return False

def test_api_docs():
    """测试API文档接口"""
    print("\n📚 获取API文档...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/docs")
        if response.status_code == 200:
            docs = response.json()
            print(f"✅ API标题: {docs.get('title')}")
            print(f"📖 描述: {docs.get('description')}")
            print(f"🔌 可用接口数量: {len(docs.get('endpoints', {}))}")
            return True
        else:
            print(f"❌ 获取文档失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 获取文档出错: {e}")
        return False

def test_demo_match():
    """测试演示匹配接口"""
    print("\n🎯 测试演示匹配接口 (Noah vs Alan)...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/demo")
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                data = result['data']
                print("✅ 演示匹配成功!")
                print(f"👥 参与者: {data['participants']['person_a']} vs {data['participants']['person_b']}")
                
                # 显示匹配评分
                matching = data['matching_analysis']
                print("\n📊 匹配评分:")
                for dimension, info in matching.items():
                    print(f"  {dimension:20s}: {info['score']:5.2f} - {info['description']}")
                
                return True
            else:
                print(f"❌ 演示匹配失败: {result}")
                return False
        else:
            print(f"❌ 演示匹配请求失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 演示匹配出错: {e}")
        return False

def test_tags_api():
    """测试标签池接口"""
    print("\n🏷️ 测试标签池接口...")
    
    try:
        # 获取所有标签
        response = requests.get(f"{BASE_URL}/api/tags?type=all")
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                data = result['data']
                print(f"✅ 总标签数量: {data['total_tags']}")
                print(f"📋 标签分类数量: {len(data['tags_by_category'])}")
                
                # 测试特定类型
                for tag_type in ['找对象', '找队友']:
                    response = requests.get(f"{BASE_URL}/api/tags?type={tag_type}")
                    if response.status_code == 200:
                        type_result = response.json()
                        if type_result.get('success'):
                            type_data = type_result['data']
                            print(f"  {tag_type}: {type_data['total_tags']} 个标签")
                
                return True
            else:
                print(f"❌ 获取标签失败: {result}")
                return False
        else:
            print(f"❌ 标签接口请求失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 标签接口出错: {e}")
        return False

def test_simple_match_api():
    """测试简洁匹配API"""
    print("\n🔍 测试简洁匹配API...")
    
    # 创建两个测试用户档案
    user_a = {
        "profile": {
            "name": {"display_name": "测试用户A"},
            "professional": {"current_role": "AI工程师"},
            "personality": {"mbti_type": "INTJ", "interests": ["AI", "编程", "阅读"]},
            "expertise_areas": ["机器学习", "深度学习", "Python"]
        },
        "user_request": {
            "request_type": "找队友",
            "description": "寻找AI技术合作伙伴，希望一起开发AI产品"
        }
    }
    
    user_b = {
        "profile": {
            "name": {"display_name": "测试用户B"},
            "professional": {"current_role": "产品经理"},
            "personality": {"mbti_type": "ENFP", "interests": ["产品设计", "用户体验", "创新"]},
            "expertise_areas": ["产品管理", "用户研究", "商业分析"]
        },
        "user_request": {
            "request_type": "找队友",
            "description": "寻找技术合伙人，想要开发有社会价值的AI产品"
        }
    }
    
    try:
        payload = {
            "user_a": user_a,
            "user_b": user_b
        }
        
        response = requests.post(
            f"{BASE_URL}/api/match/simple",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                data = result['data']
                print("✅ 简洁匹配成功!")
                print(f"👥 参与者: {data['participants']['person_a']} vs {data['participants']['person_b']}")
                
                # 显示匹配评分
                matching = data['matching_analysis']
                print("\n📊 匹配评分:")
                for dimension, info in matching.items():
                    print(f"  {dimension:20s}: {info['score']:5.2f} - {info['description']}")
                
                # 显示详细信息
                print("\n📝 详细分析:")
                for dimension, info in matching.items():
                    if info.get('details'):
                        print(f"  • {dimension}: {info['details']}")
                
                return True
            else:
                print(f"❌ 简洁匹配失败: {result}")
                return False
        else:
            print(f"❌ 简洁匹配请求失败: {response.status_code}")
            print(f"响应内容: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 简洁匹配出错: {e}")
        return False

def test_training_api():
    """测试模型训练API"""
    print("\n🧠 测试模型训练API...")
    
    # 读取现有的用户档案用于训练
    profile_files = [
        "data/profiles/noah_profile.json",
        "data/profiles/alan_profile.json"
    ]
    
    profiles = []
    for file_path in profile_files:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                profiles.append(json.load(f))
    
    if len(profiles) < 2:
        print("❌ 没有足够的档案文件进行训练测试")
        return False
    
    try:
        payload = {"profiles": profiles}
        
        response = requests.post(
            f"{BASE_URL}/api/train",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"✅ 模型训练成功!")
                print(f"📊 使用档案数量: {result.get('profiles_count')}")
                print(f"📝 消息: {result.get('message')}")
                return True
            else:
                print(f"❌ 模型训练失败: {result}")
                return False
        else:
            print(f"❌ 训练请求失败: {response.status_code}")
            print(f"响应内容: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 模型训练出错: {e}")
        return False

def show_usage_examples():
    """显示API使用示例"""
    print("\n📖 API使用示例:")
    print("=" * 50)
    
    print("1. Python requests 示例:")
    print("""
import requests

# 健康检查
response = requests.get('http://localhost:5000/health')
print(response.json())

# 简洁匹配
payload = {
    "user_a": {"profile": {...}, "user_request": {...}},
    "user_b": {"profile": {...}, "user_request": {...}}
}
response = requests.post(
    'http://localhost:5000/api/match/simple',
    json=payload
)
result = response.json()
""")
    
    print("2. curl 示例:")
    print("""
# 健康检查
curl http://localhost:5000/health

# 演示匹配
curl http://localhost:5000/api/demo

# 获取标签池
curl "http://localhost:5000/api/tags?type=找队友"

# API文档
curl http://localhost:5000/api/docs
""")

def run_all_tests():
    """运行所有测试"""
    print("🚀 开始API客户端测试")
    print("=" * 60)
    
    tests = [
        ("健康检查", test_health_check),
        ("API文档", test_api_docs),
        ("演示匹配", test_demo_match),
        ("标签池", test_tags_api),
        ("简洁匹配", test_simple_match_api),
        ("模型训练", test_training_api)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 执行测试: {test_name}")
        print("-" * 40)
        
        start_time = time.time()
        success = test_func()
        duration = time.time() - start_time
        
        results.append((test_name, success, duration))
        
        if success:
            print(f"✅ {test_name} 测试通过 ({duration:.2f}秒)")
        else:
            print(f"❌ {test_name} 测试失败 ({duration:.2f}秒)")
    
    # 显示测试总结
    print("\n📊 测试总结:")
    print("=" * 60)
    
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    for test_name, success, duration in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{test_name:15s}: {status:8s} ({duration:5.2f}秒)")
    
    print(f"\n总体结果: {passed}/{total} 测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！API服务器运行正常")
    else:
        print("⚠️ 部分测试失败，请检查API服务器状态")
    
    return passed == total

if __name__ == "__main__":
    print("🎯 用户匹配系统 API 客户端测试")
    print("确保API服务器正在运行 (python api_server.py)")
    print("=" * 60)
    
    # 先检查服务器是否可用
    if test_health_check():
        print("\n✅ 服务器可访问，开始完整测试...")
        run_all_tests()
        show_usage_examples()
    else:
        print("\n❌ 服务器不可访问")
        print("请先启动API服务器:")
        print("  python api_server.py")
        print("\n然后重新运行此测试脚本:")
        print("  python test_api_client.py") 