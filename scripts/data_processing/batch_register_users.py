#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
批量注册用户脚本
基于user_profile表的数据，通过API接口批量创建用户
"""

import requests
import json
import sys
import time
from typing import List, Dict, Optional

# API配置
API_BASE_URL = 'http://localhost:5003'
DEFAULT_PASSWORD = 'default_password_123'  # 默认密码，用户后续可以修改

def get_users_from_profile_table() -> List[Dict]:
    """从user_profile表获取需要注册的用户列表"""
    print("📋 获取需要注册的用户列表...")
    
    # 这里我们直接定义需要注册的用户数据
    # 基于之前查询到的user_profile表数据
    users_to_register = [
        {"email": "user532@qq.com", "display_name": "郭佳 Alan", "phone": "15005320000"},
        {"email": "example215@gmail.com", "display_name": "小雅 Emma", "phone": "13802158888"},
        {"email": "test46@outlook.com", "display_name": "志强 David", "phone": "13900469999"},
        {"email": "example910@gmail.com", "display_name": "傅亿航Kyrie", "phone": "13809108888"},
        {"email": "sample639@sina.com", "display_name": "泽铭 Noah", "phone": "19906392222"},
        {"email": "test1@outlook.com", "display_name": "陈浩 Alex", "phone": "13900019999"},
        {"email": "user2@qq.com", "display_name": "王雅婷 Sophia", "phone": "15000020000"},
        {"email": "demo3@163.com", "display_name": "李凯文 Kevin", "phone": "18800031111"},
        {"email": "sample4@sina.com", "display_name": "张月 Luna", "phone": "19900042222"},
        {"email": "example5@gmail.com", "display_name": "吴大伟 David", "phone": "13800058888"},
        {"email": "test6@outlook.com", "display_name": "陈虹 Iris", "phone": "13900069999"},
        {"email": "user7@qq.com", "display_name": "张明轩 Michael", "phone": "15000070000"},
        {"email": "demo8@163.com", "display_name": "刘婧怡 Jenny", "phone": "18800081111"},
        {"email": "sample9@sina.com", "display_name": "王俊杰 Jason", "phone": "19900092222"},
        {"email": "example10@gmail.com", "display_name": "周爱丽 Alice", "phone": "13800108888"},
        {"email": "test11@outlook.com", "display_name": "李莎拉 Sarah", "phone": "13900119999"},
        {"email": "user12@qq.com", "display_name": "赵凯文 Kevin", "phone": "15000120000"},
        {"email": "demo13@163.com", "display_name": "王艾玛 Emma", "phone": "18800131111"},
        {"email": "sample14@sina.com", "display_name": "陈锐恩 Ryan", "phone": "19900142222"},
        {"email": "example15@gmail.com", "display_name": "周璐希 Lucy", "phone": "13800158888"},
        {"email": "test16@outlook.com", "display_name": "刘托马斯 Thomas", "phone": "13900169999"},
        {"email": "user17@qq.com", "display_name": "刘建明 James", "phone": "15000170000"},
        {"email": "demo18@163.com", "display_name": "周爱美 Amy", "phone": "18800181111"},
        {"email": "sample19@sina.com", "display_name": "王尔力 Eric", "phone": "19900192222"},
        {"email": "test21@outlook.com", "display_name": "王玛雅 Maya", "phone": "13900219999"},
        {"email": "user22@qq.com", "display_name": "林云霏 Yunfei", "phone": "15000220000"},
        {"email": "demo23@163.com", "display_name": "陈米娅 Mia", "phone": "18800231111"},
        {"email": "sample24@sina.com", "display_name": "黄雅雯 Grace", "phone": "19900242222"},
        {"email": "example25@gmail.com", "display_name": "张江河 River", "phone": "13800258888"},
        {"email": "test26@outlook.com", "display_name": "刘星辰 Stella", "phone": "13900269999"},
        {"email": "user27@qq.com", "display_name": "赵威克 Victor", "phone": "15000270000"},
        {"email": "demo28@163.com", "display_name": "徐怡然 Yiran", "phone": "18800281111"},
        {"email": "sample29@sina.com", "display_name": "李小明 Xiaoming", "phone": "19900292222"},
        {"email": "example30@gmail.com", "display_name": "张琪琪 Kiki", "phone": "13800308888"},
        {"email": "test31@outlook.com", "display_name": "吴安德 Andrew", "phone": "13900319999"},
        {"email": "user32@qq.com", "display_name": "陈海伦娜 Helena", "phone": "15000320000"},
        {"email": "demo33@163.com", "display_name": "周杰克 Jack", "phone": "18800331111"},
        {"email": "sample34@sina.com", "display_name": "王小强 Xiaoqiang", "phone": "19900342222"},
        {"email": "example35@gmail.com", "display_name": "李可可 Coco", "phone": "13800358888"},
        {"email": "test36@outlook.com", "display_name": "张立欧 Leo", "phone": "13900369999"},
        {"email": "user37@qq.com", "display_name": "陈马丁 Martin", "phone": "15000370000"},
        {"email": "demo38@163.com", "display_name": "刘迈克 Mike", "phone": "18800381111"},
        {"email": "sample39@sina.com", "display_name": "刘小雅 Xiaoya", "phone": "19900392222"},
        {"email": "example40@gmail.com", "display_name": "黄东尼 Tony", "phone": "13800408888"},
        {"email": "test41@outlook.com", "display_name": "王晶晶 Crystal", "phone": "13900419999"},
        {"email": "user42@qq.com", "display_name": "周薇薇安 Vivian", "phone": "15000420000"}
    ]
    
    print(f"📊 找到 {len(users_to_register)} 个用户需要注册")
    return users_to_register

def register_user(user_data: Dict) -> Optional[Dict]:
    """注册单个用户"""
    url = f"{API_BASE_URL}/api/auth/register"
    data = {
        "email": user_data["email"],
        "password": DEFAULT_PASSWORD,
        "display_name": user_data["display_name"]
    }
    
    try:
        print(f"   发送请求到: {url}")
        print(f"   请求数据: {json.dumps(data, ensure_ascii=False)}")
        
        response = requests.post(url, json=data, timeout=30)
        print(f"   响应状态码: {response.status_code}")
        
        try:
            result = response.json()
            print(f"   响应内容: {json.dumps(result, ensure_ascii=False, indent=2)}")
        except json.JSONDecodeError:
            print(f"   响应内容(非JSON): {response.text}")
            return None
        
        if response.status_code == 201 and result.get('success'):
            print(f"✅ 注册成功: {user_data['email']} ({user_data['display_name']})")
            return result['data']
        else:
            error_msg = result.get('error', result.get('message', '未知错误'))
            if "already exists" in error_msg.lower() or "duplicate" in error_msg.lower():
                print(f"⚠️  用户已存在: {user_data['email']} ({user_data['display_name']})")
                return None
            else:
                print(f"❌ 注册失败: {user_data['email']} - {error_msg}")
                return None
            
    except requests.exceptions.Timeout:
        print(f"❌ 请求超时: {user_data['email']}")
        return None
    except requests.exceptions.ConnectionError:
        print(f"❌ 连接错误: {user_data['email']}")
        return None
    except Exception as e:
        print(f"❌ 注册请求异常: {user_data['email']} - {e}")
        return None

def test_health_check() -> bool:
    """测试API健康检查"""
    print("🧪 测试API健康状态...")
    
    url = f"{API_BASE_URL}/health"
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            print("✅ API健康检查通过")
            return True
        else:
            print(f"❌ API健康检查失败: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ API健康检查异常: {e}")
        return False

def main():
    """主函数"""
    print("🚀 开始批量注册用户")
    print("=" * 60)
    
    # 1. 健康检查
    if not test_health_check():
        print("\n❌ API服务不可用，请确保后端服务正在运行")
        print("💡 启动后端服务:")
        print("   python backend/services/comprehensive_api.py")
        print("   或")
        print("   python scripts/start_comprehensive_api.py")
        sys.exit(1)
    
    # 2. 获取需要注册的用户列表
    users_to_register = get_users_from_profile_table()
    
    # 3. 批量注册用户
    print(f"\n🔄 开始批量注册 {len(users_to_register)} 个用户...")
    print("-" * 60)
    
    success_count = 0
    existing_count = 0
    failed_count = 0
    
    for i, user_data in enumerate(users_to_register, 1):
        print(f"\n[{i}/{len(users_to_register)}] 正在注册: {user_data['email']}")
        
        result = register_user(user_data)
        
        if result:
            success_count += 1
        elif "用户已存在" in str(result):
            existing_count += 1
        else:
            failed_count += 1
        
        # 添加延迟避免请求过于频繁
        time.sleep(1)
    
    # 4. 输出统计结果
    print("\n" + "=" * 60)
    print("📊 批量注册完成！统计结果:")
    print(f"   ✅ 成功注册: {success_count} 个用户")
    print(f"   ⚠️  用户已存在: {existing_count} 个用户")
    print(f"   ❌ 注册失败: {failed_count} 个用户")
    print(f"   📋 总计处理: {len(users_to_register)} 个用户")
    
    if failed_count > 0:
        print(f"\n⚠️  有 {failed_count} 个用户注册失败，请检查日志")
    
    print(f"\n💡 默认密码: {DEFAULT_PASSWORD}")
    print("   用户可以使用邮箱和默认密码登录，然后修改密码")

if __name__ == "__main__":
    main() 