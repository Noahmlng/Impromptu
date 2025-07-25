#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API 安全测试套件

测试API的安全漏洞，包括：
- 认证和授权
- SQL注入
- XSS攻击
- 权限控制
- 敏感信息泄露
"""

import requests
import json
import time
import random
import string
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

@dataclass
class SecurityTestResult:
    """安全测试结果"""
    test_name: str
    vulnerability_type: str
    endpoint: str
    method: str
    status_code: int
    is_vulnerable: bool
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    description: str
    recommendation: str

class APISecurityTester:
    """API安全测试器"""
    
    def __init__(self, base_url: str = "http://localhost:5003"):
        self.base_url = base_url
        self.test_results: List[SecurityTestResult] = []
        
        # 测试用户
        self.test_user = {
            "email": f"security_test_{int(time.time())}@example.com",
            "password": "SecurityTest123!",
            "display_name": "安全测试用户"
        }
        
        self.valid_token = None
        self.user_id = None
    
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
                self.valid_token = data['data']['token']
                self.user_id = data['data']['user_id']
                return True
            return False
        except:
            return False
    
    def test_authentication_bypass(self) -> List[SecurityTestResult]:
        """测试认证绕过"""
        results = []
        
        # 测试无token访问受保护资源
        endpoints_to_test = [
            "/api/auth/me",
            "/api/profile/metadata",
            "/api/tags/user",
            "/api/match/search"
        ]
        
        for endpoint in endpoints_to_test:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                
                is_vulnerable = response.status_code != 401
                
                results.append(SecurityTestResult(
                    test_name="认证绕过测试",
                    vulnerability_type="Authentication Bypass",
                    endpoint=endpoint,
                    method="GET",
                    status_code=response.status_code,
                    is_vulnerable=is_vulnerable,
                    risk_level="HIGH" if is_vulnerable else "LOW",
                    description="无认证token访问受保护资源" + (
                        "成功" if is_vulnerable else "被正确拒绝"
                    ),
                    recommendation="确保所有受保护的端点都需要有效的认证token" if is_vulnerable else "认证控制正常"
                ))
            except Exception as e:
                results.append(SecurityTestResult(
                    test_name="认证绕过测试",
                    vulnerability_type="Authentication Error",
                    endpoint=endpoint,
                    method="GET",
                    status_code=0,
                    is_vulnerable=False,
                    risk_level="LOW",
                    description=f"测试异常: {str(e)}",
                    recommendation="检查API可用性"
                ))
        
        return results
    
    def test_invalid_tokens(self) -> List[SecurityTestResult]:
        """测试无效token处理"""
        results = []
        
        invalid_tokens = [
            "invalid_token",
            "Bearer invalid",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid",
            "",
            "null",
            "undefined",
            "' OR '1'='1",
            "<script>alert('xss')</script>",
            "../../etc/passwd",
            "admin",
            "root",
        ]
        
        for token in invalid_tokens:
            try:
                headers = {"Authorization": f"Bearer {token}"}
                response = requests.get(
                    f"{self.base_url}/api/auth/me",
                    headers=headers,
                    timeout=10
                )
                
                # 应该返回401
                is_vulnerable = response.status_code != 401
                
                results.append(SecurityTestResult(
                    test_name="无效Token测试",
                    vulnerability_type="Invalid Token Handling",
                    endpoint="/api/auth/me",
                    method="GET",
                    status_code=response.status_code,
                    is_vulnerable=is_vulnerable,
                    risk_level="MEDIUM" if is_vulnerable else "LOW",
                    description=f"无效token '{token[:20]}...' " + (
                        "被接受" if is_vulnerable else "被正确拒绝"
                    ),
                    recommendation="确保无效token被正确拒绝并返回401" if is_vulnerable else "Token验证正常"
                ))
            except Exception as e:
                # 网络异常不算漏洞
                pass
        
        return results
    
    def test_sql_injection(self) -> List[SecurityTestResult]:
        """测试SQL注入"""
        results = []
        
        sql_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "' UNION SELECT * FROM users --",
            "admin'--",
            "admin' OR '1'='1'--",
            "'; INSERT INTO users VALUES('hacker','password'); --",
            "' OR 1=1#",
            "1' AND (SELECT COUNT(*) FROM users) > 0 --",
        ]
        
        # 测试不同端点的SQL注入
        test_cases = [
            {
                "endpoint": "/api/auth/login",
                "method": "POST",
                "data_template": {"email": "{payload}", "password": "test"}
            },
            {
                "endpoint": "/api/auth/login", 
                "method": "POST",
                "data_template": {"email": "test@test.com", "password": "{payload}"}
            },
        ]
        
        for case in test_cases:
            for payload in sql_payloads:
                try:
                    data = {}
                    for key, value in case["data_template"].items():
                        data[key] = value.replace("{payload}", payload)
                    
                    response = requests.post(
                        f"{self.base_url}{case['endpoint']}",
                        json=data,
                        timeout=10
                    )
                    
                    # 检查是否可能存在SQL注入
                    response_text = response.text.lower() if response.text else ""
                    sql_error_indicators = [
                        "sql", "mysql", "postgresql", "sqlite", "syntax error",
                        "database", "table", "column", "select", "insert", "update", "delete"
                    ]
                    
                    has_sql_error = any(indicator in response_text for indicator in sql_error_indicators)
                    is_vulnerable = (response.status_code == 200 and "token" in response_text) or has_sql_error
                    
                    if is_vulnerable or has_sql_error:
                        results.append(SecurityTestResult(
                            test_name="SQL注入测试",
                            vulnerability_type="SQL Injection",
                            endpoint=case["endpoint"],
                            method=case["method"],
                            status_code=response.status_code,
                            is_vulnerable=True,
                            risk_level="CRITICAL",
                            description=f"SQL注入payload '{payload[:30]}...' 可能成功",
                            recommendation="使用参数化查询和ORM，验证和清理所有用户输入"
                        ))
                
                except Exception:
                    # 网络异常忽略
                    pass
        
        return results
    
    def test_xss_injection(self) -> List[SecurityTestResult]:
        """测试XSS注入"""
        results = []
        
        xss_payloads = [
            "<script>alert('xss')</script>",
            "<img src=x onerror=alert('xss')>",
            "javascript:alert('xss')",
            "<svg onload=alert('xss')>",
            "';alert('xss');//",
            "<iframe src=javascript:alert('xss')>",
            "<body onload=alert('xss')>",
        ]
        
        if not self.valid_token:
            return results
        
        # 测试用户输入字段
        for payload in xss_payloads:
            try:
                # 测试display_name
                profile_data = {
                    "section_type": "profile",
                    "section_key": "personal",
                    "content": {
                        "display_name": payload,
                        "bio": f"测试用户简介 {payload}"
                    }
                }
                
                response = requests.post(
                    f"{self.base_url}/api/profile/metadata",
                    json=profile_data,
                    headers={"Authorization": f"Bearer {self.valid_token}"},
                    timeout=10
                )
                
                # 检查响应是否包含未转义的payload
                if response.status_code == 200 and payload in response.text:
                    results.append(SecurityTestResult(
                        test_name="XSS注入测试",
                        vulnerability_type="Cross-Site Scripting",
                        endpoint="/api/profile/metadata",
                        method="POST",
                        status_code=response.status_code,
                        is_vulnerable=True,
                        risk_level="HIGH",
                        description=f"XSS payload '{payload[:30]}...' 未被正确转义",
                        recommendation="对所有用户输入进行HTML转义和内容安全策略(CSP)"
                    ))
            
            except Exception:
                pass
        
        return results
    
    def test_authorization_bypass(self) -> List[SecurityTestResult]:
        """测试权限绕过"""
        results = []
        
        if not self.valid_token:
            return results
        
        # 创建第二个测试用户
        second_user = {
            "email": f"security_test_2_{int(time.time())}@example.com",
            "password": "SecurityTest123!",
            "display_name": "第二个测试用户"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/auth/register",
                json=second_user,
                timeout=10
            )
            
            if response.status_code != 201:
                return results
            
            second_token = response.json()['data']['token']
            second_user_id = response.json()['data']['user_id']
            
            # 第一个用户创建metadata
            metadata = {
                "section_type": "profile",
                "section_key": "private",
                "content": {"secret": "这是私密信息"}
            }
            
            requests.post(
                f"{self.base_url}/api/profile/metadata",
                json=metadata,
                headers={"Authorization": f"Bearer {self.valid_token}"},
                timeout=10
            )
            
            # 第二个用户尝试访问第一个用户的数据
            response = requests.get(
                f"{self.base_url}/api/profile/metadata",
                headers={"Authorization": f"Bearer {second_token}"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json().get('data', {})
                # 检查是否能看到其他用户的数据
                if isinstance(data, dict) and "secret" in str(data):
                    results.append(SecurityTestResult(
                        test_name="权限绕过测试",
                        vulnerability_type="Authorization Bypass",
                        endpoint="/api/profile/metadata",
                        method="GET", 
                        status_code=response.status_code,
                        is_vulnerable=True,
                        risk_level="HIGH",
                        description="用户可以访问其他用户的私密数据",
                        recommendation="实施严格的用户权限检查，确保用户只能访问自己的数据"
                    ))
        
        except Exception:
            pass
        
        return results
    
    def test_sensitive_data_exposure(self) -> List[SecurityTestResult]:
        """测试敏感数据泄露"""
        results = []
        
        # 测试错误信息是否泄露敏感信息
        endpoints_to_test = [
            "/api/auth/login",
            "/api/auth/register", 
            "/api/profile/metadata",
            "/api/match/search"
        ]
        
        for endpoint in endpoints_to_test:
            try:
                # 发送畸形请求
                response = requests.post(
                    f"{self.base_url}{endpoint}",
                    json={"malformed": "data"},
                    timeout=10
                )
                
                response_text = response.text.lower() if response.text else ""
                
                # 检查是否泄露敏感信息
                sensitive_patterns = [
                    "traceback", "stack trace", "file not found",
                    "database", "sql", "password", "secret", "key",
                    "internal server error", "debug", "exception",
                    "/home/", "/var/", "c:\\", "python", "java"
                ]
                
                exposed_info = [pattern for pattern in sensitive_patterns if pattern in response_text]
                
                if exposed_info:
                    results.append(SecurityTestResult(
                        test_name="敏感信息泄露测试",
                        vulnerability_type="Information Disclosure",
                        endpoint=endpoint,
                        method="POST",
                        status_code=response.status_code,
                        is_vulnerable=True,
                        risk_level="MEDIUM",
                        description=f"错误响应可能泄露敏感信息: {', '.join(exposed_info)}",
                        recommendation="使用通用错误消息，不要在生产环境中显示详细的错误信息"
                    ))
            
            except Exception:
                pass
        
        return results
    
    def test_rate_limiting(self) -> List[SecurityTestResult]:
        """测试速率限制"""
        results = []
        
        # 快速发送大量请求测试是否有速率限制
        print("🔄 测试速率限制...")
        
        endpoint = "/api/auth/login"
        requests_sent = 0
        successful_requests = 0
        
        start_time = time.time()
        
        for i in range(50):  # 快速发送50个请求
            try:
                response = requests.post(
                    f"{self.base_url}{endpoint}",
                    json={"email": "test@test.com", "password": "wrong"},
                    timeout=5
                )
                requests_sent += 1
                
                if response.status_code != 429:  # 429 = Too Many Requests
                    successful_requests += 1
                
                # 如果连续成功太多，说明可能没有速率限制
                if successful_requests > 30:
                    break
                
            except Exception:
                break
        
        elapsed_time = time.time() - start_time
        
        # 如果在短时间内成功处理了很多请求，可能缺乏速率限制
        if successful_requests > 30 and elapsed_time < 10:
            results.append(SecurityTestResult(
                test_name="速率限制测试",
                vulnerability_type="Rate Limiting",
                endpoint=endpoint,
                method="POST",
                status_code=200,
                is_vulnerable=True,
                risk_level="MEDIUM",
                description=f"短时间内处理了{successful_requests}个请求，可能缺乏速率限制",
                recommendation="实施API速率限制以防止暴力破解和DoS攻击"
            ))
        
        return results
    
    def test_input_validation(self) -> List[SecurityTestResult]:
        """测试输入验证"""
        results = []
        
        if not self.valid_token:
            return results
        
        # 测试极长输入
        long_string = "A" * 100000  # 100KB字符串
        
        try:
            response = requests.post(
                f"{self.base_url}/api/profile/metadata",
                json={
                    "section_type": "profile",
                    "section_key": "test",
                    "content": {"long_field": long_string}
                },
                headers={"Authorization": f"Bearer {self.valid_token}"},
                timeout=30
            )
            
            # 如果接受了极长输入，可能存在DoS风险
            if response.status_code == 200:
                results.append(SecurityTestResult(
                    test_name="输入长度验证测试",
                    vulnerability_type="Input Validation",
                    endpoint="/api/profile/metadata",
                    method="POST",
                    status_code=response.status_code,
                    is_vulnerable=True,
                    risk_level="MEDIUM",
                    description="接受了极长的输入数据，可能导致DoS攻击",
                    recommendation="实施输入长度限制和验证"
                ))
        
        except Exception:
            pass
        
        return results
    
    def generate_security_report(self, results: List[SecurityTestResult]) -> str:
        """生成安全测试报告"""
        
        total_tests = len(results)
        vulnerabilities = [r for r in results if r.is_vulnerable]
        critical_vulns = [r for r in vulnerabilities if r.risk_level == "CRITICAL"]
        high_vulns = [r for r in vulnerabilities if r.risk_level == "HIGH"]
        medium_vulns = [r for r in vulnerabilities if r.risk_level == "MEDIUM"]
        low_vulns = [r for r in vulnerabilities if r.risk_level == "LOW"]
        
        report = f"""
