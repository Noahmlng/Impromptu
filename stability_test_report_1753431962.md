
# API 稳定性测试报告

## 📊 测试概览
- **测试时间**: 2025-07-25 16:26:02
- **API地址**: http://localhost:5003
- **总测试数**: 61
- **成功率**: 81.97%

## 📈 性能指标
- **平均响应时间**: 0.598秒
- **响应时间中位数**: 0.007秒
- **最快响应**: 0.002秒
- **最慢响应**: 5.966秒
- **响应时间标准差**: 1.101秒

## 📋 状态码分布
- **200**: 48次
- **404**: 1次
- **401**: 8次
- **400**: 1次
- **500**: 3次

## ✅ 成功测试详情
- GET /api/system/health: 0.006秒
- GET /api/auth/me (invalid token): 0.002秒
- POST /api/auth/register (invalid data): 0.002秒
- GET /api/system/stats (load test user_1): 0.631秒
- GET /api/system/health (load test user_3): 0.004秒
- GET /api/system/stats (load test user_1): 1.964秒
- GET /api/system/health (load test user_1): 0.006秒
- GET /api/system/health (load test user_4): 0.006秒
- GET /api/system/stats (load test user_2): 0.809秒
- GET /api/system/stats (load test user_0): 0.802秒
- GET /api/system/stats (load test user_3): 1.055秒
- GET /api/system/health (load test user_3): 0.003秒
- GET /api/system/stats (load test user_2): 2.215秒
- GET /api/system/health (load test user_4): 0.005秒
- GET /api/system/stats (load test user_1): 0.673秒
- GET /api/system/stats (load test user_1): 1.911秒
- GET /api/system/health (load test user_2): 0.004秒
- GET /api/system/health (load test user_2): 0.003秒
- GET /api/system/health (load test user_0): 0.007秒
- GET /api/system/health (load test user_3): 0.004秒
- GET /api/system/stats (load test user_0): 0.842秒
- GET /api/system/stats (load test user_0): 0.980秒
- GET /api/system/stats (load test user_4): 1.091秒
- GET /api/system/health (load test user_2): 0.006秒
- GET /api/system/health (load test user_0): 0.003秒
- GET /api/system/stats (load test user_0): 0.710秒
- GET /api/system/health (load test user_1): 0.004秒
- GET /api/system/health (load test user_4): 0.006秒
- GET /api/system/stats (load test user_2): 0.651秒
- GET /api/system/stats (load test user_3): 0.783秒
- GET /api/system/stats (load test user_0): 1.243秒
- GET /api/system/stats (load test user_0): 1.288秒
- GET /api/system/stats (load test user_4): 1.063秒
- GET /api/system/stats (load test user_2): 0.673秒
- GET /api/system/health (load test user_2): 0.002秒
- GET /api/system/health (load test user_2): 0.007秒
- GET /api/system/health (load test user_3): 0.008秒
- GET /api/system/stats (load test user_3): 1.198秒
- GET /api/system/health (load test user_1): 0.005秒
- GET /api/system/stats (load test user_4): 0.813秒
- GET /api/system/health (load test user_3): 0.003秒
- GET /api/system/stats (load test user_3): 0.997秒
- GET /api/system/health (load test user_2): 0.003秒
- GET /api/system/health (load test user_1): 0.008秒
- GET /api/system/health (load test user_0): 0.003秒
- GET /api/system/health (load test user_0): 0.002秒
- GET /api/system/stats (load test user_1): 1.510秒
- GET /api/system/health (load test user_3): 0.005秒
- GET /api/system/health (load test user_1): 0.006秒
- GET /api/system/stats (load test user_4): 5.966秒

## ❌ 失败测试详情
- POST /api/auth/login: 404 - None
- GET /api/auth/me: 401 - None
- POST /api/profile/metadata: 401 - None
- GET /api/profile/metadata: 401 - None
- POST /api/tags/generate: 401 - None
- POST /api/tags/manual: 401 - None
- GET /api/tags/user: 401 - None
- POST /api/match/search: 401 - None
- GET /api/system/stats (load test user_4): 500 - None
- GET /api/system/stats (load test user_4): 500 - None
- GET /api/system/stats (load test user_4): 500 - None

## 🎯 稳定性评估

基于测试结果，API稳定性评估:

- **功能稳定性**: 🟡 一般
- **性能表现**: 🟢 良好
- **错误处理**: 🔴 需要改进

## 📝 建议

- 成功率偏低，建议检查API端点实现和错误处理
- 存在失败的测试用例，建议修复相关问题后重新测试
