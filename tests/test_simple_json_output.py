#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简洁JSON输出测试程序

测试新的简洁JSON输出格式，只包含各个方向的匹配值和匹配描述
"""

import sys
import os
import json
import tempfile
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.algorithms.tag_compatibility_analyzer import EnhancedCompatibilityAnalyzer

def test_simple_json_output():
    """测试简洁JSON输出"""
    
    print("🔍 测试简洁JSON输出格式")
    print("=" * 50)
    
    # 档案路径
    noah_path = "data/profiles/noah_profile.json"
    alan_path = "data/profiles/alan_profile.json"
    
    # 检查文件存在
    if not os.path.exists(noah_path) or not os.path.exists(alan_path):
        print("❌ 档案文件不存在")
        return
    
    try:
        # 初始化分析器
        analyzer = EnhancedCompatibilityAnalyzer()
        
        print("🧠 开始分析...")
        
        # 生成简洁JSON输出
        json_result = analyzer.analyze_and_output_simple_result(noah_path, alan_path)
        
        print("\n📊 简洁JSON分析结果:")
        print("=" * 50)
        print(json_result)
        
        # 保存结果
        output_file = "data/results/simple_matching_result.json"
        os.makedirs("data/results", exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(json_result)
        
        print(f"\n💾 结果已保存到: {output_file}")
        
        # 解析并展示关键信息
        result_data = json.loads(json_result)
        
        print("\n🎯 关键评分:")
        print("=" * 30)
        
        matching_analysis = result_data["matching_analysis"]
        for dimension, data in matching_analysis.items():
            print(f"{dimension:20s}: {data['score']:5.2f} - {data['description']}")
        
        print("\n📝 详细描述:")
        print("=" * 30)
        for dimension, data in matching_analysis.items():
            if data.get('details'):
                print(f"• {dimension}: {data['details']}")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

def compare_outputs():
    """对比详细输出和简洁输出"""
    
    print("\n🔄 对比详细输出 vs 简洁输出")
    print("=" * 50)
    
    # 读取之前的详细结果
    detailed_file = "data/results/noah_alan_matching_result.json"
    simple_file = "data/results/simple_matching_result.json"
    
    try:
        if os.path.exists(detailed_file):
            with open(detailed_file, 'r', encoding='utf-8') as f:
                detailed_data = json.load(f)
            print(f"📄 详细结果文件大小: {os.path.getsize(detailed_file)} 字节")
            print(f"📋 详细结果包含字段: {len(detailed_data)} 个主要字段")
        
        if os.path.exists(simple_file):
            with open(simple_file, 'r', encoding='utf-8') as f:
                simple_data = json.load(f)
            print(f"📄 简洁结果文件大小: {os.path.getsize(simple_file)} 字节")
            print(f"📋 简洁结果包含维度: {len(simple_data.get('matching_analysis', {}))} 个匹配维度")
            
            # 显示数据结构对比
            print("\n📊 简洁输出结构:")
            print("├── participants (参与者信息)")
            print("└── matching_analysis (匹配分析)")
            for dimension in simple_data.get('matching_analysis', {}):
                print(f"    ├── {dimension}")
                print("    │   ├── score (评分)")
                print("    │   ├── description (描述)")
                print("    │   └── details (详情)")
    
    except Exception as e:
        print(f"❌ 对比失败: {e}")

def demo_api_usage():
    """演示API使用方式"""
    
    print("\n🚀 API使用演示")
    print("=" * 50)
    
    print("1. 直接获取JSON字符串:")
    print("```python")
    print("analyzer = EnhancedCompatibilityAnalyzer()")
    print("json_result = analyzer.analyze_and_output_simple_result(profile_a, profile_b)")
    print("print(json_result)")
    print("```")
    
    print("\n2. 解析为Python字典:")
    print("```python")
    print("import json")
    print("result_dict = json.loads(json_result)")
    print("overall_score = result_dict['matching_analysis']['overall_match']['score']")
    print("```")
    
    print("\n3. 获取特定维度评分:")
    print("```python")
    print("personality_score = result_dict['matching_analysis']['personality_match']['score']")
    print("career_score = result_dict['matching_analysis']['career_match']['score']")
    print("complementary_score = result_dict['matching_analysis']['complementary_match']['score']")
    print("```")
    
    print("\n✨ 输出特点:")
    print("• 结构化JSON格式，易于解析")
    print("• 7个维度的评分和描述")
    print("• 每个维度包含：score(评分) + description(描述) + details(详情)")
    print("• 文件大小大幅减少，适合API调用")
    print("• 保留核心匹配信息，去除冗余数据")

if __name__ == "__main__":
    print("🎯 简洁JSON输出测试")
    print("基于LDA主题建模 + Faiss向量匹配")
    print("=" * 60)
    
    # 运行测试
    test_simple_json_output()
    
    # 对比输出
    compare_outputs()
    
    # 演示用法
    demo_api_usage()
    
    print("\n✅ 测试完成!")
    print("现在你可以使用 analyzer.analyze_and_output_simple_result() 方法")
    print("直接获取简洁的JSON格式匹配结果！") 