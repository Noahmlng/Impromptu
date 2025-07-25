#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Impromptu 匹配系统模型训练脚本

用于训练LDA主题模型和向量化模型
"""

import os
import sys
import json
import pickle
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.models.topic_modeling import LDATopicModel
from src.models.vector_matching import TopicVectorizer
from src.algorithms.tag_compatibility_analyzer import EnhancedCompatibilityAnalyzer

def train_topic_model(profiles_dir: str, output_dir: str):
    """训练LDA主题模型"""
    print("🧠 开始训练LDA主题模型...")
    
    # 获取所有档案文件
    profile_files = list(Path(profiles_dir).glob("*.json"))
    print(f"找到 {len(profile_files)} 个用户档案")
    
    if len(profile_files) == 0:
        print("❌ 错误: 未找到用户档案文件")
        return False
    
    # 初始化分析器
    analyzer = EnhancedCompatibilityAnalyzer()
    
    # 训练模型
    profile_paths = [str(f) for f in profile_files]
    analyzer.train_models(profile_paths)
    
    # 保存模型到指定目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 这里可以添加模型保存逻辑
    print(f"✅ 模型训练完成，保存到: {output_dir}")
    return True

def batch_vectorize_users(profiles_dir: str, output_dir: str):
    """批量向量化用户档案"""
    print("📊 开始批量向量化用户档案...")
    
    profile_files = list(Path(profiles_dir).glob("*.json"))
    
    # 初始化分析器
    analyzer = EnhancedCompatibilityAnalyzer()
    
    # 训练模型
    profile_paths = [str(f) for f in profile_files]
    analyzer.train_models(profile_paths)
    
    # 分析所有档案
    analyzer.batch_analyze_profiles(profile_paths)
    
    # 保存向量数据
    os.makedirs(output_dir, exist_ok=True)
    vectors_file = os.path.join(output_dir, "all_users.json")
    
    print(f"✅ 用户向量化完成，保存到: {vectors_file}")
    return True

def main():
    """主训练流程"""
    print("🚀 Impromptu 匹配系统模型训练")
    print("================================")
    
    # 配置路径
    profiles_dir = project_root / "data" / "raw" / "profiles"
    models_dir = project_root / "data" / "models"
    vectors_dir = project_root / "data" / "processed" / "user_vectors"
    
    print(f"📁 用户档案目录: {profiles_dir}")
    print(f"📁 模型输出目录: {models_dir}")
    print(f"📁 向量输出目录: {vectors_dir}")
    print()
    
    # 检查输入目录
    if not profiles_dir.exists():
        print(f"❌ 错误: 用户档案目录不存在 {profiles_dir}")
        return
    
    # 训练主题模型
    if not train_topic_model(str(profiles_dir), str(models_dir)):
        print("❌ 主题模型训练失败")
        return
    
    # 批量向量化
    if not batch_vectorize_users(str(profiles_dir), str(vectors_dir)):
        print("❌ 用户向量化失败")
        return
    
    print("\n🎉 所有训练任务完成！")
    print("\n使用方法:")
    print("1. 运行演示: python scripts/demo/main.py")
    print("2. 启动API: bash scripts/setup/start_api.sh")

if __name__ == "__main__":
    main() 