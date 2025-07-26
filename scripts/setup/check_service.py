 #!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
快速检查API服务状态
"""

import requests
import sys

def check_service(url, service_name):
    """检查服务状态"""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"✅ {service_name} 服务正常运行")
            return True
        else:
            print(f"⚠️ {service_name} 服务响应异常: HTTP {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ {service_name} 服务连接失败 - 请确保服务已启动")
        return False
    except requests.exceptions.Timeout:
        print(f"⏰ {service_name} 服务响应超时")
        return False
    except Exception as e:
        print(f"❌ {service_name} 服务检查异常: {e}")
        return False

def main():
    """主函数"""
    print("🔍 检查服务状态...")
    print("=" * 40)
    
    # 检查后端API服务
    api_status = check_service("http://localhost:5003/health", "后端API")
    
    if not api_status:
        print("\n💡 启动后端服务:")
        print("   python backend/services/comprehensive_api.py")
        print("   或")
        print("   python scripts/start_comprehensive_api.py")
    
    print("=" * 40)
    
    if api_status:
        print("🎉 所有服务正常运行！")
        print("可以运行测试脚本:")
        print("   python scripts/test_supabase_auth.py")
        return 0
    else:
        print("⚠️ 请先启动相关服务")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 