# API 安全测试报告

## 📊 测试概览
- **测试时间**: {time.strftime('%Y-%m-%d %H:%M:%S')}
- **API地址**: {self.base_url}
- **总测试数**: {total_tests}
- **发现漏洞**: {len(vulnerabilities)}

## 🚨 风险等级分布
- **🔴 严重 (CRITICAL)**: {len(critical_vulns)}
- **🟠 高危 (HIGH)**: {len(high_vulns)}
- **🟡 中危 (MEDIUM)**: {len(medium_vulns)}
- **🟢 低危 (LOW)**: {len(low_vulns)}

## 🔍 详细漏洞信息
"""
        
        for risk_level, risk_color in [
            ("CRITICAL", "🔴"), ("HIGH", "🟠"), 
            ("MEDIUM", "🟡"), ("LOW", "🟢")
        ]:
            level_vulns = [v for v in vulnerabilities if v.risk_level == risk_level]
            if level_vulns:
                report += f"\n### {risk_color} {risk_level} 风险漏洞\n\n"
                for vuln in level_vulns:
                    report += f"""
**{vuln.test_name}**
- **漏洞类型**: {vuln.vulnerability_type}
- **影响端点**: {vuln.method} {vuln.endpoint}
- **状态码**: {vuln.status_code}
- **描述**: {vuln.description}
- **建议**: {vuln.recommendation}

