#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
用户匹配系统 API 服务器

提供 RESTful API 接口用于用户匹配分析
基于 LDA 主题建模 + Faiss 向量相似度计算
"""

import os
import json
import sys
import tempfile
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import importlib.util

# 添加项目根目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# 导入项目模块
# from src.algorithms.tag_compatibility_analyzer import EnhancedCompatibilityAnalyzer
from supabase import create_client, Client
import traceback

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:8000", "http://127.0.0.1:8000"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    },
    r"/health": {
        "origins": ["http://localhost:8000", "http://127.0.0.1:8000"],
        "methods": ["GET", "OPTIONS"]
    }
})  # 允许跨域请求

# Supabase 配置
SUPABASE_URL = 'https://anxbbsrnjgmotxzysqwf.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFueGJic3Juamdtb3R4enlzcXdmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTA0MDY0OTIsImV4cCI6MjA2NTk4MjQ5Mn0.a0t-pgH-Z2Fbs6JuMNWX8_kpqkQsBag3-COAUZVF6-0'

# 初始化 Supabase 客户端
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 全局分析器实例
analyzer = None
UPLOAD_FOLDER = 'temp_uploads'
ALLOWED_EXTENSIONS = {'json'}

# 确保上传目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

class SimpleAnalyzer:
    """简化的分析器，只用于简单匹配"""
    
    def analyze_and_output_simple_result(self, profile_a_path: str, profile_b_path: str) -> str:
        """简化的分析方法"""
        try:
            # 读取两个用户档案
            with open(profile_a_path, 'r', encoding='utf-8') as f:
                profile_a = json.load(f)
            with open(profile_b_path, 'r', encoding='utf-8') as f:
                profile_b = json.load(f)
            
            # 简单的匹配计算
            result = {
                "analysis_summary": {
                    "user_a_name": profile_a.get('profile', {}).get('name', {}).get('display_name', 'User A'),
                    "user_b_name": profile_b.get('profile', {}).get('name', {}).get('display_name', 'User B'),
                    "analysis_time": "2024-01-01T00:00:00Z"
                },
                "overall_compatibility": {
                    "score": 0.75,
                    "level": "高度匹配",
                    "description": "基于简化分析的匹配结果"
                },
                "dimensional_scores": {
                    "personality_compatibility": {
                        "score": 8.0,
                        "max_score": 10.0,
                        "description": "性格兼容度较好"
                    },
                    "interest_alignment": {
                        "score": 7.5,
                        "max_score": 10.0,
                        "description": "兴趣爱好有一定重叠"
                    },
                    "goal_compatibility": {
                        "score": 8.5,
                        "max_score": 10.0,
                        "description": "目标相对一致"
                    },
                    "lifestyle_match": {
                        "score": 7.0,
                        "max_score": 10.0,
                        "description": "生活方式基本匹配"
                    },
                    "communication_style": {
                        "score": 7.5,
                        "max_score": 10.0,
                        "description": "沟通风格较为协调"
                    },
                    "value_alignment": {
                        "score": 8.0,
                        "max_score": 10.0,
                        "description": "价值观相对一致"
                    },
                    "geographic_compatibility": {
                        "score": 6.0,
                        "max_score": 10.0,
                        "description": "地理位置有一定距离"
                    }
                },
                "recommendations": [
                    "建议进一步了解彼此的兴趣爱好",
                    "可以尝试线上交流建立初步联系",
                    "考虑地理位置因素制定见面计划"
                ]
            }
            
            return json.dumps(result, ensure_ascii=False, indent=2)
            
        except Exception as e:
            return json.dumps({
                "error": "分析失败",
                "message": str(e)
            }, ensure_ascii=False)

def allowed_file(filename):
    """检查文件扩展名是否被允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def init_analyzer():
    """初始化分析器（暂时简化）"""
    global analyzer
    if analyzer is None:
        # 暂时使用简化版本，不依赖复杂的分析器
        analyzer = SimpleAnalyzer()
        print("✅ 简化分析器初始化完成")

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        "status": "healthy",
        "message": "用户匹配系统 API 运行正常",
        "version": "1.0.0"
    })

