#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
基于 Locust 的负载测试脚本

专业的API负载和性能测试工具
可以模拟大量并发用户对API进行压力测试
"""

from locust import HttpUser, task, between
import json
import random
import time
from typing import Dict, Any

class APIUser(HttpUser):
    """模拟API用户行为"""
    
    wait_time = between(1, 3)  # 请求间隔1-3秒
    
    def on_start(self):
        """用户开始时的初始化"""
        self.token = None
        self.user_id = None
        self.test_user = {
            "email": f"load_test_{random.randint(1000, 9999)}@example.com",
            "password": "test123456",
            "display_name": f"负载测试用户{random.randint(1, 1000)}"
        }
        
        # 尝试注册和登录
        self.register_and_login()
    
    def register_and_login(self):
        """注册并登录获取token"""
        # 注册用户
        with self.client.post(
            "/api/auth/register",
            json=self.test_user,
            catch_response=True
        ) as response:
            if response.status_code == 201:
                data = response.json()
                self.token = data.get('data', {}).get('token')
                self.user_id = data.get('data', {}).get('user_id')
                response.success()
            elif response.status_code == 409:
                # 用户已存在，尝试登录
                self.login_existing_user()
            else:
                response.failure(f"注册失败: {response.status_code}")
    
    def login_existing_user(self):
        """登录已存在的用户"""
        with self.client.post(
            "/api/auth/login",
            json={
                "email": self.test_user["email"],
                "password": self.test_user["password"]
            },
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('data', {}).get('token')
                self.user_id = data.get('data', {}).get('user_id')
                response.success()
            else:
                response.failure(f"登录失败: {response.status_code}")
    
    def get_auth_headers(self) -> Dict[str, str]:
        """获取认证头"""
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        } if self.token else {"Content-Type": "application/json"}
    
    @task(10)
    def health_check(self):
        """健康检查 - 最高频率"""
        self.client.get("/api/system/health")
    
    @task(8)
    def get_system_stats(self):
        """获取系统统计"""
        self.client.get("/api/system/stats")
    
    @task(6)
    def get_user_profile(self):
        """获取用户资料"""
        if self.token:
            self.client.get(
                "/api/auth/me",
                headers=self.get_auth_headers()
            )
    
    @task(5)
    def get_user_metadata(self):
        """获取用户metadata"""
        if self.token:
            self.client.get(
                "/api/profile/metadata",
                headers=self.get_auth_headers()
            )
    
    @task(4)
    def create_metadata(self):
        """创建用户metadata"""
        if self.token:
            metadata = {
                "section_type": "profile",
                "section_key": random.choice(["personal", "professional", "preferences"]),
                "content": {
                    "test_field": f"负载测试数据_{random.randint(1, 1000)}",
                    "timestamp": int(time.time())
                }
            }
            
            self.client.post(
                "/api/profile/metadata",
                json=metadata,
                headers=self.get_auth_headers()
            )
    
    @task(3)
    def add_manual_tags(self):
        """手动添加标签"""
        if self.token:
            tags = [
                f"负载测试标签{random.randint(1, 100)}",
                random.choice(["Python", "Java", "JavaScript", "Go", "Rust"]),
                random.choice(["AI", "区块链", "云计算", "大数据", "物联网"])
            ]
            
            self.client.post(
                "/api/tags/manual",
                json={"tags": tags},
                headers=self.get_auth_headers()
            )
    
    @task(3)
    def get_user_tags(self):
        """获取用户标签"""
        if self.token:
            self.client.get(
                "/api/tags/user",
                headers=self.get_auth_headers()
            )
    
    @task(2)
    def search_users(self):
        """搜索匹配用户"""
        if self.token:
            search_data = {
                "description": f"负载测试搜索_{random.randint(1, 100)}",
                "tags": [
                    random.choice(["Python", "Java", "AI", "创业"]),
                    random.choice(["产品", "技术", "设计", "运营"])
                ],
                "match_type": random.choice(["找队友", "找对象"]),
                "limit": random.randint(3, 10)
            }
            
            self.client.post(
                "/api/match/search",
                json=search_data,
                headers=self.get_auth_headers()
            )
    
    @task(1)
    def generate_tags(self):
        """生成标签 - 较重的操作，低频率"""
        if self.token:
            self.client.post(
                "/api/tags/generate",
                json={"request_type": random.choice(["找队友", "找对象"])},
                headers=self.get_auth_headers()
            )

class HeavyUser(HttpUser):
    """重负载用户 - 执行更消耗资源的操作"""
    
    wait_time = between(2, 5)  # 更长的等待时间
    weight = 1  # 较低的权重，模拟少数重用户
    
    def on_start(self):
        """初始化重负载用户"""
        self.token = None
        self.user_id = None
        self.test_user = {
            "email": f"heavy_user_{random.randint(1000, 9999)}@example.com",
            "password": "test123456",
            "display_name": f"重负载用户{random.randint(1, 100)}"
        }
        self.register_and_login()
    
    def register_and_login(self):
        """注册并登录"""
        # 注册
        response = self.client.post("/api/auth/register", json=self.test_user)
        if response.status_code == 201:
            data = response.json()
            self.token = data.get('data', {}).get('token')
            self.user_id = data.get('data', {}).get('user_id')
        elif response.status_code == 409:
            # 用户已存在，登录
            response = self.client.post("/api/auth/login", json={
                "email": self.test_user["email"],
                "password": self.test_user["password"]
            })
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('data', {}).get('token')
                self.user_id = data.get('data', {}).get('user_id')
    
    def get_auth_headers(self):
        """获取认证头"""
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        } if self.token else {"Content-Type": "application/json"}
    
    @task(3)
    def batch_create_metadata(self):
        """批量创建metadata"""
        if self.token:
            metadata_entries = []
            for i in range(random.randint(3, 8)):
                metadata_entries.append({
                    "section_type": random.choice(["profile", "user_request"]),
                    "section_key": f"batch_key_{i}",
                    "content": {
                        "heavy_data": f"大量数据_{random.randint(1, 1000)}",
                        "index": i,
                        "timestamp": int(time.time())
                    }
                })
            
            self.client.post(
                "/api/profile/metadata/batch",
                json={"metadata_entries": metadata_entries},
                headers=self.get_auth_headers()
            )
    
    @task(2)
    def complex_search(self):
        """复杂搜索"""
        if self.token:
            complex_search = {
                "description": "这是一个复杂的搜索请求，包含大量文本描述，用于测试系统在处理复杂查询时的性能表现。我们希望找到具有多种技能和经验的合作伙伴。",
                "tags": [
                    "Python", "机器学习", "深度学习", "自然语言处理",
                    "计算机视觉", "数据科学", "云计算", "分布式系统",
                    "微服务", "Docker", "Kubernetes", "产品管理"
                ],
                "match_type": "找队友",
                "limit": 20
            }
            
            self.client.post(
                "/api/match/search",
                json=complex_search,
                headers=self.get_auth_headers()
            )
    
    @task(1)
    def generate_many_tags(self):
        """生成大量标签"""
        if self.token:
            # 首先创建大量metadata
            for section in ["personal", "professional", "preferences", "experience"]:
                metadata = {
                    "section_type": "profile",
                    "section_key": section,
                    "content": {
                        f"{section}_data": f"丰富的{section}信息，包含大量文本描述" * 10,
                        "skills": ["技能1", "技能2", "技能3"] * 5,
                        "experience": ["经验1", "经验2", "经验3"] * 5
                    }
                }
                self.client.post(
                    "/api/profile/metadata",
                    json=metadata,
                    headers=self.get_auth_headers()
                )
            
            # 然后生成标签
            self.client.post(
                "/api/tags/generate",
                json={"request_type": "找队友"},
                headers=self.get_auth_headers()
            )

# 运行配置
class StagesShape:
    """负载测试阶段配置"""
    
    def tick(self):
        run_time = self.get_run_time()
        
        if run_time < 60:
            # 第一分钟：渐进加载
            user_count = round(run_time)
            spawn_rate = 1
        elif run_time < 180:
            # 2-3分钟：稳定负载
            user_count = 60
            spawn_rate = 2
        elif run_time < 240:
            # 3-4分钟：高负载
            user_count = 100
            spawn_rate = 5
        elif run_time < 300:
            # 4-5分钟：逐渐减少
            user_count = max(10, 100 - (run_time - 240) * 2)
            spawn_rate = 2
        else:
            # 5分钟后：停止
            user_count = 0
            spawn_rate = 1
        
        return user_count, spawn_rate

if __name__ == "__main__":
    # 可以直接运行此脚本进行本地测试
    import subprocess
    import sys
    import os
    
    print("🚀 启动 Locust 负载测试")
    print("=" * 50)
    print("🌐 Web界面: http://localhost:8089")
    print("🎯 目标API: http://localhost:5003")
    print("📊 测试场景:")
    print("  - 普通用户: 模拟常规API使用")
    print("  - 重负载用户: 模拟复杂操作")
    print("=" * 50)
    
    # 检查是否安装了locust
    try:
        subprocess.run(["locust", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Locust 未安装")
        print("安装方法: pip install locust")
        sys.exit(1)
    
    # 启动locust
    os.system("locust -f tests/test_load_performance.py --host=http://localhost:5003") 