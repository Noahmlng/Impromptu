#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API 稳定性测试套件

测试所有API端点的功能性、性能和稳定性
适用于部署前的完整验证
"""

import requests
import json
import time
import random
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import statistics
import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

@dataclass
class TestResult:
    """测试结果数据类"""
    endpoint: str
    method: str
    status_code: int
    response_time: float
    success: bool
    error_message: Optional[str] = None
    response_size: int = 0

@dataclass
class StressTestConfig:
    """压力测试配置"""
    concurrent_users: int = 10
    requests_per_user: int = 10
    ramp_up_time: int = 5  # 秒
    test_duration: int = 60  # 秒

class APIStabilityTester:
    """API稳定性测试器"""
    
    def __init__(self, base_url: str = "http://localhost:5003"):
        self.base_url = base_url
        self.test_results: List[TestResult] = []
        self.test_token = None
        self.test_user_id = None
        
        # 测试用户数据
        self.test_user = {
            "email": f"test_{int(time.time())}@example.com",
            "password": "test123456",
            "display_name": "API测试用户"
        }
        
        # 测试metadata
        self.test_metadata = {
            "section_type": "profile",
            "section_key": "personal",
            "content": {
                "age_range": "25-30岁",
                "location": "深圳",
                "living_situation": "独居",
                "pets": "无宠物"
            }
        }
        
        # 测试标签
        self.test_tags = ["Python开发", "机器学习", "创业经验"]

    def setup_test_user(self) -> bool:
        """设置测试用户"""
        print("🔧 设置测试用户...")
        
        # 1. 注册用户
        try:
            response = requests.post(
                f"{self.base_url}/api/auth/register",
                json=self.test_user,
                timeout=10
            )
            
            if response.status_code == 201:
                data = response.json()
                self.test_token = data['data']['token']
                self.test_user_id = data['data']['user_id']
                print(f"✅ 测试用户注册成功: {self.test_user_id}")
                return True
            else:
                print(f"❌ 用户注册失败: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 用户注册异常: {e}")
            return False

    def get_auth_headers(self) -> Dict[str, str]:
        """获取认证头"""
        return {
            "Authorization": f"Bearer {self.test_token}",
            "Content-Type": "application/json"
        }

    def test_health_check(self) -> TestResult:
        """测试健康检查"""
        start_time = time.time()
        try:
            response = requests.get(f"{self.base_url}/api/system/health", timeout=5)
            response_time = time.time() - start_time
            
            return TestResult(
                endpoint="/api/system/health",
                method="GET",
                status_code=response.status_code,
                response_time=response_time,
                success=response.status_code == 200,
                response_size=len(response.content)
            )
        except Exception as e:
            return TestResult(
                endpoint="/api/system/health",
                method="GET", 
                status_code=0,
                response_time=time.time() - start_time,
                success=False,
                error_message=str(e)
            )

    def test_auth_endpoints(self) -> List[TestResult]:
        """测试认证相关端点"""
        results = []
        
        # 测试登录
        start_time = time.time()
        try:
            response = requests.post(
                f"{self.base_url}/api/auth/login",
                json={
                    "email": self.test_user["email"],
                    "password": self.test_user["password"]
                },
                timeout=10
            )
            response_time = time.time() - start_time
            
            results.append(TestResult(
                endpoint="/api/auth/login",
                method="POST",
                status_code=response.status_code,
                response_time=response_time,
                success=response.status_code == 200,
                response_size=len(response.content)
            ))
        except Exception as e:
            results.append(TestResult(
                endpoint="/api/auth/login",
                method="POST",
                status_code=0,
                response_time=time.time() - start_time,
                success=False,
                error_message=str(e)
            ))

        # 测试获取用户信息
        start_time = time.time()
        try:
            response = requests.get(
                f"{self.base_url}/api/auth/me",
                headers=self.get_auth_headers(),
                timeout=10
            )
            response_time = time.time() - start_time
            
            results.append(TestResult(
                endpoint="/api/auth/me",
                method="GET",
                status_code=response.status_code,
                response_time=response_time,
                success=response.status_code == 200,
                response_size=len(response.content)
            ))
        except Exception as e:
            results.append(TestResult(
                endpoint="/api/auth/me",
                method="GET",
                status_code=0,
                response_time=time.time() - start_time,
                success=False,
                error_message=str(e)
            ))
            
        return results

    def test_metadata_endpoints(self) -> List[TestResult]:
        """测试metadata相关端点"""
        results = []
        
        # 测试创建metadata
        start_time = time.time()
        try:
            response = requests.post(
                f"{self.base_url}/api/profile/metadata",
                json=self.test_metadata,
                headers=self.get_auth_headers(),
                timeout=10
            )
            response_time = time.time() - start_time
            
            results.append(TestResult(
                endpoint="/api/profile/metadata",
                method="POST",
                status_code=response.status_code,
                response_time=response_time,
                success=response.status_code in [200, 201],
                response_size=len(response.content)
            ))
        except Exception as e:
            results.append(TestResult(
                endpoint="/api/profile/metadata",
                method="POST",
                status_code=0,
                response_time=time.time() - start_time,
                success=False,
                error_message=str(e)
            ))

        # 测试获取metadata
        start_time = time.time()
        try:
            response = requests.get(
                f"{self.base_url}/api/profile/metadata",
                headers=self.get_auth_headers(),
                timeout=10
            )
            response_time = time.time() - start_time
            
            results.append(TestResult(
                endpoint="/api/profile/metadata",
                method="GET",
                status_code=response.status_code,
                response_time=response_time,
                success=response.status_code == 200,
                response_size=len(response.content)
            ))
        except Exception as e:
            results.append(TestResult(
                endpoint="/api/profile/metadata",
                method="GET",
                status_code=0,
                response_time=time.time() - start_time,
                success=False,
                error_message=str(e)
            ))
            
        return results

    def test_tags_endpoints(self) -> List[TestResult]:
        """测试标签相关端点"""
        results = []
        
        # 测试生成标签
        start_time = time.time()
        try:
            response = requests.post(
                f"{self.base_url}/api/tags/generate",
                json={"request_type": "找队友"},
                headers=self.get_auth_headers(),
                timeout=30  # 标签生成可能需要更长时间
            )
            response_time = time.time() - start_time
            
            results.append(TestResult(
                endpoint="/api/tags/generate",
                method="POST",
                status_code=response.status_code,
                response_time=response_time,
                success=response.status_code == 200,
                response_size=len(response.content)
            ))
        except Exception as e:
            results.append(TestResult(
                endpoint="/api/tags/generate",
                method="POST",
                status_code=0,
                response_time=time.time() - start_time,
                success=False,
                error_message=str(e)
            ))

        # 测试手动添加标签
        start_time = time.time()
        try:
            response = requests.post(
                f"{self.base_url}/api/tags/manual",
                json={"tags": self.test_tags},
                headers=self.get_auth_headers(),
                timeout=10
            )
            response_time = time.time() - start_time
            
            results.append(TestResult(
                endpoint="/api/tags/manual",
                method="POST",
                status_code=response.status_code,
                response_time=response_time,
                success=response.status_code == 200,
                response_size=len(response.content)
            ))
        except Exception as e:
            results.append(TestResult(
                endpoint="/api/tags/manual",
                method="POST",
                status_code=0,
                response_time=time.time() - start_time,
                success=False,
                error_message=str(e)
            ))

        # 测试获取用户标签
        start_time = time.time()
        try:
            response = requests.get(
                f"{self.base_url}/api/tags/user",
                headers=self.get_auth_headers(),
                timeout=10
            )
            response_time = time.time() - start_time
            
            results.append(TestResult(
                endpoint="/api/tags/user",
                method="GET",
                status_code=response.status_code,
                response_time=response_time,
                success=response.status_code == 200,
                response_size=len(response.content)
            ))
        except Exception as e:
            results.append(TestResult(
                endpoint="/api/tags/user",
                method="GET",
                status_code=0,
                response_time=time.time() - start_time,
                success=False,
                error_message=str(e)
            ))
            
        return results

    def test_matching_endpoints(self) -> List[TestResult]:
        """测试匹配相关端点"""
        results = []
        
        # 测试搜索匹配
        start_time = time.time()
        try:
            response = requests.post(
                f"{self.base_url}/api/match/search",
                json={
                    "description": "寻找技术合作伙伴",
                    "tags": ["Python开发", "机器学习"],
                    "match_type": "找队友",
                    "limit": 5
                },
                headers=self.get_auth_headers(),
                timeout=30
            )
            response_time = time.time() - start_time
            
            results.append(TestResult(
                endpoint="/api/match/search",
                method="POST",
                status_code=response.status_code,
                response_time=response_time,
                success=response.status_code == 200,
                response_size=len(response.content)
            ))
        except Exception as e:
            results.append(TestResult(
                endpoint="/api/match/search",
                method="POST",
                status_code=0,
                response_time=time.time() - start_time,
                success=False,
                error_message=str(e)
            ))
            
        return results

    def test_error_handling(self) -> List[TestResult]:
        """测试错误处理"""
        results = []
        
        # 测试无效token
        start_time = time.time()
        try:
            response = requests.get(
                f"{self.base_url}/api/auth/me",
                headers={"Authorization": "Bearer invalid_token"},
                timeout=10
            )
            response_time = time.time() - start_time
            
            results.append(TestResult(
                endpoint="/api/auth/me (invalid token)",
                method="GET",
                status_code=response.status_code,
                response_time=response_time,
                success=response.status_code == 401,  # 应该返回401
                response_size=len(response.content)
            ))
        except Exception as e:
            results.append(TestResult(
                endpoint="/api/auth/me (invalid token)",
                method="GET",
                status_code=0,
                response_time=time.time() - start_time,
                success=False,
                error_message=str(e)
            ))

        # 测试无效数据
        start_time = time.time()
        try:
            response = requests.post(
                f"{self.base_url}/api/auth/register",
                json={"email": "invalid_email"},  # 缺少必要字段
                timeout=10
            )
            response_time = time.time() - start_time
            
            results.append(TestResult(
                endpoint="/api/auth/register (invalid data)",
                method="POST",
                status_code=response.status_code,
                response_time=response_time,
                success=response.status_code == 400,  # 应该返回400
                response_size=len(response.content)
            ))
        except Exception as e:
            results.append(TestResult(
                endpoint="/api/auth/register (invalid data)",
                method="POST",
                status_code=0,
                response_time=time.time() - start_time,
                success=False,
                error_message=str(e)
            ))
            
        return results

    def run_concurrent_load_test(self, config: StressTestConfig) -> List[TestResult]:
        """运行并发负载测试"""
        print(f"🔥 开始负载测试: {config.concurrent_users}个并发用户, 每用户{config.requests_per_user}个请求")
        
        results = []
        
        def make_request(user_id: int, request_id: int):
            """单个请求函数"""
            start_time = time.time()
            try:
                # 随机选择一个端点进行测试
                endpoint = random.choice([
                    "/api/system/health",
                    "/api/system/stats",
                ])
                
                response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                response_time = time.time() - start_time
                
                return TestResult(
                    endpoint=f"{endpoint} (load test user_{user_id})",
                    method="GET",
                    status_code=response.status_code,
                    response_time=response_time,
                    success=response.status_code == 200,
                    response_size=len(response.content)
                )
            except Exception as e:
                return TestResult(
                    endpoint=f"load test user_{user_id}",
                    method="GET",
                    status_code=0,
                    response_time=time.time() - start_time,
                    success=False,
                    error_message=str(e)
                )

        # 使用线程池执行并发请求
        with ThreadPoolExecutor(max_workers=config.concurrent_users) as executor:
            futures = []
            
            # 提交所有任务
            for user_id in range(config.concurrent_users):
                for request_id in range(config.requests_per_user):
                    future = executor.submit(make_request, user_id, request_id)
                    futures.append(future)
                    
                    # 添加渐进加载延迟
                    if config.ramp_up_time > 0:
                        time.sleep(config.ramp_up_time / config.concurrent_users)
            
            # 收集结果
            for future in as_completed(futures):
                try:
                    result = future.result(timeout=30)
                    results.append(result)
                except Exception as e:
                    results.append(TestResult(
                        endpoint="load test (timeout)",
                        method="GET",
                        status_code=0,
                        response_time=30.0,
                        success=False,
                        error_message=str(e)
                    ))
        
        return results

    def analyze_results(self, results: List[TestResult]) -> Dict[str, Any]:
        """分析测试结果"""
        if not results:
            return {"error": "没有测试结果"}
            
        total_tests = len(results)
        successful_tests = sum(1 for r in results if r.success)
        failed_tests = total_tests - successful_tests
        
        response_times = [r.response_time for r in results if r.response_time > 0]
        
        analysis = {
            "总测试数": total_tests,
            "成功测试": successful_tests,
            "失败测试": failed_tests,
            "成功率": f"{(successful_tests/total_tests)*100:.2f}%" if total_tests > 0 else "0%",
            "响应时间列表": response_times,
            "响应时间统计": {
                "平均": f"{statistics.mean(response_times):.3f}秒" if response_times else "N/A",
                "中位数": f"{statistics.median(response_times):.3f}秒" if response_times else "N/A",
                "最小": f"{min(response_times):.3f}秒" if response_times else "N/A",
                "最大": f"{max(response_times):.3f}秒" if response_times else "N/A",
                "标准差": f"{statistics.stdev(response_times):.3f}秒" if len(response_times) > 1 else "N/A"
            },
            "状态码分布": {},
            "失败详情": []
        }
        
        # 统计状态码分布
        status_counts = {}
        for result in results:
            status = result.status_code
            status_counts[status] = status_counts.get(status, 0) + 1
        analysis["状态码分布"] = status_counts
        
        # 收集失败详情
        for result in results:
            if not result.success:
                analysis["失败详情"].append({
                    "端点": result.endpoint,
                    "方法": result.method,
                    "状态码": result.status_code,
                    "错误": result.error_message,
                    "响应时间": f"{result.response_time:.3f}秒"
                })
        
        return analysis

    def generate_report(self, results: List[TestResult], analysis: Dict[str, Any]) -> str:
        """生成测试报告"""
        report = f"""