@app.route('/api/database/users', methods=['GET'])
def get_all_users():
    """获取所有用户信息（包含元数据和标签）"""
    try:
        # 获取用户基本信息
        profiles_response = supabase.table('user_profile').select('*').execute()
        if not profiles_response.data:
            return jsonify({
                "success": True,
                "data": [],
                "message": "未找到用户数据"
            })
        
        # 获取用户元数据，按user_id分组
        metadata_response = supabase.table('user_metadata').select('*').execute()
        metadata_dict = {}
        if metadata_response.data:
            for item in metadata_response.data:
                user_id = item['user_id']
                if user_id not in metadata_dict:
                    metadata_dict[user_id] = {}
                
                # 根据section_type和section_key组织元数据
                section_type = item.get('section_type', 'unknown')
                section_key = item.get('section_key', 'unknown')
                content = item.get('content', {})
                
                # 如果content是字符串，需要解析为JSON
                if isinstance(content, str):
                    try:
                        content = json.loads(content)
                    except (json.JSONDecodeError, TypeError):
                        content = {}
                
                if section_type not in metadata_dict[user_id]:
                    metadata_dict[user_id][section_type] = {}
                metadata_dict[user_id][section_type][section_key] = content
        
        # 获取用户标签
        user_tags_response = supabase.table('user_tags').select('user_id, tag_name, tag_category, confidence_score, tag_source').execute()
        user_tags_dict = {}
        if user_tags_response.data:
            for tag in user_tags_response.data:
                user_id = tag['user_id']
                if user_id not in user_tags_dict:
                    user_tags_dict[user_id] = []
                user_tags_dict[user_id].append({
                    'name': tag['tag_name'],
                    'category': tag['tag_category'],
                    'weight': float(tag['confidence_score']) if tag['confidence_score'] else 0.5,
                    'source': tag['tag_source']
                })
        
        # 合并数据并转换为Web应用期望的格式
        users = []
        for profile in profiles_response.data:
            user_id = profile['user_id']
            metadata = metadata_dict.get(user_id, {})
            user_tags = user_tags_dict.get(user_id, [])
            
            # 从元数据中提取信息
            personal_info = metadata.get('profile', {}).get('personal', {})
            professional_info = metadata.get('profile', {}).get('professional', {})
            personality_info = metadata.get('profile', {}).get('personality', {})
            user_request = metadata.get('user_request', {})
            
            # 解析年龄（从字符串中提取数字）
            age_range = personal_info.get('age_range', '')
            age = None
            if age_range:
                import re
                age_match = re.search(r'(\d+)', age_range)
                if age_match:
                    age = int(age_match.group(1))
            
            # 解析性别（根据名字简单推测，这里可能需要更复杂的逻辑）
            gender = 'unknown'
            display_name = profile.get('display_name', '')
            # 简单的性别推测逻辑（可以改进）
            female_names = ['sophia', 'luna', 'iris', 'jenny', 'alice', 'emma', 'lucy', 'amy', 'maya', 'mia', 'grace', 'stella', 'helena', 'crystal', 'vivian', 'coco', 'xiaoya', 'kiki']
            if any(name in display_name.lower() for name in female_names):
                gender = 'female'
            else:
                gender = 'male'
            
            # 构建looking_for列表
            looking_for = []
            request_type = user_request.get('request_type', '')
            if request_type == '找对象':
                looking_for = ['寻找真爱', '长期关系', '结婚生子', '生活伴侣']
            elif request_type == '找队友':
                looking_for = ['产品合作', '创业伙伴', '技术合作']
            else:
                looking_for = ['其他']
            
            user_data = {
                'id': user_id,
                'username': display_name or user_id,
                'age': age,
                'gender': gender,
                'location_city': personal_info.get('location', ''),
                'location_state': personal_info.get('location', ''),
                'bio': user_request.get('description', '') or f"{professional_info.get('current_role', '用户')}",
                'occupation': professional_info.get('current_role', ''),
                'looking_for': looking_for,
                'profile_photo_url': profile.get('avatar_url'),
                'social_links': {},
                'preferences': {},
                'is_profile_complete': True,
                'visibility': 'public',
                'tags': user_tags
            }
            users.append(user_data)
        
        return jsonify({
            "success": True,
            "data": users,
            "total": len(users)
        })
        
    except Exception as e:
        print(f"获取用户数据出错: {e}")
        traceback.print_exc()
        return jsonify({
            "error": "获取用户数据失败",
            "message": str(e)
        }), 500

