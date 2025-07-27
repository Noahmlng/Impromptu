# Impromptu - AI智能社交匹配平台

> 基于大语言模型和多维算法的智能社交匹配系统，专为寻找队友、合作伙伴、恋爱对象等场景设计的现代化全栈应用。

## ✨ 项目特色

🧠 **AI驱动的多维匹配** - 结合LLM、LDA主题建模、向量相似度的智能算法  
🎯 **精准兼容性分析** - 性格、兴趣、职业、价值观、诉求等6维度深度匹配  
🔐 **安全的用户系统** - 基于Supabase的认证和数据管理  
💬 **智能个性分析** - AI驱动的个性化聊天和深度画像分析  
🎮 **互动解锁机制** - 趣味小游戏解锁更多匹配功能  
📱 **现代化界面** - Next.js + Tailwind CSS打造的响应式用户体验

## 🎯 核心功能

### 智能匹配系统
- **多维度兼容性分析**: 性格、兴趣、职业、价值观、诉求、互补性等6个维度
- **AI增强分析**: 基于大语言模型的深度语义理解和匹配推荐
- **向量化搜索**: 使用Faiss进行高效的用户相似度计算
- **动态权重调整**: 根据用户类型和诉求智能调整匹配算法权重

### 用户体验功能
- **个性化档案**: 丰富的用户信息收集和展示
- **实时聊天**: AI辅助的个性分析对话系统
- **匹配搜索**: 即时的匹配结果搜索和筛选
- **解锁系统**: 通过小游戏解锁更多功能和匹配机会

### 技术特性
- **RESTful API**: 完整的后端API服务
- **实时通信**: WebSocket支持的实时功能
- **数据安全**: 企业级的数据加密和隐私保护
- **性能优化**: 缓存机制和算法优化确保快速响应

## 🏗️ 技术架构

### 前端技术栈
- **框架**: Next.js 14 (App Router)
- **语言**: TypeScript
- **样式**: Tailwind CSS + Radix UI
- **状态管理**: Zustand
- **认证**: Supabase Auth
- **主题**: next-themes (深色/浅色模式)

### 后端技术栈
- **框架**: FastAPI (Python)
- **数据库**: Supabase (PostgreSQL)
- **AI服务**: OpenAI API + Moonshot AI
- **向量搜索**: Faiss
- **主题建模**: Gensim (LDA)
- **中文处理**: jieba分词

### 算法技术
- **机器学习**: scikit-learn + numpy
- **自然语言处理**: 中文分词 + 停用词过滤
- **向量化**: TF-IDF + Word2Vec
- **相似度计算**: 余弦相似度 + 欧氏距离

## 📁 项目结构

```
Impromptu/
├── frontend/                   # Next.js 前端应用
│   ├── app/                   # App Router页面
│   │   ├── home/             # 主页
│   │   ├── chat/             # 聊天页面
│   │   ├── profile/          # 用户档案
│   │   ├── personality-chat/ # 个性分析聊天
│   │   └── onboarding/       # 用户引导
│   ├── components/           # React组件
│   │   ├── ui/              # 基础UI组件
│   │   ├── chat-interface.tsx
│   │   ├── match-search.tsx
│   │   └── unlock-modal.tsx
│   ├── lib/                 # 工具库
│   │   ├── api.ts          # API客户端
│   │   ├── store.ts        # 状态管理
│   │   └── supabase.ts     # 数据库客户端
│   └── hooks/              # React Hooks
├── backend/                # Python 后端服务
│   ├── algorithms/         # 核心匹配算法
│   │   ├── llm_compatibility_analyzer.py
│   │   ├── tag_compatibility_analyzer.py
│   │   └── user_profile_analyzer.py
│   ├── models/            # 数据模型
│   │   ├── compatibility_result.py
│   │   ├── matching_result.py
│   │   ├── topic_modeling.py
│   │   └── vector_matching.py
│   ├── services/          # 业务服务
│   │   ├── main_api.py    # 主API服务
│   │   ├── auth_service.py
│   │   ├── matching_service.py
│   │   ├── database_service.py
│   │   └── unlock_service.py
│   └── prompts/           # AI提示词
├── configs/               # 配置文件
│   ├── config.py         # 主配置
│   └── prompts/          # 提示词模板
├── data/                 # 数据目录
│   ├── raw/profiles/     # 用户档案
│   ├── processed/        # 处理后数据
│   ├── models/           # 训练模型
│   └── results/          # 匹配结果
├── scripts/              # 工具脚本
│   ├── setup/           # 部署脚本
│   ├── demo/            # 演示脚本
│   └── database/        # 数据库脚本
└── docs/                # 项目文档
```

## 🚀 快速开始

### 环境要求
- **Node.js**: 18.0+ 
- **Python**: 3.8+
- **操作系统**: macOS, Linux, Windows