---
"""
        
        # 安全评估
        security_score = max(0, 100 - (len(critical_vulns) * 30 + len(high_vulns) * 20 + len(medium_vulns) * 10 + len(low_vulns) * 5))
        
        report += f"""
## 🎯 安全评估

**安全评分**: {security_score}/100

"""
        
        if security_score >= 90:
            report += "**🟢 安全状况良好**: API具有较好的安全防护，可以安全部署。\n"
        elif security_score >= 70:
            report += "**🟡 安全状况一般**: 存在一些安全问题，建议修复后部署。\n"
        elif security_score >= 50:
            report += "**🟠 安全风险较高**: 存在多个安全漏洞，需要优先修复。\n"
        else:
            report += "**🔴 安全风险严重**: 存在严重安全漏洞，不建议部署到生产环境。\n"
        
        report += """
## 📝 通用安全建议

1. **认证和授权**
   - 使用强JWT密钥
   - 实施token过期机制
   - 确保所有受保护端点都需要认证

2. **输入验证**
   - 验证所有用户输入
   - 实施长度和格式限制
   - 使用参数化查询防止SQL注入

3. **输出编码**
   - 对所有输出进行HTML转义
   - 实施内容安全策略(CSP)

4. **速率限制**
   - 实施API调用频率限制
   - 防止暴力破解攻击

