#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Impromptu 匹配系统主入口

统一的命令行接口，支持多种运行模式
"""

import sys
import os
import argparse
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def run_demo():
    """运行演示程序"""
    from scripts.demo.main import main
    main()

def run_api():
    """启动API服务"""
    os.system("bash scripts/setup/start_api.sh")

def run_train():
    """训练模型"""
    from scripts.train.train_models import main
    main()

def run_web():
    """启动Web界面"""
    os.system("bash scripts/setup/start_web.sh")

def main():
    parser = argparse.ArgumentParser(description='Impromptu 匹配系统')
    parser.add_argument('mode', choices=['demo', 'api', 'train', 'web', 'setup'], 
                       help='运行模式')
    parser.add_argument('--port', type=int, default=5000, help='API服务端口')
    
    args = parser.parse_args()
    
    print("🚀 Impromptu - AI社交匹配算法系统")
    print("=" * 40)
    
    if args.mode == 'demo':
        print("📱 启动命令行演示...")
        run_demo()
    elif args.mode == 'api':
        print("🌐 启动API服务...")
        run_api()
    elif args.mode == 'train':
        print("🧠 开始模型训练...")
        run_train()
    elif args.mode == 'web':
        print("💻 启动Web界面...")
        run_web()
    elif args.mode == 'setup':
        print("🔧 运行项目安装...")
        os.system("bash scripts/setup/install.sh")
    
if __name__ == "__main__":
    main() 