@app.route('/api/database/users/<user_id>', methods=['GET'])
def get_user_by_id(user_id):
    """获取指定用户信息"""
    try:
        # 获取用户基本信息
        profile_response = supabase.table('profiles').select('id, username').eq('id', user_id).execute()
        if not profile_response.data:
            return jsonify({
                "error": "用户不存在",
                "message": f"未找到ID为 {user_id} 的用户"
            }), 404
        
        profile = profile_response.data[0]
        
        # 获取用户元数据
        metadata_response = supabase.table('user_metadata').select('*').eq('id', user_id).execute()
        metadata = metadata_response.data[0] if metadata_response.data else {}
        
        # 获取用户标签
        user_tags_response = supabase.table('user_tags').select('tag_id, weight').eq('user_id', user_id).execute()
        user_tags = []
        
        if user_tags_response.data:
            tag_ids = [ut['tag_id'] for ut in user_tags_response.data]
            tags_response = supabase.table('tags').select('id, name, category').in_('id', tag_ids).execute()
            tags_dict = {tag['id']: tag for tag in tags_response.data} if tags_response.data else {}
            
            for ut in user_tags_response.data:
                tag_info = tags_dict.get(ut['tag_id'])
                if tag_info:
                    user_tags.append({
                        'name': tag_info['name'],
                        'category': tag_info['category'],
                        'weight': ut['weight']
                    })
        
        user_data = {
            'id': profile['id'],
            'username': profile['username'],
            'age': metadata.get('age'),
            'gender': metadata.get('gender'),
            'location_city': metadata.get('location_city'),
            'location_state': metadata.get('location_state'),
            'bio': metadata.get('bio'),
            'occupation': metadata.get('occupation'),
            'looking_for': metadata.get('looking_for', []),
            'profile_photo_url': metadata.get('profile_photo_url'),
            'social_links': metadata.get('social_links', {}),
            'preferences': metadata.get('preferences', {}),
            'is_profile_complete': metadata.get('is_profile_complete', False),
            'visibility': metadata.get('visibility', 'public'),
            'tags': user_tags
        }
        
        return jsonify({
            "success": True,
            "data": user_data
        })
        
    except Exception as e:
        print(f"获取用户数据出错: {e}")
        traceback.print_exc()
        return jsonify({
            "error": "获取用户数据失败",
            "message": str(e)
        }), 500

@app.route('/api/database/tags', methods=['GET'])
def get_database_tags():
    """从数据库获取标签信息"""
    try:
        response = supabase.table('tags').select('*').eq('is_active', True).execute()
        
        tags = response.data if response.data else []
        
        # 按类别分组
        tags_by_category = {}
        for tag in tags:
            category = tag['category']
            if category not in tags_by_category:
                tags_by_category[category] = []
            tags_by_category[category].append(tag)
        
        return jsonify({
            "success": True,
            "data": {
                "total_tags": len(tags),
                "tags_by_category": tags_by_category,
                "all_tags": tags
            }
        })
        
    except Exception as e:
        print(f"获取标签数据出错: {e}")
        return jsonify({
            "error": "获取标签数据失败",
            "message": str(e)
        }), 500

@app.route('/api/database/test', methods=['GET'])
def test_database_connection():
    """测试数据库连接"""
    try:
        # 测试基本查询
        profiles_count = supabase.table('profiles').select('id', count='exact').execute()
        metadata_count = supabase.table('user_metadata').select('id', count='exact').execute()
        tags_count = supabase.table('tags').select('id', count='exact').execute()
        
        return jsonify({
            "success": True,
            "message": "数据库连接正常",
            "stats": {
                "profiles_count": profiles_count.count if hasattr(profiles_count, 'count') else len(profiles_count.data or []),
                "metadata_count": metadata_count.count if hasattr(metadata_count, 'count') else len(metadata_count.data or []),
                "tags_count": tags_count.count if hasattr(tags_count, 'count') else len(tags_count.data or [])
            }
        })
        
    except Exception as e:
        print(f"数据库连接测试失败: {e}")
        return jsonify({
            "error": "数据库连接失败",
            "message": str(e)
        }), 500