5. **错误处理**
   - 使用通用错误消息
   - 不要泄露系统内部信息

6. **HTTPS**
   - 生产环境必须使用HTTPS
   - 配置安全的TLS设置
"""
        
        return report
    
    def run_security_tests(self) -> bool:
        """运行所有安全测试"""
        print("🔒 开始API安全测试")
        print("=" * 60)
        
        all_results = []
        
        # 设置测试用户
        print("🔧 设置测试环境...")
        if not self.setup_test_user():
            print("⚠️ 无法设置测试用户，部分测试将跳过")
        
        # 认证绕过测试
        print("1️⃣ 认证绕过测试...")
        auth_bypass_results = self.test_authentication_bypass()
        all_results.extend(auth_bypass_results)
        
        # 无效token测试
        print("2️⃣ 无效Token处理测试...")
        invalid_token_results = self.test_invalid_tokens()
        all_results.extend(invalid_token_results)
        
        # SQL注入测试
        print("3️⃣ SQL注入测试...")
        sql_injection_results = self.test_sql_injection()
        all_results.extend(sql_injection_results)
        
        # XSS注入测试
        print("4️⃣ XSS注入测试...")
        xss_results = self.test_xss_injection()
        all_results.extend(xss_results)
        
        # 权限绕过测试
        print("5️⃣ 权限绕过测试...")
        authz_results = self.test_authorization_bypass()
        all_results.extend(authz_results)
        
        # 敏感信息泄露测试
        print("6️⃣ 敏感信息泄露测试...")
        info_disclosure_results = self.test_sensitive_data_exposure()
        all_results.extend(info_disclosure_results)
        
        # 速率限制测试
        print("7️⃣ 速率限制测试...")
        rate_limit_results = self.test_rate_limiting()
        all_results.extend(rate_limit_results)
        
        # 输入验证测试
        print("8️⃣ 输入验证测试...")
        input_validation_results = self.test_input_validation()
        all_results.extend(input_validation_results)
        
        # 生成报告
        report = self.generate_security_report(all_results)
        
        # 保存报告
        report_file = f"security_test_report_{int(time.time())}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n📄 安全测试报告已保存: {report_file}")
        print("\n" + "=" * 60)
        print(report)
        
        # 计算是否通过安全测试
        vulnerabilities = [r for r in all_results if r.is_vulnerable]
        critical_high_vulns = [r for r in vulnerabilities if r.risk_level in ["CRITICAL", "HIGH"]]
        
        return len(critical_high_vulns) == 0

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='API安全测试工具')
    parser.add_argument('--url', default='http://localhost:5003', help='API服务器地址')
    
    args = parser.parse_args()
    
    tester = APISecurityTester(args.url)
    success = tester.run_security_tests()
    
    if success:
        print("\n✅ API安全测试通过！没有发现严重安全漏洞。")
        sys.exit(0)
    else:
        print("\n⚠️ API存在安全风险，建议修复后重新测试。")
        sys.exit(1)

if __name__ == "__main__":
    main() 