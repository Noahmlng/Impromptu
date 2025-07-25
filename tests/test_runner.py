#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API 测试运行器

统一管理和执行所有测试套件：
- 功能测试
- 性能测试
- 安全测试
- 负载测试
- 监控测试
"""

import subprocess
import sys
import time
import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import concurrent.futures

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

@dataclass
class TestSuite:
    """测试套件配置"""
    name: str
    script_path: str
    description: str
    required: bool = True
    timeout: int = 300  # 超时时间（秒）
    args: List[str] = None

@dataclass
class TestResult:
    """测试结果"""
    suite_name: str
    success: bool
    duration: float
    exit_code: int
    stdout: str
    stderr: str
    error_message: Optional[str] = None

class APITestRunner:
    """API测试运行器"""
    
    def __init__(self, api_url: str = "http://localhost:5003"):
        self.api_url = api_url
        self.test_results: List[TestResult] = []
        
        # 定义测试套件
        self.test_suites = [
            TestSuite(
                name="功能稳定性测试",
                script_path="tests/test_api_stability.py",
                description="测试所有API端点的功能性、性能和稳定性",
                required=True,
                timeout=600,
                args=["--url", api_url]
            ),
            TestSuite(
                name="安全测试",
                script_path="tests/test_security.py", 
                description="测试API的安全漏洞和权限控制",
                required=True,
                timeout=300,
                args=["--url", api_url]
            ),
            TestSuite(
                name="基础功能测试",
                script_path="scripts/demo/test_api_client.py",
                description="基础API功能验证",
                required=False,
                timeout=120,
                args=[]
            ),
        ]
    
    def check_api_availability(self) -> bool:
        """检查API是否可用"""
        print("🔍 检查API可用性...")
        
        try:
            import requests
            response = requests.get(f"{self.api_url}/api/system/health", timeout=10)
            if response.status_code == 200:
                print("✅ API服务器运行正常")
                return True
            else:
                print(f"❌ API返回错误状态码: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 无法连接到API服务器: {e}")
            print(f"请确保API服务器在 {self.api_url} 上运行")
            return False
    
    def run_single_test(self, test_suite: TestSuite) -> TestResult:
        """运行单个测试套件"""
        print(f"\n🧪 运行测试: {test_suite.name}")
        print(f"📝 描述: {test_suite.description}")
        print(f"⏱️ 超时时间: {test_suite.timeout}秒")
        print("-" * 60)
        
        start_time = time.time()
        
        try:
            # 构建命令
            cmd = [sys.executable, test_suite.script_path]
            if test_suite.args:
                cmd.extend(test_suite.args)
            
            # 运行测试
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=test_suite.timeout,
                cwd=project_root
            )
            
            duration = time.time() - start_time
            
            success = result.returncode == 0
            
            print(f"{'✅' if success else '❌'} {test_suite.name} - {duration:.2f}秒")
            
            if not success and result.stderr:
                print(f"错误信息: {result.stderr[:200]}...")
            
            return TestResult(
                suite_name=test_suite.name,
                success=success,
                duration=duration,
                exit_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr
            )
            
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            print(f"⏰ {test_suite.name} 超时 - {duration:.2f}秒")
            
            return TestResult(
                suite_name=test_suite.name,
                success=False,
                duration=duration,
                exit_code=-1,
                stdout="",
                stderr="",
                error_message="测试超时"
            )
            
        except Exception as e:
            duration = time.time() - start_time
            print(f"💥 {test_suite.name} 异常 - {str(e)}")
            
            return TestResult(
                suite_name=test_suite.name,
                success=False,
                duration=duration,
                exit_code=-2,
                stdout="",
                stderr="",
                error_message=str(e)
            )
    
    def run_parallel_tests(self, test_suites: List[TestSuite]) -> List[TestResult]:
        """并行运行测试套件"""
        print(f"🚀 并行运行 {len(test_suites)} 个测试套件")
        
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            # 提交所有测试任务
            future_to_suite = {
                executor.submit(self.run_single_test, suite): suite 
                for suite in test_suites
            }
            
            # 收集结果
            for future in concurrent.futures.as_completed(future_to_suite):
                suite = future_to_suite[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    print(f"💥 {suite.name} 执行异常: {e}")
                    results.append(TestResult(
                        suite_name=suite.name,
                        success=False,
                        duration=0,
                        exit_code=-3,
                        stdout="",
                        stderr="",
                        error_message=str(e)
                    ))
        
        return results
    
    def run_load_test(self) -> TestResult:
        """运行负载测试（可选）"""
        print("\n🔥 准备运行负载测试...")
        
        # 检查是否安装了locust
        try:
            result = subprocess.run(
                ["locust", "--version"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            
            if result.returncode != 0:
                return TestResult(
                    suite_name="负载测试",
                    success=False,
                    duration=0,
                    exit_code=-1,
                    stdout="",
                    stderr="",
                    error_message="Locust未安装"
                )
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print("⚠️ Locust未安装，跳过负载测试")
            print("安装方法: pip install locust")
            return TestResult(
                suite_name="负载测试",
                success=False,
                duration=0,
                exit_code=-1,
                stdout="",
                stderr="",
                error_message="Locust未安装"
            )
        
        # 运行简化的负载测试
        print("🔥 运行30秒负载测试...")
        start_time = time.time()
        
        try:
            result = subprocess.run([
                "locust",
                "-f", "tests/test_load_performance.py",
                "--host", self.api_url,
                "--users", "10",
                "--spawn-rate", "2", 
                "--run-time", "30s",
                "--headless"
            ], 
            capture_output=True, 
            text=True, 
            timeout=60,
            cwd=project_root
            )
            
            duration = time.time() - start_time
            success = result.returncode == 0
            
            print(f"{'✅' if success else '❌'} 负载测试完成 - {duration:.2f}秒")
            
            return TestResult(
                suite_name="负载测试",
                success=success,
                duration=duration,
                exit_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr
            )
            
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            print(f"⏰ 负载测试超时 - {duration:.2f}秒")
            
            return TestResult(
                suite_name="负载测试",
                success=False,
                duration=duration,
                exit_code=-1,
                stdout="",
                stderr="",
                error_message="负载测试超时"
            )
    
    def run_performance_monitoring(self, duration: int = 60) -> TestResult:
        """运行性能监控测试"""
        print(f"\n📊 运行性能监控测试 ({duration}秒)...")
        
        start_time = time.time()
        
        try:
            result = subprocess.run([
                sys.executable,
                "tests/test_performance_monitor.py",
                "--url", self.api_url,
                "--duration", str(duration)
            ],
            capture_output=True,
            text=True,
            timeout=duration + 30,
            cwd=project_root
            )
            
            test_duration = time.time() - start_time
            success = result.returncode == 0
            
            print(f"{'✅' if success else '❌'} 性能监控完成 - {test_duration:.2f}秒")
            
            return TestResult(
                suite_name="性能监控",
                success=success,
                duration=test_duration,
                exit_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr
            )
            
        except subprocess.TimeoutExpired:
            test_duration = time.time() - start_time
            print(f"⏰ 性能监控超时 - {test_duration:.2f}秒")
            
            return TestResult(
                suite_name="性能监控",
                success=False,
                duration=test_duration,
                exit_code=-1,
                stdout="",
                stderr="",
                error_message="性能监控超时"
            )
        except Exception as e:
            test_duration = time.time() - start_time
            print(f"💥 性能监控异常: {e}")
            
            return TestResult(
                suite_name="性能监控",
                success=False,
                duration=test_duration,
                exit_code=-2,
                stdout="",
                stderr="",
                error_message=str(e)
            )
    
    def generate_summary_report(self) -> str:
        """生成测试总结报告"""
        if not self.test_results:
            return "没有测试结果"
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r.success)
        failed_tests = total_tests - passed_tests
        total_duration = sum(r.duration for r in self.test_results)
        
        report = f"""