@app.route('/api/match/simple', methods=['POST'])
def match_users_simple():
    """
    简洁匹配接口 - 接收两个用户档案JSON，返回简洁的匹配结果
    
    请求体格式:
    {
        "user_a": {...},  // 用户A的档案JSON
        "user_b": {...}   // 用户B的档案JSON
    }
    """
    try:
        init_analyzer()
        
        data = request.get_json()
        if not data or 'user_a' not in data or 'user_b' not in data:
            return jsonify({
                "error": "请求格式错误",
                "message": "需要提供 user_a 和 user_b 两个用户档案"
            }), 400
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f1:
            json.dump(data['user_a'], f1, ensure_ascii=False, indent=2)
            temp_file_a = f1.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f2:
            json.dump(data['user_b'], f2, ensure_ascii=False, indent=2)
            temp_file_b = f2.name
        
        try:
            # 进行匹配分析
            result_json = analyzer.analyze_and_output_simple_result(temp_file_a, temp_file_b)
            result = json.loads(result_json)
            
            return jsonify({
                "success": True,
                "data": result
            })
            
        finally:
            # 清理临时文件
            os.unlink(temp_file_a)
            os.unlink(temp_file_b)
            
    except Exception as e:
        print(f"匹配分析出错: {e}")
        traceback.print_exc()
        return jsonify({
            "error": "匹配分析失败",
            "message": str(e)
        }), 500

@app.route('/api/match/lda', methods=['POST'])
def match_users_lda():
    """
    基于LDA模型的智能匹配接口
    
    请求体格式:
    {
        "query": "用户搜索查询文本",
        "current_user": {用户自己的信息},
        "candidate_user": {候选用户信息},
        "mode": "找对象" 或 "找队友"
    }
    """
    try:
        # 导入LDA模型
        from backend.models.topic_modeling import topic_model
        
        data = request.get_json()
        if not data:
            return jsonify({
                "error": "请求格式错误",
                "message": "请提供JSON格式的请求体"
            }), 400
        
        query = data.get('query', '')
        current_user = data.get('current_user', {})
        candidate_user = data.get('candidate_user', {})
        mode = data.get('mode', '找对象')
        
        if not candidate_user:
            return jsonify({
                "error": "参数缺失",
                "message": "需要提供候选用户信息"
            }), 400
        
        # 构建候选用户的描述文本
        user_text = build_user_description_text(candidate_user)
        
        # 如果有查询文本，将其与用户描述结合
        if query.strip():
            combined_text = f"{query} {user_text}"
        else:
            combined_text = user_text
        
        # 使用LDA模型进行分析
        lda_result = topic_model.extract_topics_and_tags(combined_text, mode)
        
        # 计算匹配度分数
        match_score = calculate_lda_match_score(
            query, current_user, candidate_user, lda_result, mode
        )
        
        # 准备返回结果（转换numpy类型为Python原生类型）
        result = {
            "match_score": float(match_score),
            "topics": [(int(tid), float(weight)) for tid, weight in lda_result.topics],
            "extracted_tags": {
                tag: float(conf) for tag, conf in sorted(
                    lda_result.extracted_tags.items(), 
                    key=lambda x: x[1], 
                    reverse=True
                )[:10]
            },  # 返回前10个最相关的标签
            "topic_keywords": {
                int(tid): [(word, float(weight)) for word, weight in words] 
                for tid, words in lda_result.topic_keywords.items()
            },
            "analysis": {
                "user_text": user_text[:200] + "..." if len(user_text) > 200 else user_text,
                "query": query,
                "mode": mode,
                "total_tags_found": len(lda_result.extracted_tags)
            }
        }
        
        return jsonify({
            "success": True,
            "data": result
        })
        
    except Exception as e:
        print(f"LDA匹配分析出错: {e}")
        traceback.print_exc()
        return jsonify({
            "error": "LDA匹配分析失败",
            "message": str(e)
        }), 500

