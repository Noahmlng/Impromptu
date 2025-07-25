# Impromptu 系统架构文档

## 系统概述

Impromptu 是一个基于AI的社交匹配算法系统，采用模块化设计，支持多维度用户兼容性分析和智能匹配推荐。

## 整体架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Frontend  │    │   API Gateway   │    │  Core Algorithm │
│   (HTML/CSS/JS) │◄──►│   (Flask API)   │◄──►│   (Python)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Data Layer    │
                       │   (JSON/Models) │
                       └─────────────────┘
```

## 核心模块

### 1. 算法层 (src/algorithms/)

#### EnhancedCompatibilityAnalyzer
- **功能**: 核心匹配算法实现
- **输入**: 用户档案JSON文件
- **输出**: 多维度匹配评分和详细分析
- **关键方法**:
  - `train_models()`: 训练LDA主题模型
  - `enhanced_compatibility_analysis()`: 执行兼容性分析
  - `analyze_and_output_simple_result()`: 生成简化输出

#### LLMCompatibilityAnalyzer
- **功能**: 基于大语言模型的增强分析
- **特点**: 支持自然语言理解和生成
- **集成**: 可选的AI增强功能

#### UserProfileAnalyzer
- **功能**: 用户档案分析和标签提取
- **输出**: 结构化的用户特征向量

### 2. 模型层 (src/models/)

#### TopicModeling (LDA)
```python
class LDATopicModel:
    - train_model(texts)
    - extract_topics(profile)
    - calculate_similarity(topics_a, topics_b)
```

#### VectorMatching (Faiss)
```python
class VectorUserMatcher:
    - vectorize_user(profile)
    - find_similar_users(query_vector, k=10)
    - calculate_similarity(vector_a, vector_b)
```

#### TagMatching
```python
class TagMatcher:
    - match_tags(tags_a, tags_b)
    - calculate_tag_similarity()
    - extract_complementary_tags()
```

### 3. 服务层 (src/services/)

#### APIServer (Flask)
- **端口**: 5000
- **功能**: RESTful API接口
- **主要端点**:
  - `/api/match/*`: 匹配分析接口
  - `/api/database/*`: 数据管理接口
  - `/api/train`: 模型训练接口

### 4. 数据层

#### 数据存储结构
```
data/
├── raw/profiles/          # 原始用户档案
├── processed/user_vectors/ # 处理后的用户向量
├── models/                # 训练好的模型文件
└── results/               # 匹配结果输出
```

#### 数据格式
- **用户档案**: JSON格式，包含基本信息、性格、兴趣、诉求等
- **模型文件**: pickle格式的LDA模型和向量化器
- **匹配结果**: JSON格式的结构化分析结果

## 算法流程

### 1. 模型训练流程
```
用户档案 → 文本预处理 → LDA主题建模 → 向量化 → 模型保存
```

### 2. 匹配分析流程
```
用户A档案 → 特征提取 → 向量化 → 相似度计算 → 多维度评分 → 结果输出
用户B档案 ↗
```

### 3. 多维度评分算法
```python
# 各维度权重配置
weights = {
    'personality_match': 0.15,
    'interests_match': 0.20,
    'career_match': 0.25,
    'values_match': 0.15,
    'request_match': 0.20,
    'complementary_match': 0.05
}

# 总体评分计算
overall_score = sum(score * weight for score, weight in weights.items())
```

## 技术栈

### 后端技术
- **Python 3.8+**: 主要开发语言
- **Flask**: Web框架
- **Gensim**: LDA主题建模
- **Faiss**: 向量相似度计算
- **Scikit-learn**: 机器学习工具
- **Jieba**: 中文分词

### 前端技术
- **HTML5/CSS3**: 页面结构和样式
- **JavaScript (ES6+)**: 交互逻辑
- **Fetch API**: HTTP请求

### 数据处理
- **JSON**: 数据交换格式
- **Pickle**: 模型序列化
- **NumPy**: 数值计算

## 性能优化

### 1. 向量化优化
- 使用Faiss进行高效的向量相似度计算
- 支持GPU加速（可选）
- 向量索引优化

### 2. 缓存策略
- 模型缓存：避免重复加载
- 结果缓存：相同输入的快速返回
- 内存管理：及时释放大对象

### 3. 并发处理
- 异步模型训练
- 批量用户处理
- 连接池管理

## 扩展性设计

### 1. 模块化架构
- 算法模块可独立替换
- 数据源可扩展
- API接口标准化

### 2. 配置驱动
- 权重参数可配置
- 模型参数可调整
- 提示词模板化

### 3. 插件系统
- 支持新的匹配算法
- 支持新的数据源
- 支持新的输出格式

## 部署架构

### 开发环境
```
┌─────────────┐
│   Local     │
│ Development │
└─────────────┘
```

### 生产环境建议
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Nginx     │    │   Gunicorn │    │   Redis     │
│  (Reverse   │◄──►│  (WSGI)     │◄──►│  (Cache)    │
│   Proxy)    │    │             │    │             │
└─────────────┘    └─────────────┘    └─────────────┘
```

## 监控和日志

### 1. 性能监控
- API响应时间
- 模型训练时间
- 内存使用情况

### 2. 错误处理
- 异常捕获和记录
- 优雅降级
- 用户友好的错误信息

### 3. 日志系统
- 结构化日志
- 不同级别日志
- 日志轮转

## 安全考虑

### 1. 数据安全
- 用户数据加密存储
- API访问控制
- 敏感信息脱敏

### 2. 系统安全
- 输入验证
- SQL注入防护
- XSS防护

## 未来扩展

### 1. 功能扩展
- 实时匹配推荐
- 多语言支持
- 移动端适配

### 2. 技术升级
- 深度学习模型
- 图神经网络
- 实时流处理

### 3. 集成能力
- 第三方平台集成
- 数据同步机制
- 开放API平台 