# API 测试总结报告

## 📊 测试概览
- **测试时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **API地址**: {self.api_url}
- **总测试套件**: {total_tests}
- **通过测试**: {passed_tests}
- **失败测试**: {failed_tests}
- **总耗时**: {total_duration:.2f}秒
- **成功率**: {(passed_tests/total_tests*100):.1f}%

## 📋 详细结果
"""
        
        for result in self.test_results:
            status_icon = "✅" if result.success else "❌"
            report += f"""
### {status_icon} {result.suite_name}
- **状态**: {'通过' if result.success else '失败'}
- **耗时**: {result.duration:.2f}秒
- **退出码**: {result.exit_code}
"""
            
            if not result.success:
                if result.error_message:
                    report += f"- **错误**: {result.error_message}\n"
                elif result.stderr:
                    report += f"- **错误信息**: {result.stderr[:200]}...\n"
        
        # 测试评估
        report += "\n## 🎯 测试评估\n"
        
        if passed_tests == total_tests:
            report += "**🟢 测试全部通过**: API已准备好部署到生产环境。\n"
        elif passed_tests >= total_tests * 0.8:
            report += "**🟡 大部分测试通过**: API基本稳定，建议修复失败的测试后部署。\n"
        else:
            report += "**🔴 多项测试失败**: API存在严重问题，不建议部署到生产环境。\n"
        
        # 部署建议
        report += "\n## 📝 部署建议\n"
        
        # 检查关键测试
        critical_tests = ["功能稳定性测试", "安全测试"]
        critical_failures = [r for r in self.test_results if not r.success and r.suite_name in critical_tests]
        
        if critical_failures:
            report += "- ⚠️ 关键测试失败，必须修复后才能部署\n"
            for failure in critical_failures:
                report += f"  - {failure.suite_name}: {failure.error_message or '检查详细错误信息'}\n"
        
        if passed_tests == total_tests:
            report += "- 🎉 所有测试通过，可以安全部署\n"
            report += "- 🚀 建议先部署到测试环境进行最终验证\n"
            report += "- 📊 考虑设置生产环境监控和告警\n"
        
        return report
    
    def save_results(self):
        """保存测试结果"""
        # 生成总结报告
        report = self.generate_summary_report()
        
        # 保存报告
        report_file = f"test_summary_report_{int(time.time())}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        # 保存详细结果为JSON
        results_data = {
            "timestamp": datetime.now().isoformat(),
            "api_url": self.api_url,
            "summary": {
                "total_tests": len(self.test_results),
                "passed_tests": sum(1 for r in self.test_results if r.success),
                "failed_tests": sum(1 for r in self.test_results if not r.success),
                "total_duration": sum(r.duration for r in self.test_results),
            },
            "results": [
                {
                    "suite_name": r.suite_name,
                    "success": r.success,
                    "duration": r.duration,
                    "exit_code": r.exit_code,
                    "error_message": r.error_message,
                    "stdout_length": len(r.stdout),
                    "stderr_length": len(r.stderr)
                }
                for r in self.test_results
            ]
        }
        
        results_file = f"test_results_{int(time.time())}.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results_data, f, indent=2, ensure_ascii=False)
        
        return report_file, results_file
    
    def run_all_tests(self, include_load_test: bool = False, include_monitoring: bool = False):
        """运行所有测试"""
        print("🚀 开始API完整测试套件")
        print("=" * 80)
        print(f"🎯 目标API: {self.api_url}")
        print(f"📅 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # 1. 检查API可用性
        if not self.check_api_availability():
            print("❌ API不可用，测试终止")
            return False
        
        # 2. 运行核心测试套件
        print("\n📦 运行核心测试套件...")
        core_results = self.run_parallel_tests(self.test_suites)
        self.test_results.extend(core_results)
        
        # 3. 运行负载测试（可选）
        if include_load_test:
            load_result = self.run_load_test()
            self.test_results.append(load_result)
        
        # 4. 运行性能监控（可选）
        if include_monitoring:
            monitoring_result = self.run_performance_monitoring(60)
            self.test_results.append(monitoring_result)
        
        # 5. 生成和保存报告
        print("\n📄 生成测试报告...")
        report_file, results_file = self.save_results()
        
        # 6. 显示总结
        print("\n" + "=" * 80)
        print("📊 测试完成！")
        print("=" * 80)
        
        report = self.generate_summary_report()
        print(report)
        
        print(f"\n📄 详细报告已保存: {report_file}")
        print(f"📊 测试数据已保存: {results_file}")
        
        # 返回是否所有关键测试都通过
        critical_tests = ["功能稳定性测试", "安全测试"]
        critical_success = all(
            r.success for r in self.test_results 
            if r.suite_name in critical_tests
        )
        
        return critical_success

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='API完整测试套件运行器')
    parser.add_argument('--url', default='http://localhost:5003', help='API服务器地址')
    parser.add_argument('--load-test', action='store_true', help='包含负载测试')
    parser.add_argument('--monitoring', action='store_true', help='包含性能监控')
    parser.add_argument('--quick', action='store_true', help='快速测试（跳过可选测试）')
    
    args = parser.parse_args()
    
    runner = APITestRunner(args.url)
    
    include_load = args.load_test and not args.quick
    include_monitoring = args.monitoring and not args.quick
    
    try:
        success = runner.run_all_tests(
            include_load_test=include_load,
            include_monitoring=include_monitoring
        )
        
        if success:
            print("\n🎉 所有关键测试通过！API可以部署。")
            sys.exit(0)
        else:
            print("\n⚠️ 部分关键测试失败，请修复后重新测试。")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️ 测试被用户中断")
        sys.exit(2)
    except Exception as e:
        print(f"\n💥 测试运行器异常: {e}")
        sys.exit(3)

if __name__ == "__main__":
    main() 