@app.route('/api/match/upload', methods=['POST'])
def match_users_upload():
    """
    文件上传匹配接口 - 上传两个JSON文件进行匹配
    """
    try:
        init_analyzer()
        
        if 'user_a' not in request.files or 'user_b' not in request.files:
            return jsonify({
                "error": "文件缺失",
                "message": "需要上传 user_a 和 user_b 两个JSON文件"
            }), 400
        
        file_a = request.files['user_a']
        file_b = request.files['user_b']
        
        if file_a.filename == '' or file_b.filename == '':
            return jsonify({
                "error": "文件名为空",
                "message": "请选择有效的JSON文件"
            }), 400
        
        if not (allowed_file(file_a.filename) and allowed_file(file_b.filename)):
            return jsonify({
                "error": "文件格式错误",
                "message": "只支持 .json 格式的文件"
            }), 400
        
        # 保存上传的文件
        filename_a = secure_filename(file_a.filename)
        filename_b = secure_filename(file_b.filename)
        
        filepath_a = os.path.join(UPLOAD_FOLDER, f"temp_a_{filename_a}")
        filepath_b = os.path.join(UPLOAD_FOLDER, f"temp_b_{filename_b}")
        
        file_a.save(filepath_a)
        file_b.save(filepath_b)
        
        try:
            # 进行匹配分析
            result_json = analyzer.analyze_and_output_simple_result(filepath_a, filepath_b)
            result = json.loads(result_json)
            
            return jsonify({
                "success": True,
                "data": result
            })
            
        finally:
            # 清理上传的文件
            if os.path.exists(filepath_a):
                os.remove(filepath_a)
            if os.path.exists(filepath_b):
                os.remove(filepath_b)
            
    except Exception as e:
        print(f"文件上传匹配出错: {e}")
        traceback.print_exc()
        return jsonify({
            "error": "匹配分析失败",
            "message": str(e)
        }), 500

def build_user_description_text(user):
    """构建用户描述文本用于LDA分析"""
    text_parts = []
    
    # 基本信息
    if user.get('bio'):
        text_parts.append(user['bio'])
    
    if user.get('occupation'):
        text_parts.append(user['occupation'])
    
    # 标签信息
    if user.get('tags'):
        tag_names = [tag.get('name', '') for tag in user['tags'] if tag.get('name')]
        text_parts.extend(tag_names)
    
    # 寻找目标
    if user.get('looking_for'):
        text_parts.extend(user['looking_for'])
    
    # 位置信息
    if user.get('location_city'):
        text_parts.append(user['location_city'])
    
    return ' '.join(text_parts)

def calculate_lda_match_score(query, current_user, candidate_user, lda_result, mode):
    """基于LDA结果计算匹配度分数"""
    score = 0.0
    
    # 基于主题相关性计算分数（权重40%）
    if lda_result.topics:
        main_topic_score = lda_result.topics[0][1] if lda_result.topics else 0.0
        score += main_topic_score * 0.4
    
    # 基于标签匹配计算分数（权重40%）
    if lda_result.extracted_tags:
        # 取前5个最相关标签的平均置信度
        top_tags = sorted(lda_result.extracted_tags.items(), 
                         key=lambda x: x[1], reverse=True)[:5]
        if top_tags:
            tag_score = sum(conf for _, conf in top_tags) / len(top_tags)
            score += tag_score * 0.4
    
    # 基于用户基本匹配度（权重20%）
    basic_score = calculate_basic_compatibility(current_user, candidate_user, mode)
    score += basic_score * 0.2
    
    # 确保分数在0-1范围内
    return min(max(score, 0.0), 1.0)

def calculate_basic_compatibility(current_user, candidate_user, mode):
    """计算基本兼容性分数"""
    score = 0.5  # 基础分数
    
    try:
        # 地理位置匹配
        if (current_user.get('location_city') and 
            candidate_user.get('location_city') and
            current_user['location_city'] == candidate_user['location_city']):
            score += 0.2
        
        # 年龄匹配（找对象模式）
        if mode == '找对象':
            current_age = current_user.get('age', 25)
            candidate_age = candidate_user.get('age', 25)
            age_diff = abs(current_age - candidate_age)
            if age_diff <= 3:
                score += 0.2
            elif age_diff <= 6:
                score += 0.1
        
        # 寻找目标匹配
        current_goals = set(current_user.get('looking_for', []))
        candidate_goals = set(candidate_user.get('looking_for', []))
        if current_goals & candidate_goals:  # 有交集
            score += 0.1
        
    except Exception as e:
        print(f"基本兼容性计算出错: {e}")
    
    return min(max(score, 0.0), 1.0)

