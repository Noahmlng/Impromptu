#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
快速功能测试脚本

验证项目核心功能是否正常工作
"""

import sys
import os
import json
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

def test_basic_imports():
    """测试基本模块导入"""
    print("🔧 测试模块导入...")
    
    try:
        from src.models import CompatibilityResult, UserRequest
        print("✅ 数据模型导入成功")
        
        from configs.config import ConfigManager
        print("✅ 配置管理导入成功")
        
        from src.algorithms.tag_compatibility_analyzer import EnhancedCompatibilityAnalyzer
        print("✅ 核心算法导入成功")
        
        return True
    except Exception as e:
        print(f"❌ 模块导入失败: {e}")
        return False

def test_analyzer_initialization():
    """测试分析器初始化"""
    print("\n🧠 测试分析器初始化...")
    
    try:
        from src.algorithms.tag_compatibility_analyzer import EnhancedCompatibilityAnalyzer
        
        analyzer = EnhancedCompatibilityAnalyzer()
        print("✅ 分析器初始化成功")
        
        return True
    except Exception as e:
        print(f"❌ 分析器初始化失败: {e}")
        return False

def test_profile_loading():
    """测试用户档案加载"""
    print("\n📄 测试用户档案加载...")
    
    try:
        profiles_dir = Path("data/raw/profiles")
        profile_files = list(profiles_dir.glob("*.json"))
        
        if len(profile_files) == 0:
            print("❌ 未找到用户档案文件")
            return False
        
        # 测试加载第一个档案
        with open(profile_files[0], 'r', encoding='utf-8') as f:
            profile = json.load(f)
        
        print(f"✅ 成功加载用户档案: {profile_files[0].name}")
        print(f"   用户: {profile.get('basic_info', {}).get('name', '未知')}")
        
        return True
    except Exception as e:
        print(f"❌ 档案加载失败: {e}")
        return False

def test_simple_matching():
    """测试简单匹配功能"""
    print("\n🔍 测试简单匹配功能...")
    
    try:
        from src.algorithms.tag_compatibility_analyzer import EnhancedCompatibilityAnalyzer
        
        # 获取两个测试档案
        profiles_dir = Path("data/raw/profiles")
        profile_files = list(profiles_dir.glob("*.json"))
        
        if len(profile_files) < 2:
            print("❌ 需要至少2个用户档案进行测试")
            return False
        
        analyzer = EnhancedCompatibilityAnalyzer()
        
        # 使用前两个档案进行测试
        profile_a = str(profile_files[0])
        profile_b = str(profile_files[1])
        
        print(f"   测试档案A: {profile_files[0].name}")
        print(f"   测试档案B: {profile_files[1].name}")
        
        # 执行简单匹配
        result = analyzer.analyze_and_output_simple_result(profile_a, profile_b)
        result_data = json.loads(result)
        
        if 'matching_analysis' in result_data:
            overall_score = result_data['matching_analysis']['overall_match']['score']
            print(f"✅ 匹配分析完成，总体评分: {overall_score:.1f}/10")
        else:
            print("✅ 匹配分析完成")
        
        return True
    except Exception as e:
        print(f"❌ 匹配测试失败: {e}")
        return False

def main():
    """主测试流程"""
    print("🧪 Impromptu 快速功能测试")
    print("=" * 40)
    
    tests = [
        test_basic_imports,
        test_analyzer_initialization,
        test_profile_loading,
        test_simple_matching
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 40)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！项目功能正常。")
        print("\n🚀 可以开始使用:")
        print("1. 运行演示: make demo")
        print("2. 启动API: make api")
        print("3. 启动Web: make web")
        return True
    else:
        print("❌ 部分测试失败，请检查项目配置。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 