# API 稳定性测试报告

## 📊 测试概览
- **测试时间**: {time.strftime('%Y-%m-%d %H:%M:%S')}
- **API地址**: {self.base_url}
- **总测试数**: {analysis['总测试数']}
- **成功率**: {analysis['成功率']}

## 📈 性能指标
- **平均响应时间**: {analysis['响应时间统计']['平均']}
- **响应时间中位数**: {analysis['响应时间统计']['中位数']}
- **最快响应**: {analysis['响应时间统计']['最小']}
- **最慢响应**: {analysis['响应时间统计']['最大']}
- **响应时间标准差**: {analysis['响应时间统计']['标准差']}

## 📋 状态码分布
"""
        
        for status, count in analysis['状态码分布'].items():
            report += f"- **{status}**: {count}次\n"
        
        report += "\n## ✅ 成功测试详情\n"
        for result in results:
            if result.success:
                report += f"- {result.method} {result.endpoint}: {result.response_time:.3f}秒\n"
        
        if analysis['失败详情']:
            report += "\n## ❌ 失败测试详情\n"
            for failure in analysis['失败详情']:
                report += f"- {failure['方法']} {failure['端点']}: {failure['状态码']} - {failure['错误']}\n"
        
        report += f"""
## 🎯 稳定性评估