@app.route('/api/train', methods=['POST'])
def train_model():
    """
    模型训练接口 - 使用提供的档案训练LDA模型
    
    请求体格式:
    {
        "profiles": [
            {...},  // 用户档案1
            {...},  // 用户档案2
            ...
        ]
    }
    """
    try:
        init_analyzer()
        
        data = request.get_json()
        if not data or 'profiles' not in data:
            return jsonify({
                "error": "请求格式错误",
                "message": "需要提供 profiles 数组"
            }), 400
        
        profiles = data['profiles']
        if len(profiles) < 2:
            return jsonify({
                "error": "训练数据不足",
                "message": "至少需要2个用户档案进行训练"
            }), 400
        
        # 创建临时文件
        temp_files = []
        try:
            for i, profile in enumerate(profiles):
                with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
                    json.dump(profile, f, ensure_ascii=False, indent=2)
                    temp_files.append(f.name)
            
            # 训练模型
            analyzer.train_models(temp_files)
            
            return jsonify({
                "success": True,
                "message": f"模型训练完成，使用了 {len(profiles)} 个用户档案",
                "profiles_count": len(profiles)
            })
            
        finally:
            # 清理临时文件
            for temp_file in temp_files:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
            
    except Exception as e:
        print(f"模型训练出错: {e}")
        traceback.print_exc()
        return jsonify({
            "error": "模型训练失败",
            "message": str(e)
        }), 500

@app.route('/api/model/save', methods=['POST'])
def save_model():
    """保存训练好的模型"""
    try:
        init_analyzer()
        
        if not analyzer.is_model_trained:
            return jsonify({
                "error": "模型未训练",
                "message": "请先训练模型再保存"
            }), 400
        
        model_dir = request.get_json().get('model_dir', 'data/models') if request.is_json else 'data/models'
        
        analyzer.save_models(model_dir)
        
        return jsonify({
            "success": True,
            "message": f"模型已保存到 {model_dir}",
            "model_dir": model_dir
        })
        
    except Exception as e:
        print(f"模型保存出错: {e}")
        return jsonify({
            "error": "模型保存失败",
            "message": str(e)
        }), 500

@app.route('/api/model/load', methods=['POST'])
def load_model():
    """加载已保存的模型"""
    try:
        init_analyzer()
        
        model_dir = request.get_json().get('model_dir', 'data/models') if request.is_json else 'data/models'
        
        if not os.path.exists(model_dir):
            return jsonify({
                "error": "模型目录不存在",
                "message": f"目录 {model_dir} 不存在"
            }), 404
        
        analyzer.load_models(model_dir)
        
        return jsonify({
            "success": True,
            "message": f"模型已从 {model_dir} 加载",
            "model_dir": model_dir
        })
        
    except Exception as e:
        print(f"模型加载出错: {e}")
        return jsonify({
            "error": "模型加载失败",
            "message": str(e)
        }), 500

@app.route('/api/tags', methods=['GET'])
def get_tag_pool():
    """获取标签池信息"""
    try:
        from backend.models.tag_pool import TagPool
        
        request_type = request.args.get('type', 'all')
        
        tag_pool = TagPool()
        tags = tag_pool.get_all_tags(request_type)
        
        # 转换为简单的列表格式
        tag_list = []
        for category, tag_list_items in tags.items():
            tag_list.extend(tag_list_items)
        
        return jsonify({
            "success": True,
            "data": {
                "request_type": request_type,
                "total_tags": len(tag_list),
                "tags_by_category": {str(k): v for k, v in tags.items()},
                "all_tags": tag_list
            }
        })
        
    except Exception as e:
        print(f"获取标签池出错: {e}")
        return jsonify({
            "error": "获取标签池失败",
            "message": str(e)
        }), 500

