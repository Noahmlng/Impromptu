#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简化的功能测试脚本
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

def test_basic_import():
    """测试基本导入"""
    try:
        from backend.models import CompatibilityResult
        from configs.config import ConfigManager
        print("✅ 基本模块导入成功")
        return True
    except Exception as e:
        print(f"❌ 基本导入失败: {e}")
        return False

def test_analyzer_import():
    """测试分析器导入"""
    try:
        from backend.algorithms.tag_compatibility_analyzer import EnhancedCompatibilityAnalyzer
        print("✅ 分析器导入成功")
        return True
    except Exception as e:
        print(f"❌ 分析器导入失败: {e}")
        return False

def test_analyzer_creation():
    """测试分析器创建"""
    try:
        from backend.algorithms.tag_compatibility_analyzer import EnhancedCompatibilityAnalyzer
        analyzer = EnhancedCompatibilityAnalyzer()
        print("✅ 分析器创建成功")
        return True
    except Exception as e:
        print(f"❌ 分析器创建失败: {e}")
        return False

def main():
    print("🧪 Impromptu 简化功能测试")
    print("=" * 30)
    
    tests = [
        test_basic_import,
        test_analyzer_import,
        test_analyzer_creation
    ]
    
    passed = 0
    for i, test in enumerate(tests, 1):
        print(f"\n{i}. {test.__doc__}")
        if test():
            passed += 1
    
    print(f"\n📊 测试结果: {passed}/{len(tests)} 通过")
    
    if passed == len(tests):
        print("🎉 基本功能正常！")
        return True
    else:
        print("❌ 部分测试失败")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 