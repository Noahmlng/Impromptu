
# API 稳定性测试报告

## 📊 测试概览
- **测试时间**: 2025-07-25 16:25:28
- **API地址**: http://localhost:5003
- **总测试数**: 61
- **成功率**: 86.89%

## 📈 性能指标
- **平均响应时间**: 0.523秒
- **响应时间中位数**: 0.006秒
- **最快响应**: 0.001秒
- **最慢响应**: 4.862秒
- **响应时间标准差**: 1.031秒

## 📋 状态码分布
- **200**: 51次
- **404**: 1次
- **401**: 8次
- **400**: 1次

## ✅ 成功测试详情
- GET /api/system/health: 0.030秒
- GET /api/auth/me (invalid token): 0.001秒
- POST /api/auth/register (invalid data): 0.002秒
- GET /api/system/health (load test user_4): 0.006秒
- GET /api/system/health (load test user_4): 0.004秒
- GET /api/system/stats (load test user_2): 0.627秒
- GET /api/system/health (load test user_4): 0.009秒
- GET /api/system/stats (load test user_3): 4.222秒
- GET /api/system/health (load test user_0): 0.005秒
- GET /api/system/stats (load test user_0): 0.490秒
- GET /api/system/stats (load test user_4): 0.647秒
- GET /api/system/health (load test user_3): 0.005秒
- GET /api/system/stats (load test user_3): 2.376秒
- GET /api/system/health (load test user_1): 0.005秒
- GET /api/system/health (load test user_1): 0.006秒
- GET /api/system/stats (load test user_0): 0.536秒
- GET /api/system/stats (load test user_2): 4.862秒
- GET /api/system/health (load test user_2): 0.005秒
- GET /api/system/health (load test user_3): 0.004秒
- GET /api/system/health (load test user_3): 0.003秒
- GET /api/system/stats (load test user_2): 1.070秒
- GET /api/system/health (load test user_4): 0.004秒
- GET /api/system/stats (load test user_3): 3.015秒
- GET /api/system/stats (load test user_1): 2.701秒
- GET /api/system/stats (load test user_0): 0.536秒
- GET /api/system/health (load test user_4): 0.005秒
- GET /api/system/stats (load test user_0): 0.566秒
- GET /api/system/health (load test user_0): 0.007秒
- GET /api/system/stats (load test user_4): 0.567秒
- GET /api/system/health (load test user_2): 0.003秒
- GET /api/system/stats (load test user_1): 0.540秒
- GET /api/system/stats (load test user_1): 0.614秒
- GET /api/system/health (load test user_1): 0.007秒
- GET /api/system/health (load test user_2): 0.006秒
- GET /api/system/health (load test user_4): 0.003秒
- GET /api/system/health (load test user_3): 0.007秒
- GET /api/system/stats (load test user_1): 0.541秒
- GET /api/system/stats (load test user_0): 0.757秒
- GET /api/system/stats (load test user_0): 0.569秒
- GET /api/system/stats (load test user_2): 2.297秒
- GET /api/system/stats (load test user_0): 0.661秒
- GET /api/system/stats (load test user_2): 2.133秒
- GET /api/system/health (load test user_1): 0.003秒
- GET /api/system/health (load test user_2): 0.004秒
- GET /api/system/health (load test user_0): 0.004秒
- GET /api/system/health (load test user_2): 0.006秒
- GET /api/system/health (load test user_1): 0.005秒
- GET /api/system/health (load test user_4): 0.006秒
- GET /api/system/health (load test user_3): 0.007秒
- GET /api/system/health (load test user_3): 0.006秒
- GET /api/system/health (load test user_1): 0.006秒
- GET /api/system/health (load test user_3): 0.005秒
- GET /api/system/stats (load test user_4): 1.148秒

## ❌ 失败测试详情
- POST /api/auth/login: 404 - None
- GET /api/auth/me: 401 - None
- POST /api/profile/metadata: 401 - None
- GET /api/profile/metadata: 401 - None
- POST /api/tags/generate: 401 - None
- POST /api/tags/manual: 401 - None
- GET /api/tags/user: 401 - None
- POST /api/match/search: 401 - None

## 🎯 稳定性评估

基于测试结果，API稳定性评估:

- **功能稳定性**: 🟡 一般
- **性能表现**: 🟢 良好
- **错误处理**: 🔴 需要改进

## 📝 建议

- 成功率偏低，建议检查API端点实现和错误处理
- 存在失败的测试用例，建议修复相关问题后重新测试