基于测试结果，API稳定性评估:

- **功能稳定性**: {'🟢 良好' if analysis['成功率'].replace('%', '') != '0' and float(analysis['成功率'].replace('%', '')) >= 95 else '🟡 一般' if float(analysis['成功率'].replace('%', '')) >= 80 else '🔴 需要改进'}
- **性能表现**: {'🟢 良好' if analysis.get('响应时间列表') and statistics.mean(analysis['响应时间列表']) < 2.0 else '🟡 一般' if analysis.get('响应时间列表') and statistics.mean(analysis['响应时间列表']) < 5.0 else '🔴 需要优化'}
- **错误处理**: {'🟢 良好' if analysis['失败测试'] == 0 else '🟡 可接受' if analysis['失败测试'] < analysis['总测试数'] * 0.1 else '🔴 需要改进'}

## 📝 建议

"""
        
        # 根据测试结果给出建议
        success_rate = float(analysis['成功率'].replace('%', ''))
        response_times = analysis.get('响应时间列表', [])
        avg_response_time = statistics.mean(response_times) if response_times else 0
        
        if success_rate < 95:
            report += "- 成功率偏低，建议检查API端点实现和错误处理\n"
        
        if avg_response_time > 2.0:
            report += "- 平均响应时间较长，建议优化数据库查询和业务逻辑\n"
            
        if analysis['失败测试'] > 0:
            report += "- 存在失败的测试用例，建议修复相关问题后重新测试\n"
            
        if success_rate >= 95 and avg_response_time <= 2.0 and analysis['失败测试'] == 0:
            report += "- 🎉 API表现优异，可以放心部署到生产环境\n"
        
        return report

    def run_full_stability_test(self) -> bool:
        """运行完整的稳定性测试"""
        print("🚀 开始API稳定性测试")
        print("=" * 60)
        
        all_results = []
        
        # 1. 健康检查
        print("\n1️⃣ 健康检查测试...")
        health_result = self.test_health_check()
        all_results.append(health_result)
        
        if not health_result.success:
            print("❌ API服务器不可用，停止测试")
            return False
            
        print("✅ API服务器运行正常")
        
        # 2. 设置测试用户
        if not self.setup_test_user():
            print("❌ 无法设置测试用户，跳过需要认证的测试")
            # 可以继续进行不需要认证的测试
        
        # 3. 认证测试
        print("\n2️⃣ 认证功能测试...")
        auth_results = self.test_auth_endpoints()
        all_results.extend(auth_results)
        
        # 4. Metadata测试
        print("\n3️⃣ Metadata功能测试...")
        metadata_results = self.test_metadata_endpoints()
        all_results.extend(metadata_results)
        
        # 5. 标签测试
        print("\n4️⃣ 标签功能测试...")
        tags_results = self.test_tags_endpoints()
        all_results.extend(tags_results)
        
        # 6. 匹配测试
        print("\n5️⃣ 匹配功能测试...")
        matching_results = self.test_matching_endpoints()
        all_results.extend(matching_results)
        
        # 7. 错误处理测试
        print("\n6️⃣ 错误处理测试...")
        error_results = self.test_error_handling()
        all_results.extend(error_results)
        
        # 8. 负载测试
        print("\n7️⃣ 负载测试...")
        load_config = StressTestConfig(
            concurrent_users=5,  # 适中的并发数
            requests_per_user=10,
            ramp_up_time=2
        )
        load_results = self.run_concurrent_load_test(load_config)
        all_results.extend(load_results)
        
        # 9. 分析结果
        print("\n8️⃣ 分析测试结果...")
        analysis = self.analyze_results(all_results)
        
        # 10. 生成报告
        report = self.generate_report(all_results, analysis)
        
        # 保存报告
        report_file = f"stability_test_report_{int(time.time())}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n📄 测试报告已保存: {report_file}")
        print("\n" + "=" * 60)
        print(report)
        
        # 判断测试是否通过
        success_rate = float(analysis['成功率'].replace('%', ''))
        return success_rate >= 80  # 80%以上成功率认为测试通过

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='API稳定性测试工具')
    parser.add_argument('--url', default='http://localhost:5003', help='API服务器地址')
    parser.add_argument('--concurrent', type=int, default=5, help='并发用户数')
    parser.add_argument('--requests', type=int, default=10, help='每用户请求数')
    
    args = parser.parse_args()
    
    tester = APIStabilityTester(args.url)
    
    # 更新负载测试配置
    load_config = StressTestConfig(
        concurrent_users=args.concurrent,
        requests_per_user=args.requests
    )
    
    success = tester.run_full_stability_test()
    
    if success:
        print("\n🎉 API稳定性测试通过！可以安全部署。")
        sys.exit(0)
    else:
        print("\n⚠️ API稳定性测试未完全通过，建议修复问题后重新测试。")
        sys.exit(1)

if __name__ == "__main__":
    main() 