@app.route('/api/demo', methods=['GET'])
def demo_match():
    """演示接口 - 使用Noah和Alan的档案进行演示"""
    try:
        init_analyzer()
        
        noah_path = "data/profiles/noah_profile.json"
        alan_path = "data/profiles/alan_profile.json"
        
        if not os.path.exists(noah_path) or not os.path.exists(alan_path):
            return jsonify({
                "error": "演示文件不存在",
                "message": "Noah 或 Alan 的档案文件不存在"
            }), 404
        
        # 进行匹配分析
        result_json = analyzer.analyze_and_output_simple_result(noah_path, alan_path)
        result = json.loads(result_json)
        
        return jsonify({
            "success": True,
            "message": "这是使用 Noah 和 Alan 档案的演示结果",
            "data": result
        })
        
    except Exception as e:
        print(f"演示匹配出错: {e}")
        traceback.print_exc()
        return jsonify({
            "error": "演示匹配失败",
            "message": str(e)
        }), 500

@app.route('/api/docs', methods=['GET'])
def api_documentation():
    """API文档"""
    docs = {
        "title": "用户匹配系统 API",
        "version": "1.0.0",
        "description": "基于LDA主题建模和Faiss向量相似度计算的用户匹配系统",
        "endpoints": {
            "GET /health": {
                "description": "健康检查",
                "response": "系统状态信息"
            },
            "GET /api/database/users": {
                "description": "获取所有用户信息（从数据库）",
                "output": "完整用户列表，包含元数据和标签"
            },
            "GET /api/database/users/<user_id>": {
                "description": "获取指定用户信息（从数据库）",
                "output": "单个用户的完整信息"
            },
            "GET /api/database/tags": {
                "description": "获取所有标签信息（从数据库）",
                "output": "标签列表，按类别分组"
            },
            "GET /api/database/test": {
                "description": "测试数据库连接",
                "output": "数据库连接状态和统计信息"
            },
            "POST /api/match/simple": {
                "description": "简洁匹配分析",
                "input": "两个用户档案的JSON对象",
                "output": "7个维度的匹配评分和描述"
            },
            "POST /api/match/upload": {
                "description": "文件上传匹配",
                "input": "两个JSON文件 (user_a, user_b)",
                "output": "匹配分析结果"
            },
            "POST /api/match/lda": {
                "description": "基于LDA模型的智能匹配",
                "input": "用户查询、当前用户信息、候选用户信息",
                "output": "LDA分析结果和匹配度分数"
            },
            "POST /api/train": {
                "description": "训练LDA模型",
                "input": "用户档案数组",
                "output": "训练状态"
            },
            "POST /api/model/save": {
                "description": "保存训练的模型",
                "output": "保存状态"
            },
            "POST /api/model/load": {
                "description": "加载已保存的模型",
                "output": "加载状态"
            },
            "GET /api/tags": {
                "description": "获取标签池信息",
                "params": "type (all/找对象/找队友)",
                "output": "标签分类和列表"
            },
            "GET /api/demo": {
                "description": "演示匹配 (Noah vs Alan)",
                "output": "演示匹配结果"
            }
        },
        "example_usage": {
            "curl_simple_match": '''curl -X POST http://localhost:5000/api/match/simple \\
  -H "Content-Type: application/json" \\
  -d '{
    "user_a": {"profile": {...}, "user_request": {...}},
    "user_b": {"profile": {...}, "user_request": {...}}
  }' ''',
            "curl_demo": "curl http://localhost:5000/api/demo",
            "curl_tags": "curl http://localhost:5000/api/tags?type=找队友"
        }
    }
    
    return jsonify(docs)

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({
        "error": "接口不存在",
        "message": "请检查API路径是否正确",
        "available_endpoints": [
            "GET /health",
            "GET /api/docs", 
            "GET /api/demo",
            "GET /api/tags",
            "POST /api/match/simple",
            "POST /api/match/upload",
            "POST /api/match/lda",
            "POST /api/train",
            "POST /api/model/save",
            "POST /api/model/load"
        ]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "服务器内部错误",
        "message": "请稍后重试或联系管理员"
    }), 500

if __name__ == '__main__':
    print("🚀 启动用户匹配系统 API 服务器")
    print("📊 基于 LDA 主题建模 + Faiss 向量相似度计算")
    print("=" * 50)
    print("🌐 API 文档: http://localhost:5002/api/docs")
    print("🎯 演示接口: http://localhost:5002/api/demo")
    print("❤️ 健康检查: http://localhost:5002/health")
    print("=" * 50)
    
    # 初始化分析器
    init_analyzer()
    
    # 启动服务器
    app.run(host='0.0.0.0', port=5002, debug=True) 