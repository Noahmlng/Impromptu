#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API 性能监控工具

实时监控API的性能指标，包括：
- 响应时间
- 吞吐量
- 错误率
- 资源使用情况
"""

import requests
import json
import time
import threading
import psutil
import statistics
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
import sys
import os
import csv
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

@dataclass
class PerformanceMetric:
    """性能指标数据类"""
    timestamp: datetime
    endpoint: str
    method: str
    response_time: float
    status_code: int
    success: bool
    response_size: int = 0
    cpu_usage: float = 0.0
    memory_usage: float = 0.0

@dataclass
class MonitoringStats:
    """监控统计数据"""
    start_time: datetime = field(default_factory=datetime.now)
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    response_times: List[float] = field(default_factory=list)
    error_rates: List[float] = field(default_factory=list)
    cpu_usage_history: List[float] = field(default_factory=list)
    memory_usage_history: List[float] = field(default_factory=list)

class APIPerformanceMonitor:
    """API性能监控器"""
    
    def __init__(self, base_url: str = "http://localhost:5003", monitor_duration: int = 300):
        self.base_url = base_url
        self.monitor_duration = monitor_duration  # 监控时长（秒）
        self.metrics: List[PerformanceMetric] = []
        self.stats = MonitoringStats()
        self.monitoring_active = False
        
        # 测试端点配置
        self.test_endpoints = [
            {"endpoint": "/api/system/health", "method": "GET", "weight": 10},
            {"endpoint": "/api/system/stats", "method": "GET", "weight": 5},
        ]
        
        # 认证用户配置
        self.test_user = {
            "email": f"monitor_test_{int(time.time())}@example.com",
            "password": "MonitorTest123!",
            "display_name": "性能监控测试用户"
        }
        self.auth_token = None
        
    def setup_test_user(self) -> bool:
        """设置测试用户"""
        try:
            response = requests.post(
                f"{self.base_url}/api/auth/register",
                json=self.test_user,
                timeout=10
            )
            
            if response.status_code == 201:
                data = response.json()
                self.auth_token = data['data']['token']
                
                # 添加需要认证的端点
                self.test_endpoints.extend([
                    {"endpoint": "/api/auth/me", "method": "GET", "weight": 3},
                    {"endpoint": "/api/profile/metadata", "method": "GET", "weight": 2},
                ])
                
                return True
            return False
        except Exception as e:
            print(f"⚠️ 设置测试用户失败: {e}")
            return False
    
    def get_auth_headers(self) -> Dict[str, str]:
        """获取认证头"""
        return {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        } if self.auth_token else {"Content-Type": "application/json"}
    
    def get_system_metrics(self) -> Dict[str, float]:
        """获取系统资源使用情况"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory_percent = psutil.virtual_memory().percent
            return {
                "cpu_usage": cpu_percent,
                "memory_usage": memory_percent
            }
        except Exception:
            return {"cpu_usage": 0.0, "memory_usage": 0.0}
    
    def make_request(self, endpoint_config: Dict[str, Any]) -> PerformanceMetric:
        """发送请求并记录性能指标"""
        endpoint = endpoint_config["endpoint"]
        method = endpoint_config["method"]
        
        start_time = time.time()
        system_metrics = self.get_system_metrics()
        
        try:
            headers = self.get_auth_headers() if endpoint.startswith("/api/auth") or endpoint.startswith("/api/profile") else {}
            
            if method == "GET":
                response = requests.get(f"{self.base_url}{endpoint}", headers=headers, timeout=10)
            elif method == "POST":
                response = requests.post(f"{self.base_url}{endpoint}", headers=headers, timeout=10)
            else:
                raise ValueError(f"不支持的HTTP方法: {method}")
            
            response_time = time.time() - start_time
            
            return PerformanceMetric(
                timestamp=datetime.now(),
                endpoint=endpoint,
                method=method,
                response_time=response_time,
                status_code=response.status_code,
                success=200 <= response.status_code < 400,
                response_size=len(response.content) if response.content else 0,
                cpu_usage=system_metrics["cpu_usage"],
                memory_usage=system_metrics["memory_usage"]
            )
            
        except Exception as e:
            return PerformanceMetric(
                timestamp=datetime.now(),
                endpoint=endpoint,
                method=method,
                response_time=time.time() - start_time,
                status_code=0,
                success=False,
                cpu_usage=system_metrics["cpu_usage"],
                memory_usage=system_metrics["memory_usage"]
            )
    
    def continuous_monitoring_worker(self):
        """持续监控工作线程"""
        print(f"🔄 开始持续监控，时长: {self.monitor_duration}秒")
        
        end_time = time.time() + self.monitor_duration
        request_interval = 2  # 每2秒发送一次请求
        
        while time.time() < end_time and self.monitoring_active:
            # 随机选择一个端点进行测试
            import random
            endpoint_config = random.choices(
                self.test_endpoints,
                weights=[ep["weight"] for ep in self.test_endpoints],
                k=1
            )[0]
            
            # 发送请求
            metric = self.make_request(endpoint_config)
            self.metrics.append(metric)
            
            # 更新统计数据
            self.update_stats(metric)
            
            # 等待下次请求
            time.sleep(request_interval)
        
        self.monitoring_active = False
        print("✅ 监控完成")
    
    def update_stats(self, metric: PerformanceMetric):
        """更新统计数据"""
        self.stats.total_requests += 1
        
        if metric.success:
            self.stats.successful_requests += 1
        else:
            self.stats.failed_requests += 1
        
        self.stats.response_times.append(metric.response_time)
        self.stats.cpu_usage_history.append(metric.cpu_usage)
        self.stats.memory_usage_history.append(metric.memory_usage)
        
        # 计算错误率
        error_rate = (self.stats.failed_requests / self.stats.total_requests) * 100
        self.stats.error_rates.append(error_rate)
    
    def get_real_time_stats(self) -> Dict[str, Any]:
        """获取实时统计数据"""
        if not self.stats.response_times:
            return {"error": "没有可用数据"}
        
        recent_metrics = self.metrics[-10:]  # 最近10个请求
        recent_response_times = [m.response_time for m in recent_metrics if m.success]
        
        return {
            "总请求数": self.stats.total_requests,
            "成功请求": self.stats.successful_requests,
            "失败请求": self.stats.failed_requests,
            "成功率": f"{(self.stats.successful_requests / self.stats.total_requests * 100):.2f}%" if self.stats.total_requests > 0 else "0%",
            "平均响应时间": f"{statistics.mean(self.stats.response_times):.3f}秒",
            "最近响应时间": f"{statistics.mean(recent_response_times):.3f}秒" if recent_response_times else "N/A",
            "当前错误率": f"{self.stats.error_rates[-1]:.2f}%" if self.stats.error_rates else "0%",
            "CPU使用率": f"{self.stats.cpu_usage_history[-1]:.1f}%" if self.stats.cpu_usage_history else "0%",
            "内存使用率": f"{self.stats.memory_usage_history[-1]:.1f}%" if self.stats.memory_usage_history else "0%"
        }
    
    def print_real_time_stats(self):
        """打印实时统计信息"""
        while self.monitoring_active:
            if self.stats.total_requests > 0:
                stats = self.get_real_time_stats()
                
                # 清屏并打印统计信息
                os.system('cls' if os.name == 'nt' else 'clear')
                print("📊 API 性能监控实时数据")
                print("=" * 50)
                print(f"📈 总请求数: {stats['总请求数']}")
                print(f"✅ 成功率: {stats['成功率']}")
                print(f"⏱️  平均响应时间: {stats['平均响应时间']}")
                print(f"⚡ 最近响应时间: {stats['最近响应时间']}")
                print(f"❌ 当前错误率: {stats['当前错误率']}")
                print(f"🖥️  CPU使用率: {stats['CPU使用率']}")
                print(f"💾 内存使用率: {stats['内存使用率']}")
                print("\n按 Ctrl+C 停止监控")
                print("=" * 50)
            
            time.sleep(5)  # 每5秒更新一次显示
    
    def analyze_performance_trends(self) -> Dict[str, Any]:
        """分析性能趋势"""
        if len(self.metrics) < 10:
            return {"error": "数据不足，无法分析趋势"}
        
        # 分段分析（每分钟一段）
        segments = []
        current_segment = []
        segment_start = self.metrics[0].timestamp
        
        for metric in self.metrics:
            if metric.timestamp - segment_start < timedelta(minutes=1):
                current_segment.append(metric)
            else:
                if current_segment:
                    segments.append(current_segment)
                current_segment = [metric]
                segment_start = metric.timestamp
        
        if current_segment:
            segments.append(current_segment)
        
        # 计算每段的统计数据
        trend_data = []
        for i, segment in enumerate(segments):
            successful = [m for m in segment if m.success]
            if successful:
                avg_response_time = statistics.mean([m.response_time for m in successful])
                success_rate = len(successful) / len(segment) * 100
                avg_cpu = statistics.mean([m.cpu_usage for m in segment])
                avg_memory = statistics.mean([m.memory_usage for m in segment])
                
                trend_data.append({
                    "分钟": i + 1,
                    "平均响应时间": avg_response_time,
                    "成功率": success_rate,
                    "CPU使用率": avg_cpu,
                    "内存使用率": avg_memory,
                    "请求数": len(segment)
                })
        
        # 分析趋势
        response_times = [d["平均响应时间"] for d in trend_data]
        success_rates = [d["成功率"] for d in trend_data]
        
        trends = {
            "响应时间趋势": "稳定",
            "成功率趋势": "稳定",
            "资源使用趋势": "稳定"
        }
        
        if len(response_times) >= 3:
            # 简单的趋势分析
            if response_times[-1] > response_times[0] * 1.2:
                trends["响应时间趋势"] = "上升"
            elif response_times[-1] < response_times[0] * 0.8:
                trends["响应时间趋势"] = "下降"
        
        if len(success_rates) >= 3:
            if success_rates[-1] < success_rates[0] - 10:
                trends["成功率趋势"] = "下降"
            elif success_rates[-1] > success_rates[0] + 10:
                trends["成功率趋势"] = "上升"
        
        return {
            "分段数据": trend_data,
            "趋势分析": trends,
            "总体评估": self.get_overall_assessment(trend_data)
        }
    
    def get_overall_assessment(self, trend_data: List[Dict]) -> str:
        """获取总体评估"""
        if not trend_data:
            return "数据不足"
        
        avg_response_time = statistics.mean([d["平均响应时间"] for d in trend_data])
        avg_success_rate = statistics.mean([d["成功率"] for d in trend_data])
        avg_cpu = statistics.mean([d["CPU使用率"] for d in trend_data])
        avg_memory = statistics.mean([d["内存使用率"] for d in trend_data])
        
        if avg_response_time < 1.0 and avg_success_rate > 95 and avg_cpu < 80 and avg_memory < 80:
            return "🟢 性能优异"
        elif avg_response_time < 3.0 and avg_success_rate > 90 and avg_cpu < 90 and avg_memory < 90:
            return "🟡 性能良好"
        else:
            return "🔴 性能需要优化"
    
    def export_metrics_to_csv(self, filename: str = None) -> str:
        """导出性能指标到CSV文件"""
        if not filename:
            filename = f"performance_metrics_{int(time.time())}.csv"
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'timestamp', 'endpoint', 'method', 'response_time', 
                'status_code', 'success', 'response_size', 
                'cpu_usage', 'memory_usage'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for metric in self.metrics:
                writer.writerow({
                    'timestamp': metric.timestamp.isoformat(),
                    'endpoint': metric.endpoint,
                    'method': metric.method,
                    'response_time': metric.response_time,
                    'status_code': metric.status_code,
                    'success': metric.success,
                    'response_size': metric.response_size,
                    'cpu_usage': metric.cpu_usage,
                    'memory_usage': metric.memory_usage
                })
        
        return filename
    
    def generate_performance_report(self) -> str:
        """生成性能监控报告"""
        if not self.metrics:
            return "没有性能数据可供分析"
        
        # 基础统计
        successful_metrics = [m for m in self.metrics if m.success]
        
        response_times = [m.response_time for m in successful_metrics]
        all_response_times = [m.response_time for m in self.metrics]
        
        # 分析趋势
        trend_analysis = self.analyze_performance_trends()
        
        # 计算百分位数
        def percentile(data, p):
            return sorted(data)[int(len(data) * p / 100)] if data else 0
        
        report = f"""
# API 性能监控报告

## 📊 监控概览
- **监控时间**: {self.stats.start_time.strftime('%Y-%m-%d %H:%M:%S')} 到 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **监控时长**: {self.monitor_duration}秒
- **API地址**: {self.base_url}
- **总请求数**: {self.stats.total_requests}

## 📈 成功率统计
- **成功请求**: {self.stats.successful_requests}
- **失败请求**: {self.stats.failed_requests}
- **成功率**: {(self.stats.successful_requests / self.stats.total_requests * 100):.2f}%

## ⏱️ 响应时间统计
- **平均响应时间**: {statistics.mean(response_times):.3f}秒
- **中位数响应时间**: {statistics.median(response_times):.3f}秒
- **50th百分位**: {percentile(response_times, 50):.3f}秒
- **90th百分位**: {percentile(response_times, 90):.3f}秒
- **95th百分位**: {percentile(response_times, 95):.3f}秒
- **99th百分位**: {percentile(response_times, 99):.3f}秒
- **最快响应**: {min(response_times):.3f}秒
- **最慢响应**: {max(response_times):.3f}秒

## 🖥️ 系统资源使用
- **平均CPU使用率**: {statistics.mean(self.stats.cpu_usage_history):.1f}%
- **最高CPU使用率**: {max(self.stats.cpu_usage_history):.1f}%
- **平均内存使用率**: {statistics.mean(self.stats.memory_usage_history):.1f}%
- **最高内存使用率**: {max(self.stats.memory_usage_history):.1f}%

## 📊 端点性能分析
"""
        
        # 按端点分析
        endpoint_stats = {}
        for metric in successful_metrics:
            if metric.endpoint not in endpoint_stats:
                endpoint_stats[metric.endpoint] = []
            endpoint_stats[metric.endpoint].append(metric.response_time)
        
        for endpoint, times in endpoint_stats.items():
            report += f"""
### {endpoint}
- **请求数**: {len(times)}
- **平均响应时间**: {statistics.mean(times):.3f}秒
- **最快响应**: {min(times):.3f}秒
- **最慢响应**: {max(times):.3f}秒
"""
        
        # 添加趋势分析
        if "分段数据" in trend_analysis:
            report += "\n## 📈 性能趋势分析\n"
            for trend_name, trend_value in trend_analysis["趋势分析"].items():
                report += f"- **{trend_name}**: {trend_value}\n"
            
            report += f"\n**总体评估**: {trend_analysis['总体评估']}\n"
        
        # 性能建议
        avg_response_time = statistics.mean(response_times)
        success_rate = (self.stats.successful_requests / self.stats.total_requests * 100)
        avg_cpu = statistics.mean(self.stats.cpu_usage_history)
        
        report += "\n## 📝 性能优化建议\n"
        
        if avg_response_time > 3.0:
            report += "- ⚠️ 平均响应时间较长，建议优化数据库查询和业务逻辑\n"
        
        if success_rate < 95:
            report += "- ⚠️ 成功率偏低，建议检查错误处理和系统稳定性\n"
        
        if avg_cpu > 80:
            report += "- ⚠️ CPU使用率较高，建议优化计算密集型操作\n"
        
        if percentile(response_times, 95) > percentile(response_times, 50) * 3:
            report += "- ⚠️ 响应时间波动较大，建议检查系统负载和资源瓶颈\n"
        
        if avg_response_time <= 2.0 and success_rate >= 95 and avg_cpu <= 70:
            report += "- 🎉 API性能表现优异，可以安全部署到生产环境\n"
        
        return report
    
    def start_monitoring(self):
        """开始性能监控"""
        print("🚀 启动API性能监控")
        print("=" * 50)
        
        # 检查API可用性
        try:
            response = requests.get(f"{self.base_url}/api/system/health", timeout=10)
            if response.status_code != 200:
                print(f"❌ API不可用: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 无法连接到API: {e}")
            return False
        
        print("✅ API连接正常")
        
        # 设置测试用户
        if self.setup_test_user():
            print("✅ 测试用户设置成功")
        else:
            print("⚠️ 测试用户设置失败，将跳过需要认证的端点")
        
        # 开始监控
        self.monitoring_active = True
        
        # 启动监控线程
        monitor_thread = threading.Thread(target=self.continuous_monitoring_worker)
        stats_thread = threading.Thread(target=self.print_real_time_stats)
        
        monitor_thread.start()
        stats_thread.start()
        
        try:
            monitor_thread.join()
            stats_thread.join()
        except KeyboardInterrupt:
            print("\n⏹️ 监控已停止")
            self.monitoring_active = False
        
        # 生成报告
        report = self.generate_performance_report()
        
        # 保存报告
        report_file = f"performance_report_{int(time.time())}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        # 导出CSV数据
        csv_file = self.export_metrics_to_csv()
        
        print(f"\n📄 性能报告已保存: {report_file}")
        print(f"📊 性能数据已导出: {csv_file}")
        print("\n" + "=" * 50)
        print(report)
        
        return True

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='API性能监控工具')
    parser.add_argument('--url', default='http://localhost:5003', help='API服务器地址')
    parser.add_argument('--duration', type=int, default=300, help='监控时长（秒）')
    
    args = parser.parse_args()
    
    monitor = APIPerformanceMonitor(args.url, args.duration)
    
    try:
        monitor.start_monitoring()
    except KeyboardInterrupt:
        print("\n👋 监控已停止")

if __name__ == "__main__":
    main() 