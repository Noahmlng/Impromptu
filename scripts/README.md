# Scripts 目录

项目的各种脚本工具，按功能分类组织。

## 目录结构

```
scripts/
├── demo/               # 演示脚本
│   ├── main.py         # 主演示程序
│   ├── quick_test.py   # 快速测试
│   └── ...
├── setup/              # 安装配置脚本
│   ├── install.sh      # 项目安装脚本
│   ├── start_api.sh    # API启动脚本
│   ├── start_web.sh    # Web启动脚本
│   └── check_environment.py # 环境检查
├── train/              # 模型训练脚本
│   └── train_models.py # 模型训练
├── deployment/         # 部署脚本
│   └── deploy_test.sh  # 部署测试
├── database/           # 数据库相关脚本
│   ├── debug_auth_flow.py
│   ├── test_supabase_auth.py
│   ├── migrate_users_to_auth.py
│   └── ...
└── data_processing/    # 数据处理脚本
    ├── batch_register_users.py
    ├── batch_generate_tags.py
    └── import_profiles_to_db.py
```

## 使用说明

### 快速开始
```bash
# 环境检查
python scripts/setup/check_environment.py

# 安装项目
bash scripts/setup/install.sh

# 启动API服务（推荐使用新的统一入口）
python backend/main.py comprehensive
```

### 演示和测试
```bash
# 运行主演示
python scripts/demo/main.py

# 快速测试
python scripts/demo/quick_test.py
```

### 数据库操作
```bash
# 导入用户档案到数据库
python scripts/data_processing/import_profiles_to_db.py

# 批量注册用户
python scripts/data_processing/batch_register_users.py

# 测试数据库连接
python scripts/database/test_supabase_connection.py
```

### 模型训练
```bash
# 训练LDA主题模型
python scripts/train/train_models.py
```

## 注意事项

- 推荐使用 `python backend/main.py comprehensive` 启动API服务
- 运行脚本前请确保已激活虚拟环境并安装依赖
- 数据库相关脚本需要正确配置Supabase环境变量 