### 一键启动
```bash
# 克隆项目
git clone <repository-url>
cd Impromptu

# 快速启动（包含环境检查、依赖安装、服务启动）
make quick-start
```

### 开发模式
```bash
# 开发模式 - 同时启动前后端服务
make dev

# 仅启动后端 (http://localhost:8000)
make backend

# 仅启动前端 (http://localhost:3000)  
make frontend

# 查看所有可用命令
make help
```

### 手动安装
```bash
# 1. 安装依赖
make install

# 2. 配置环境变量
cp .env.example .env.local
# 编辑 .env.local 添加必要的API密钥

# 3. 初始化数据库
python scripts/database/simple_create_table.py

# 4. 训练模型（可选）
python scripts/train/train_models.py

# 5. 启动服务
make dev
```

## 🌐 访问地址

启动成功后，访问以下地址：

- **前端应用**: http://localhost:3000
- **后端API**: http://localhost:8000  
- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health

## 💡 使用指南

### 1. 用户注册登录
- 支持邮箱注册和登录
- 安全的身份认证和会话管理
- 个人信息保护和隐私设置

### 2. 创建个人档案
```json
{
  "basic_info": {
    "name": "张三",
    "age": 28,
    "location": "北京",
    "occupation": "产品经理"
  },
  "personality": {
    "mbti": "ENFP", 
    "traits": ["外向", "创新", "协作"]
  },
  "interests": ["AI技术", "创业", "产品设计"],
  "user_request": {
    "request_type": "找队友",
    "description": "寻找技术合伙人，希望一起做AI产品"
  }
}
```

### 3. 智能匹配
- 输入匹配诉求和偏好
- AI分析生成个性化匹配结果
- 查看详细的兼容性评分报告

### 4. 互动解锁
- 通过趣味小游戏获得解锁机会
- 解锁更多用户档案和匹配功能
- 增加平台互动性和用户粘性

## 🧠 算法详解

### 多维度匹配算法
```python
# 评分权重配置
scoring_weights = {
    "personality_match": 0.25,    # 性格匹配
    "interests_match": 0.20,      # 兴趣匹配
    "career_match": 0.20,         # 职业匹配
    "values_match": 0.15,         # 价值观匹配
    "request_match": 0.15,        # 诉求匹配
    "complementary_match": 0.05   # 互补性匹配
}
```

### AI增强分析
- **语义理解**: 深度理解用户档案和诉求描述
- **智能推理**: 基于上下文的兼容性推理
- **个性化建议**: 针对性的关系发展建议

### 评分体系
- **0-3分**: 匹配度较低，不建议联系
- **4-5分**: 一般匹配，可以了解
- **6-7分**: 较好匹配，值得深入交流  
- **8-10分**: 高度匹配，强烈推荐

## 📊 API接口

### 核心接口
```bash
# 用户匹配
POST /api/match/analyze
POST /api/match/search

# 用户管理  
GET /api/users/profile
PUT /api/users/profile
POST /api/users/register

# 解锁功能
POST /api/unlock/attempt
GET /api/unlock/status

# 聊天服务
POST /api/chat/personality
GET /api/chat/history
```

详细API文档请访问: http://localhost:8000/docs

## 🔧 配置说明

### 环境变量
```bash
# .env.local
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
OPENAI_API_KEY=your_openai_key
KIMI_API_KEY=your_moonshot_key
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

### 配置文件
- `configs/config.py`: 后端配置参数
- `configs/prompts/prompts.yaml`: AI提示词模板
- `frontend/next.config.js`: 前端构建配置

## 🛠️ 开发工具

### 可用命令
```bash
make dev          # 开发模式
make test         # 运行测试  
make clean        # 清理临时文件
make status       # 检查服务状态
make logs         # 查看日志
make stop         # 停止所有服务
make restart      # 重启服务
```

### 代码规范
- 后端遵循 PEP 8 Python编码规范
- 前端使用 ESLint + Prettier 格式化
- 使用 TypeScript 确保类型安全

## 🔒 安全特性

- **数据加密**: 敏感信息端到端加密
- **身份认证**: JWT + Supabase 安全认证  
- **隐私保护**: 最小化数据收集原则
- **API安全**: 请求限流和权限控制

## 📈 性能优化

- **算法优化**: 向量化计算和批处理
- **缓存机制**: Redis缓存热点数据
- **异步处理**: 非阻塞IO和并发处理
- **前端优化**: 代码分割和懒加载

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

1. Fork项目仓库
2. 创建功能分支: `git checkout -b feature/new-feature`
3. 提交更改: `git commit -m 'Add new feature'`
4. 推送分支: `git push origin feature/new-feature`
5. 提交Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 🆘 问题反馈

遇到问题？
- 📧 邮箱: support@impromptu.ai
- 🐛 Issue: [GitHub Issues](https://github.com/your-repo/issues)
- 📖 文档: [项目文档](./docs/)

---

⭐ 如果这个项目对您有帮助，请给我们一个Star！
