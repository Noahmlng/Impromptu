# Impromptu - AI社交匹配算法系统

基于LDA主题建模和向量相似度计算的智能社交匹配系统，专为找队友、寻合伙人等场景设计。

## 🎯 核心功能

- **多维度兼容性分析**: 性格、兴趣、职业、价值观、诉求等6个维度的深度匹配
- **智能主题建模**: 基于LDA的用户档案主题提取和相似度计算
- **向量化匹配**: 使用Faiss进行高效的用户向量相似度搜索
- **动态诉求匹配**: 支持实时输入匹配需求，灵活调整匹配策略
- **RESTful API**: 完整的Web API接口，支持前端集成
- **Web界面**: 直观的用户界面，支持档案上传和匹配结果展示

## 📁 项目结构

```
Impromptu/
├── src/                    # 源代码
│   ├── algorithms/         # 核心算法
│   │   ├── tag_compatibility_analyzer.py  # 主匹配算法
│   │   ├── llm_compatibility_analyzer.py  # LLM增强分析
│   │   └── user_profile_analyzer.py       # 用户档案分析
│   ├── models/             # 数据模型
│   │   ├── topic_modeling.py    # LDA主题建模
│   │   ├── vector_matching.py   # 向量匹配
│   │   ├── tag_matching.py      # 标签匹配
│   │   └── ...
│   ├── services/           # 服务层
│   │   └── api_server.py   # Flask API服务器
│   └── utils/              # 工具函数
├── data/                   # 数据目录
│   ├── raw/               # 原始数据
│   │   └── profiles/      # 用户档案JSON文件
│   ├── processed/         # 处理后数据
│   │   └── user_vectors/  # 用户向量数据
│   ├── models/            # 训练好的模型
│   └── results/           # 匹配结果
├── scripts/               # 脚本目录
│   ├── demo/              # 演示脚本
│   │   ├── main.py        # 主演示程序
│   │   └── ...
│   ├── setup/             # 安装配置脚本
│   │   ├── install.sh     # 项目安装脚本
│   │   └── start_api.sh   # API启动脚本
│   └── train/             # 训练脚本
│       └── train_models.py # 模型训练
├── web/                   # 前端文件
│   ├── index.html         # 主页面
│   ├── app.js            # 前端逻辑
│   └── style.css         # 样式文件
├── configs/               # 配置文件
│   ├── config.py         # 主配置
│   └── prompts/          # 提示词模板
├── tests/                 # 测试文件
├── docs/                  # 文档目录
└── requirements.txt       # 依赖列表
```

## 🚀 快速开始

### 1. 安装依赖

```bash
# 克隆项目
git clone <repository-url>
cd Impromptu

# 运行安装脚本
bash scripts/setup/install.sh
```

### 2. 准备数据

将用户档案JSON文件放入 `data/raw/profiles/` 目录，格式参考：

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

### 3. 训练模型

```bash
# 激活虚拟环境
source venv/bin/activate

# 训练模型
python scripts/train/train_models.py
```

### 4. 运行演示

```bash
# 命令行演示
python scripts/demo/main.py

# 启动API服务
bash scripts/setup/start_api.sh

# 访问Web界面
open http://localhost:8000
```

## 💡 使用方法

### 命令行演示
运行 `python scripts/demo/main.py`，输入匹配诉求，系统会：
1. 分析所有用户档案
2. 计算多维度兼容性评分
3. 按匹配度排序输出结果

### API接口
启动API服务后，可使用以下端点：

- `POST /api/match` - 用户匹配分析
- `POST /api/upload` - 上传用户档案
- `GET /api/profiles` - 获取用户列表
- `GET /health` - 健康检查

### Web界面
访问 http://localhost:8000 使用图形界面：
1. 上传用户档案
2. 输入匹配需求
3. 查看匹配结果和评分详情

## 🧠 算法原理

### 多维度匹配
系统从6个维度分析用户兼容性：
- **性格匹配**: MBTI、性格特征相似度
- **兴趣匹配**: 共同兴趣和爱好重叠度
- **职业匹配**: 专业背景和技能互补性
- **价值观匹配**: 人生观、工作观一致性
- **诉求匹配**: 具体需求的契合度
- **互补匹配**: 能力和资源的互补性

### 技术栈
- **LDA主题建模**: 提取用户档案的潜在主题
- **Faiss向量搜索**: 高效的相似度计算
- **中文NLP**: jieba分词 + 停用词过滤
- **机器学习**: scikit-learn + gensim

## 📊 评分系统

每个维度使用0-10分评分：
- 8-10分: 高度匹配
- 6-7分: 较好匹配  
- 4-5分: 一般匹配
- 0-3分: 匹配度较低

总体评分为各维度加权平均，重点关注诉求匹配度。

## 🔧 配置说明

主要配置文件：
- `configs/config.py`: 系统配置参数
- `configs/prompts/prompts.yaml`: LLM提示词模板
- `requirements.txt`: Python依赖包

## 📄 许可证

本项目使用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件
