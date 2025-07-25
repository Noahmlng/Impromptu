#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import sys
import requests
import time
import yaml
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# 添加项目根目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from configs.config import ConfigManager
from src.models import CompatibilityResult, UserRequest

class KimiCompatibilityAnalyzer:
    def __init__(self, config: Optional[ConfigManager] = None, api_key: str = None, prompts_file: str = "prompts/prompts.yaml"):
        self.config_manager = config or ConfigManager()
        
        if api_key:
            self.config_manager.api_config.api_key = api_key
        
        if not self.config_manager.validate():
            raise ValueError("API key is required")
        
        self.api_config = self.config_manager.api_config
        self.analysis_config = self.config_manager.analysis_config
        
        # Load prompts from YAML file
        self.prompts = self.load_prompts(prompts_file)
    
    def load_prompts(self, prompts_file: str) -> Dict[str, Any]:
        """Load prompts from YAML file"""
        with open(prompts_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def load_profile(self, profile_path: str) -> Dict[str, Any]:
        """Load profile from JSON file"""
        with open(profile_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def extract_user_request(self, profile: Dict[str, Any]) -> UserRequest:
        """从profile中提取用户诉求"""
        request_data = profile.get('user_request', {})
        
        # 如果没有诉求数据，返回默认值
        if not request_data:
            return UserRequest(
                request_type="找队友",
                description="寻找志同道合的合作伙伴"
            )
        
        return UserRequest(
            request_type=request_data.get('request_type', '找队友'),
            description=request_data.get('description', '寻找志同道合的合作伙伴')
        )
    
    def format_request_for_prompt(self, user_request: UserRequest) -> str:
        """格式化诉求信息用于prompt"""
        return f"""
诉求类型: {user_request.request_type}
诉求描述: {user_request.description}
"""
    
    def create_prompts(self, person_a: Dict, person_b: Dict) -> tuple[str, str]:
        """Create system and user prompts for compatibility analysis"""
        
        # 提取诉求信息
        request_a = self.extract_user_request(person_a)
        request_b = self.extract_user_request(person_b)
        
        # 获取system prompt
        system_prompt = self.prompts['compatibility_analysis']['system_prompt']
        
        # 创建user prompt
        user_prompt_template = self.prompts['compatibility_analysis']['user_prompt']
        user_prompt = user_prompt_template.format(
            person_a_profile=json.dumps(person_a, ensure_ascii=False, indent=2),
            person_b_profile=json.dumps(person_b, ensure_ascii=False, indent=2),
            person_a_request=self.format_request_for_prompt(request_a),
            person_b_request=self.format_request_for_prompt(request_b)
        )
        
        return system_prompt, user_prompt
    
    def call_kimi_api(self, system_prompt: str, user_prompt: str) -> str:
        """Call Kimi API with system and user messages"""
        
        payload = {
            "model": self.api_config.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": self.api_config.temperature,
            "max_tokens": self.api_config.max_tokens
        }
        
        for attempt in range(self.api_config.max_retries):
            try:
                response = requests.post(
                    self.api_config.chat_endpoint,
                    headers=self.api_config.headers,
                    json=payload,
                    timeout=self.api_config.timeout
                )
                
                response.raise_for_status()
                result = response.json()
                
                if 'choices' in result and len(result['choices']) > 0:
                    return result['choices'][0]['message']['content']
                else:
                    raise ValueError("Invalid response format")
                    
            except Exception as e:
                if attempt < self.api_config.max_retries - 1:
                    time.sleep(self.api_config.retry_delay)
                else:
                    raise Exception(f"API call failed after {self.api_config.max_retries} attempts: {str(e)}")
    
    def parse_analysis_result(self, analysis_text: str, person_a_name: str, person_b_name: str) -> CompatibilityResult:
        """Parse analysis result from API response"""
        
        # 首先尝试解析JSON格式的回复
        try:
            import re
            json_match = re.search(r'\{.*\}', analysis_text, re.DOTALL)
            if json_match:
                analysis_json = json.loads(json_match.group())
                
                return CompatibilityResult(
                    person_a=person_a_name,
                    person_b=person_b_name,
                    mutual_interest_score=float(analysis_json.get('mutual_interest_score', 0)),
                    a_to_b_interest=float(analysis_json.get('a_to_b_interest', 0)),
                    b_to_a_interest=float(analysis_json.get('b_to_a_interest', 0)),
                    request_matching_score=float(analysis_json.get('request_matching_score', 0)),
                    personality_matching_score=float(analysis_json.get('personality_matching_score', 0)),
                    compatibility_factors=analysis_json.get('compatibility_factors', []),
                    potential_conflicts=analysis_json.get('potential_conflicts', []),
                    request_analysis=analysis_json.get('request_analysis', ''),
                    recommendation=analysis_json.get('recommendation', ''),
                    detailed_analysis=analysis_text
                )
        except (json.JSONDecodeError, ValueError):
            pass
        
        # 如果JSON解析失败，尝试从文本中提取分数
        try:
            import re
            
            def extract_score(pattern, text, default=0.0):
                match = re.search(pattern, text)
                if match:
                    return float(match.group(1))
                return default
            
            mutual_score = extract_score(r'mutual_interest_score.*?:?\s*(\d+(?:\.\d+)?)', analysis_text)
            a_to_b_score = extract_score(r'a_to_b_interest.*?:?\s*(\d+(?:\.\d+)?)', analysis_text)
            b_to_a_score = extract_score(r'b_to_a_interest.*?:?\s*(\d+(?:\.\d+)?)', analysis_text)
            request_score = extract_score(r'request_matching_score.*?:?\s*(\d+(?:\.\d+)?)', analysis_text)
            personality_score = extract_score(r'personality_matching_score.*?:?\s*(\d+(?:\.\d+)?)', analysis_text)
            
            # 提取文本分析
            request_analysis = ""
            recommendation = ""
            
            # 查找诉求分析部分
            request_match = re.search(r'### 诉求匹配分析\s*\n\n(.*?)(?=\n\n###|\n\n```|\Z)', analysis_text, re.DOTALL)
            if request_match:
                request_analysis = request_match.group(1).strip()
            
            # 查找建议部分
            rec_match = re.search(r'### 关系发展建议\s*\n\n(.*?)(?=\n\n###|\n\n```|\Z)', analysis_text, re.DOTALL)
            if rec_match:
                recommendation = rec_match.group(1).strip()
            
            return CompatibilityResult(
                person_a=person_a_name,
                person_b=person_b_name,
                mutual_interest_score=mutual_score,
                a_to_b_interest=a_to_b_score,
                b_to_a_interest=b_to_a_score,
                request_matching_score=request_score,
                personality_matching_score=personality_score,
                compatibility_factors=[],
                potential_conflicts=[],
                request_analysis=request_analysis or "需要人工分析",
                recommendation=recommendation or "建议进一步沟通了解",
                detailed_analysis=analysis_text
            )
            
        except Exception:
            pass
        
        # 最终fallback
        return CompatibilityResult(
            person_a=person_a_name,
            person_b=person_b_name,
            mutual_interest_score=0.0,
            a_to_b_interest=0.0,
            b_to_a_interest=0.0,
            request_matching_score=0.0,
            personality_matching_score=0.0,
            compatibility_factors=[],
            potential_conflicts=[],
            request_analysis="需要人工分析",
            recommendation="Manual analysis needed",
            detailed_analysis=analysis_text
        )
    
    def analyze_compatibility(self, profile_a_path: str, profile_b_path: str) -> CompatibilityResult:
        """Analyze compatibility between two people"""
        
        profile_a = self.load_profile(profile_a_path)
        profile_b = self.load_profile(profile_b_path)
        
        person_a_name = profile_a.get('profile', {}).get('name', {}).get('display_name', 'Person A')
        person_b_name = profile_b.get('profile', {}).get('name', {}).get('display_name', 'Person B')
        
        system_prompt, user_prompt = self.create_prompts(profile_a, profile_b)
        analysis_text = self.call_kimi_api(system_prompt, user_prompt)
        
        return self.parse_analysis_result(analysis_text, person_a_name, person_b_name)
    
    def batch_analyze(self, profile_paths: List[str]) -> List[CompatibilityResult]:
        """Analyze compatibility between all pairs"""
        
        results = []
        for i in range(len(profile_paths)):
            for j in range(i + 1, len(profile_paths)):
                try:
                    result = self.analyze_compatibility(profile_paths[i], profile_paths[j])
                    results.append(result)
                except Exception as e:
                    continue  # Skip failed analyses
        
        return results
    
    def save_results(self, results: List[CompatibilityResult], output_path: str = "data/results/compatibility_results.json"):
        """Save analysis results to JSON file"""
        
        results_data = []
        for result in results:
            results_data.append({
                "person_a": result.person_a,
                "person_b": result.person_b,
                "mutual_interest_score": result.mutual_interest_score,
                "a_to_b_interest": result.a_to_b_interest,
                "b_to_a_interest": result.b_to_a_interest,
                "request_matching_score": result.request_matching_score,
                "personality_matching_score": result.personality_matching_score,
                "compatibility_factors": result.compatibility_factors,
                "potential_conflicts": result.potential_conflicts,
                "request_analysis": result.request_analysis,
                "recommendation": result.recommendation,
                "detailed_analysis": result.detailed_analysis
            })
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results_data, f, ensure_ascii=False, indent=2)

def main():
    """Simple example usage"""
    
    try:
        analyzer = KimiCompatibilityAnalyzer()
    except ValueError:
        return
    
    # Profile files in data/profiles directory
    profiles = [
        "data/profiles/noah_profile.json",
        "data/profiles/kyrie_profile.json", 
        "data/profiles/alan_profile.json"
    ]
    
    # Filter existing profiles
    existing_profiles = [p for p in profiles if __import__('os').path.exists(p)]
    
    if len(existing_profiles) < 2:
        return
    
    # Analyze all pairs
    results = analyzer.batch_analyze(existing_profiles)
    
    # Save results
    analyzer.save_results(results)
    
    # Simple output
    for result in results:
        print(f"{result.person_a} ↔ {result.person_b}: {result.mutual_interest_score}/10 (诉求匹配: {result.request_matching_score}/10)")

if __name__ == "__main__":
    main() 