# 用户匹配系统 REST API

基于 **LDA 主题建模** + **Faiss 向量相似度计算** 的用户匹配系统 API 接口

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动API服务器

```bash
python api_server.py
```

服务器将在 `http://localhost:5000` 启动

### 3. 测试API

```bash
# 健康检查
curl http://localhost:5000/health

# 查看API文档
curl http://localhost:5000/api/docs

# 演示匹配 (Noah vs Alan)
curl http://localhost:5000/api/demo
```

### 4. 运行完整测试

```bash
python test_api_client.py
```

## 📡 API 接口

### 基础接口

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/health` | 健康检查 |
| GET | `/api/docs` | API文档 |
| GET | `/api/demo` | 演示匹配 (Noah vs Alan) |

### 匹配接口

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/api/match/simple` | 简洁匹配分析 |
| POST | `/api/match/upload` | 文件上传匹配 |

### 模型管理

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/api/train` | 训练LDA模型 |
| POST | `/api/model/save` | 保存模型 |
| POST | `/api/model/load` | 加载模型 |

### 数据接口

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/tags` | 获取标签池 |

## 💻 使用示例

### Python 客户端

```python
import requests
import json

# 1. 健康检查
response = requests.get('http://localhost:5000/health')
print(response.json())

# 2. 简洁匹配
user_a = {
    "profile": {
        "name": {"display_name": "用户A"},
        "professional": {"current_role": "AI工程师"},
        "personality": {"mbti_type": "INTJ"},
        "expertise_areas": ["机器学习", "Python"]
    },
    "user_request": {
        "request_type": "找队友",
        "description": "寻找AI技术合作伙伴"
    }
}

user_b = {
    "profile": {
        "name": {"display_name": "用户B"},
        "professional": {"current_role": "产品经理"},
        "personality": {"mbti_type": "ENFP"},
        "expertise_areas": ["产品管理", "用户研究"]
    },
    "user_request": {
        "request_type": "找队友",
        "description": "寻找技术合伙人"
    }
}

payload = {"user_a": user_a, "user_b": user_b}
response = requests.post(
    'http://localhost:5000/api/match/simple',
    json=payload
)

result = response.json()
if result['success']:
    matching = result['data']['matching_analysis']
    for dimension, info in matching.items():
        print(f"{dimension}: {info['score']:.2f} - {info['description']}")
```

### curl 示例

```bash
# 演示匹配
curl http://localhost:5000/api/demo

# 获取标签池
curl "http://localhost:5000/api/tags?type=找队友"

# 简洁匹配
curl -X POST http://localhost:5000/api/match/simple \
  -H "Content-Type: application/json" \
  -d '{
    "user_a": {"profile": {...}, "user_request": {...}},
    "user_b": {"profile": {...}, "user_request": {...}}
  }'
```

## 📊 输出格式

API 返回标准的 JSON 格式，包含7个维度的匹配分析：

```json
{
  "success": true,
  "data": {
    "participants": {
      "person_a": "用户A",
      "person_b": "用户B"
    },
    "matching_analysis": {
      "overall_match": {
        "score": 5.23,
        "description": "总体中等匹配",
        "details": "共同标签8个，诉求类型匹配，向量相似度0.45"
      },
      "personality_match": {
        "score": 6.80,
        "description": "性格良好匹配",
        "details": "MBTI类型互补，性格特征有一定相似性"
      },
      "interests_match": {
        "score": 4.20,
        "description": "兴趣中等匹配",
        "details": "兴趣爱好不同，但可以互相学习"
      },
      "career_match": {
        "score": 7.50,
        "description": "职业良好匹配",
        "details": "职业相关：技术开发, 产品管理, 有合作经验"
      },
      "values_match": {
        "score": 5.00,
        "description": "价值观中等匹配",
        "details": "价值观可能存在差异，需要进一步了解"
      },
      "request_match": {
        "score": 8.20,
        "description": "诉求高度匹配",
        "details": "诉求相似度0.82，都在寻找合作伙伴"
      },
      "complementary_match": {
        "score": 8.50,
        "description": "互补性高度匹配",
        "details": "技能和经验背景存在互补性，可能形成良好的合作关系"
      }
    }
  }
}
```

## 🏗️ 系统架构

```
├── API层 (Flask)
│   ├── 匹配接口
│   ├── 模型管理
│   └── 数据接口
│
├── 分析引擎
│   ├── LDA主题建模
│   ├── Faiss向量匹配
│   └── 标签池管理
│
└── 数据层
    ├── 用户档案
    ├── 训练模型
    └── 匹配结果
```

## 🎯 特色功能

### 1. 多维度匹配分析
- **7个维度**：总体、性格、兴趣、职业、价值观、诉求、互补性
- **量化评分**：0-10分评分系统
- **智能描述**：自动生成匹配描述和建议

### 2. 智能标签提取
- **200+ 预定义标签**：覆盖找对象/找队友场景
- **LDA主题建模**：自动从文本中提取语义标签
- **中文优化**：专门优化的中文分词和处理

### 3. 高效向量匹配
- **Faiss加速**：毫秒级相似度计算
- **向量化表示**：用户档案和诉求的数值化表示
- **可扩展性**：支持大规模用户匹配

### 4. 灵活的API设计
- **RESTful接口**：标准HTTP API
- **多种输入方式**：JSON对象、文件上传
- **错误处理**：详细的错误信息和状态码

## 🔧 配置选项

系统支持多种配置，可在 `config.py` 中调整：

- **LDA参数**：主题数量、训练轮数、收敛阈值
- **向量匹配**：相似度算法、权重分配、筛选阈值
- **标签池**：自定义标签分类和内容

## 📈 性能优化

- **模型缓存**：训练好的LDA模型可保存和重用
- **向量索引**：Faiss索引支持快速检索
- **并发处理**：Flask支持多线程请求处理
- **内存优化**：适当的批量处理和资源管理

## 🛠️ 开发指南

### 添加新的匹配维度

1. 在 `models/matching_result.py` 中添加新维度
2. 在 `tag_compatibility_analyzer.py` 中实现计算逻辑
3. 更新API文档和测试用例

### 扩展标签池

1. 编辑 `models/tag_pool.py`
2. 在相应的标签分类中添加新标签
3. 重新训练LDA模型以学习新标签

### 集成外部系统

API支持与各种系统集成：
- **移动应用**：通过HTTP API调用
- **Web应用**：CORS已启用，支持前端调用
- **批量处理**：支持批量上传和分析

## ⚠️ 注意事项

1. **模型训练**：首次使用需要训练LDA模型
2. **中文支持**：确保输入文本为UTF-8编码
3. **内存使用**：大规模匹配时注意内存消耗
4. **API限制**：当前版本无速率限制，生产环境建议添加

## 📞 技术支持

如有问题或建议，请：
1. 查看 API 文档：`GET /api/docs`
2. 运行测试脚本：`python test_api_client.py`
3. 检查服务器日志：查看控制台输出

## 🔮 后续规划

- [ ] 集成 Supabase 云端存储
- [ ] 添加用户认证和权限管理
- [ ] 实现批量匹配和推荐算法
- [ ] 添加实时匹配和通知功能
- [ ] 性能监控和分析仪表板 