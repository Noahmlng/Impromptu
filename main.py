#!/usr/bin/env python3

import os
import json
import tempfile
import sys
import importlib.util
from typing import List, Tuple

# 直接导入tag_compatibility_analyzer模块
spec = importlib.util.spec_from_file_location(
    "tag_compatibility_analyzer", 
    os.path.join(os.path.dirname(__file__), "tests", "tag_compatibility_analyzer.py")
)
tag_analyzer_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tag_analyzer_module)
EnhancedCompatibilityAnalyzer = tag_analyzer_module.EnhancedCompatibilityAnalyzer

def create_temporary_noah_profile(original_path: str, new_request: str) -> str:
    """创建临时的noah档案，包含新的诉求"""
    with open(original_path, 'r', encoding='utf-8') as f:
        noah_profile = json.load(f)
    
    # 更新用户诉求
    noah_profile['user_request'] = {
        'request_type': '找队友',
        'description': new_request
    }
    
    # 创建临时文件
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8')
    json.dump(noah_profile, temp_file, ensure_ascii=False, indent=2)
    temp_file.close()
    
    return temp_file.name

def get_all_other_profiles(profiles_dir: str, exclude_name: str = "noah_profile.json") -> List[str]:
    """获取除了指定文件外的所有档案路径"""
    profiles = []
    for filename in os.listdir(profiles_dir):
        if filename.endswith('.json') and filename != exclude_name:
            profile_path = os.path.join(profiles_dir, filename)
            if os.path.exists(profile_path):
                profiles.append(profile_path)
    return profiles

def main():
    """主程序：使用noah作为匹配者，动态输入诉求，匹配所有其他用户"""
    
    print("=== AI队友匹配系统 ===")
    print("默认匹配者: Noah (泽铭)")
    print()
    
    # 检查noah档案是否存在
    noah_profile_path = "data/profiles/noah_profile.json"
    if not os.path.exists(noah_profile_path):
        print(f"错误：找不到Noah的档案文件 {noah_profile_path}")
        return
    
    # 获取用户输入的诉求
    print("请输入Noah这次希望匹配的诉求描述：")
    print("(例如：寻找有前端开发经验的技术合伙人，希望一起做AI产品)")
    user_request = input(">>> ").strip()
    
    if not user_request:
        user_request = "正在做AI Agent创业，寻找技术合伙人或产品合伙人。希望找到对AI技术有深度理解，同时具备产品思维的伙伴。"
        print(f"使用默认诉求: {user_request}")
    
    print(f"\n📝 本次匹配诉求: {user_request}")
    print()
    
    # 获取所有其他档案
    profiles_dir = "data/profiles"
    other_profiles = get_all_other_profiles(profiles_dir)
    
    if len(other_profiles) == 0:
        print("错误：没有找到其他用户档案进行匹配")
        return
    
    print(f"📊 找到 {len(other_profiles)} 个候选档案")
    for profile in other_profiles:
        filename = os.path.basename(profile)
        print(f"  - {filename}")
    print()
    
    # 创建临时的noah档案（包含新诉求）
    temp_noah_path = create_temporary_noah_profile(noah_profile_path, user_request)
    
    try:
        # 初始化增强兼容性分析器
        print("🚀 初始化分析系统...")
        analyzer = EnhancedCompatibilityAnalyzer()
        
        # 准备所有档案路径（包括临时noah档案）
        all_profiles = [temp_noah_path] + other_profiles
        
        # 训练模型
        print("🧠 训练主题建模...")
        analyzer.train_models(all_profiles)
        
        # 分析所有档案
        print("📈 分析用户档案...")
        analyzer.batch_analyze_profiles(all_profiles)
        
        # 与每个候选者进行匹配分析
        print("🔍 进行兼容性分析...")
        match_results = []
        
        for other_profile in other_profiles:
            try:
                # 使用简洁输出格式
                json_result = analyzer.analyze_and_output_simple_result(temp_noah_path, other_profile)
                result_data = json.loads(json_result)
                
                # 提取关键信息
                if 'participants' in result_data:
                    other_name = result_data['participants']['person_b']
                    overall_score = result_data['matching_analysis']['overall_match']['score']
                    
                    match_results.append({
                        'name': other_name,
                        'profile_path': other_profile,
                        'score': overall_score,
                        'result_data': result_data
                    })
                else:
                    # 兼容旧格式
                    other_name = result_data.get('person_b', '未知用户')
                    overall_score = result_data.get('overall_match', {}).get('score', 0)
                    
                    match_results.append({
                        'name': other_name,
                        'profile_path': other_profile,
                        'score': overall_score,
                        'result_data': result_data
                    })
                
            except Exception as e:
                print(f"⚠️  分析 {other_profile} 时出错: {e}")
        
        # 按评分排序（从高到低）
        match_results.sort(key=lambda x: x['score'], reverse=True)
        
        # 输出匹配结果
        print(f"\n🎯 匹配结果 (共 {len(match_results)} 个候选者):")
        print("=" * 60)
        
        for i, match in enumerate(match_results, 1):
            result_data = match['result_data']
            print(f"\n{i}. {match['name']} - 总体匹配度: {match['score']:.1f}/10")
            print(f"   📁 档案: {os.path.basename(match['profile_path'])}")
            
            # 显示各维度评分
            dimensions = [
                ('性格匹配', 'personality_match'),
                ('兴趣匹配', 'interests_match'), 
                ('职业匹配', 'career_match'),
                ('价值观匹配', 'values_match'),
                ('诉求匹配', 'request_match'),
                ('互补性', 'complementary_match')
            ]
            
            print("   📊 详细评分:")
            
            # 适应新的JSON结构
            if 'matching_analysis' in result_data:
                analysis_data = result_data['matching_analysis']
                for dim_name, dim_key in dimensions:
                    if dim_key in analysis_data:
                        score = analysis_data[dim_key]['score']
                        desc = analysis_data[dim_key]['description']
                        print(f"      {dim_name}: {score:.1f}/10 - {desc}")
                
                print(f"   💡 总体评价: {analysis_data['overall_match']['description']}")
            else:
                # 兼容旧格式
                for dim_name, dim_key in dimensions:
                    if dim_key in result_data:
                        score = result_data[dim_key]['score']
                        desc = result_data[dim_key]['description']
                        print(f"      {dim_name}: {score:.1f}/10 - {desc}")
                
                if 'overall_match' in result_data:
                    print(f"   💡 总体评价: {result_data['overall_match']['description']}")
            
            print("-" * 60)
        
        # 保存详细结果
        output_file = "data/results/noah_matching_results.json"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        output_data = {
            'matcher': 'Noah (泽铭)',
            'request': user_request,
            'timestamp': None,  # 可以添加时间戳
            'results': [match['result_data'] for match in match_results]
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 详细结果已保存到: {output_file}")
        
        if match_results:
            top_match = match_results[0]
            print(f"\n🏆 最佳匹配: {top_match['name']} (评分: {top_match['score']:.1f}/10)")
        
    except Exception as e:
        print(f"❌ 分析过程中出错: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 清理临时文件
        if os.path.exists(temp_noah_path):
            os.unlink(temp_noah_path)

if __name__ == "__main__":
    main() 