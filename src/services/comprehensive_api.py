#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
综合匹配系统API服务器
包含用户认证、metadata建档、tag建模、用户匹配等完整功能
"""

import os
import json
import sys
import hashlib
import jwt
import datetime
from typing import Dict, List, Any, Optional
from flask import Flask, request, jsonify, g
from flask_cors import CORS
from functools import wraps
import traceback

# 添加项目根目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from supabase import create_client, Client
from src.algorithms.tag_compatibility_analyzer import EnhancedCompatibilityAnalyzer
from src.models.tag_pool import TagPool
from src.models.topic_modeling import LDATopicModel
from configs.config import ConfigManager

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": ["*"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# 配置
JWT_SECRET = os.getenv('JWT_SECRET', 'impromptu_secret_key_2024')
SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://anxbbsrnjgmotxzysqwf.supabase.co')
SUPABASE_KEY = os.getenv('SUPABASE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFueGJic3Juamdtb3R4enlzcXdmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTA0MDY0OTIsImV4cCI6MjA2NTk4MjQ5Mn0.a0t-pgH-Z2Fbs6JuMNWX8_kpqkQsBag3-COAUZVF6-0')

# 初始化 Supabase 客户端
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 全局组件
analyzer = None
tag_pool = None
topic_model = None

def init_components():
    """初始化系统组件"""
    global analyzer, tag_pool, topic_model
    
    try:
        config_manager = ConfigManager()
        analyzer = EnhancedCompatibilityAnalyzer(config_manager)
        tag_pool = TagPool()
        topic_model = LDATopicModel(config_manager.topic_config)
        print("✅ 系统组件初始化完成")
    except Exception as e:
        print(f"❌ 组件初始化失败: {e}")

# 认证装饰器
def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': '未提供认证token'}), 401
        
        try:
            # 移除 'Bearer ' 前缀
            if token.startswith('Bearer '):
                token = token[7:]
            
            # 解析JWT
            payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            g.current_user_id = payload['user_id']
            g.current_user_email = payload.get('email')
            return f(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token已过期'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': '无效的Token'}), 401
    
    return decorated_function

def hash_password(password: str) -> str:
    """密码哈希"""
    return hashlib.sha256(password.encode()).hexdigest()

def generate_jwt_token(user_id: str, email: str) -> str:
    """生成JWT token"""
    payload = {
        'user_id': user_id,
        'email': email,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')

# ==================== 用户认证API ====================

@app.route('/api/auth/register', methods=['POST'])
def register():
    """用户注册"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '请求体不能为空'}), 400
        
        required_fields = ['email', 'password', 'display_name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'缺少必需字段: {field}'}), 400
        
        email = data['email'].lower().strip()
        password = data['password']
        display_name = data['display_name'].strip()
        
        # 检查用户是否已存在
        existing_user = supabase.table('user_profile').select('user_id').eq('email', email).execute()
        if existing_user.data:
            return jsonify({'error': '邮箱已被注册'}), 409
        
        # 生成用户ID
        user_id = f"user_{int(datetime.datetime.now().timestamp())}"
        
        # 哈希密码
        password_hash = hash_password(password)
        
        # 创建用户档案
        user_profile = {
            'user_id': user_id,
            'email': email,
            'password_hash': password_hash,
            'display_name': display_name,
            'avatar_url': data.get('avatar_url'),
            'created_at': datetime.datetime.utcnow().isoformat(),
            'updated_at': datetime.datetime.utcnow().isoformat()
        }
        
        result = supabase.table('user_profile').insert(user_profile).execute()
        
        if result.data:
            # 生成JWT token
            token = generate_jwt_token(user_id, email)
            
            return jsonify({
                'success': True,
                'message': '注册成功',
                'data': {
                    'user_id': user_id,
                    'email': email,
                    'display_name': display_name,
                    'token': token
                }
            }), 201
        else:
            return jsonify({'error': '注册失败'}), 500
            
    except Exception as e:
        print(f"注册错误: {e}")
        traceback.print_exc()
        return jsonify({'error': '注册失败', 'message': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '请求体不能为空'}), 400
        
        email = data.get('email', '').lower().strip()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'error': '邮箱和密码不能为空'}), 400
        
        # 查找用户
        user_result = supabase.table('user_profile').select('*').eq('email', email).execute()
        
        if not user_result.data:
            return jsonify({'error': '用户不存在'}), 404
        
        user = user_result.data[0]
        
        # 验证密码
        password_hash = hash_password(password)
        if user['password_hash'] != password_hash:
            return jsonify({'error': '密码错误'}), 401
        
        # 暂时跳过 is_active 检查
        if False:  # user.get('is_active', True):
            return jsonify({'error': '账户已被禁用'}), 403
        
        # 生成JWT token
        token = generate_jwt_token(user['user_id'], user['email'])
        
        # 更新最后登录时间
        supabase.table('user_profile').update({
            'last_login_at': datetime.datetime.utcnow().isoformat()
        }).eq('user_id', user['user_id']).execute()
        
        return jsonify({
            'success': True,
            'message': '登录成功',
            'data': {
                'user_id': user['user_id'],
                'email': user['email'],
                'display_name': user['display_name'],
                'avatar_url': user.get('avatar_url'),
                'token': token
            }
        })
        
    except Exception as e:
        print(f"登录错误: {e}")
        traceback.print_exc()
        return jsonify({'error': '登录失败', 'message': str(e)}), 500

@app.route('/api/auth/me', methods=['GET'])
@auth_required
def get_current_user():
    """获取当前用户信息"""
    try:
        user_result = supabase.table('user_profile').select('*').eq('user_id', g.current_user_id).execute()
        
        if not user_result.data:
            return jsonify({'error': '用户不存在'}), 404
        
        user = user_result.data[0]
        
        # 移除敏感信息
        user.pop('password_hash', None)
        
        return jsonify({
            'success': True,
            'data': user
        })
        
    except Exception as e:
        print(f"获取用户信息错误: {e}")
        return jsonify({'error': '获取用户信息失败', 'message': str(e)}), 500

# ==================== 用户Metadata建档API ====================

@app.route('/api/profile/metadata', methods=['POST'])
@auth_required
def create_or_update_metadata():
    """创建或更新用户metadata"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '请求体不能为空'}), 400
        
        section_type = data.get('section_type')  # 如: 'profile', 'user_request'
        section_key = data.get('section_key')    # 如: 'personal', 'professional'
        content = data.get('content')            # metadata内容
        
        if not all([section_type, section_key, content]):
            return jsonify({'error': '缺少必需字段: section_type, section_key, content'}), 400
        
        # 检查是否已存在
        existing = supabase.table('user_metadata').select('id').eq('user_id', g.current_user_id).eq('section_type', section_type).eq('section_key', section_key).execute()
        
        metadata_entry = {
            'user_id': g.current_user_id,
            'section_type': section_type,
            'section_key': section_key,
            'content': json.dumps(content, ensure_ascii=False) if isinstance(content, dict) else content,
            'data_type': data.get('data_type', 'nested_object'),
            'display_order': data.get('display_order', 1),
            'metadata': json.dumps(data.get('metadata', {}), ensure_ascii=False),
            'updated_at': datetime.datetime.utcnow().isoformat()
        }
        
        if existing.data:
            # 更新
            result = supabase.table('user_metadata').update(metadata_entry).eq('id', existing.data[0]['id']).execute()
            message = 'Metadata更新成功'
        else:
            # 创建
            metadata_entry['created_at'] = datetime.datetime.utcnow().isoformat()
            result = supabase.table('user_metadata').insert(metadata_entry).execute()
            message = 'Metadata创建成功'
        
        return jsonify({
            'success': True,
            'message': message,
            'data': result.data[0] if result.data else None
        })
        
    except Exception as e:
        print(f"Metadata操作错误: {e}")
        traceback.print_exc()
        return jsonify({'error': 'Metadata操作失败', 'message': str(e)}), 500

@app.route('/api/profile/metadata', methods=['GET'])
@auth_required
def get_user_metadata():
    """获取用户的所有metadata"""
    try:
        result = supabase.table('user_metadata').select('*').eq('user_id', g.current_user_id).execute()
        
        # 按section_type和section_key组织数据
        organized_metadata = {}
        for item in result.data:
            section_type = item['section_type']
            section_key = item['section_key']
            
            if section_type not in organized_metadata:
                organized_metadata[section_type] = {}
            
            # 解析content
            content = item['content']
            if isinstance(content, str):
                try:
                    content = json.loads(content)
                except json.JSONDecodeError:
                    pass
            
            organized_metadata[section_type][section_key] = {
                'content': content,
                'data_type': item['data_type'],
                'display_order': item['display_order'],
                'created_at': item['created_at'],
                'updated_at': item['updated_at']
            }
        
        return jsonify({
            'success': True,
            'data': organized_metadata
        })
        
    except Exception as e:
        print(f"获取Metadata错误: {e}")
        return jsonify({'error': '获取Metadata失败', 'message': str(e)}), 500

@app.route('/api/profile/metadata/batch', methods=['POST'])
@auth_required
def batch_update_metadata():
    """批量更新用户metadata"""
    try:
        data = request.get_json()
        if not data or 'metadata_entries' not in data:
            return jsonify({'error': '请求体格式错误，需要metadata_entries'}), 400
        
        entries = data['metadata_entries']
        results = []
        errors = []
        
        for entry in entries:
            try:
                section_type = entry.get('section_type')
                section_key = entry.get('section_key')
                content = entry.get('content')
                
                if not all([section_type, section_key, content]):
                    errors.append(f"条目缺少必需字段: {entry}")
                    continue
                
                # 检查是否已存在
                existing = supabase.table('user_metadata').select('id').eq('user_id', g.current_user_id).eq('section_type', section_type).eq('section_key', section_key).execute()
                
                metadata_entry = {
                    'user_id': g.current_user_id,
                    'section_type': section_type,
                    'section_key': section_key,
                    'content': json.dumps(content, ensure_ascii=False) if isinstance(content, dict) else content,
                    'data_type': entry.get('data_type', 'nested_object'),
                    'display_order': entry.get('display_order', 1),
                    'metadata': json.dumps(entry.get('metadata', {}), ensure_ascii=False),
                    'updated_at': datetime.datetime.utcnow().isoformat()
                }
                
                if existing.data:
                    # 更新
                    result = supabase.table('user_metadata').update(metadata_entry).eq('id', existing.data[0]['id']).execute()
                else:
                    # 创建
                    metadata_entry['created_at'] = datetime.datetime.utcnow().isoformat()
                    result = supabase.table('user_metadata').insert(metadata_entry).execute()
                
                if result.data:
                    results.append(result.data[0])
                    
            except Exception as e:
                errors.append(f"处理条目失败: {entry} - {str(e)}")
        
        return jsonify({
            'success': len(results) > 0,
            'message': f'成功处理{len(results)}条记录' + (f'，{len(errors)}条失败' if errors else ''),
            'data': {
                'success_count': len(results),
                'error_count': len(errors),
                'results': results,
                'errors': errors
            }
        })
        
    except Exception as e:
        print(f"批量更新Metadata错误: {e}")
        traceback.print_exc()
        return jsonify({'error': '批量更新Metadata失败', 'message': str(e)}), 500

# ==================== Tag建模API ====================

@app.route('/api/tags/generate', methods=['POST'])
@auth_required
def generate_user_tags():
    """基于用户metadata生成tags"""
    try:
        init_components()
        
        data = request.get_json()
        request_type = data.get('request_type', '找队友')  # '找对象' 或 '找队友'
        
        # 获取用户的所有metadata
        metadata_result = supabase.table('user_metadata').select('*').eq('user_id', g.current_user_id).execute()
        
        if not metadata_result.data:
            return jsonify({'error': '用户metadata为空，请先完善个人信息'}), 400
        
        # 构建用户文本描述
        text_parts = []
        for item in metadata_result.data:
            content = item['content']
            if isinstance(content, str):
                try:
                    content = json.loads(content)
                except json.JSONDecodeError:
                    text_parts.append(content)
                    continue
            
            # 提取文本内容
            if isinstance(content, dict):
                for key, value in content.items():
                    if isinstance(value, str):
                        text_parts.append(value)
                    elif isinstance(value, list):
                        text_parts.extend([str(v) for v in value])
            elif isinstance(content, list):
                text_parts.extend([str(item) for item in content])
        
        user_text = ' '.join(text_parts)
        
        if not user_text.strip():
            return jsonify({'error': '无法从metadata中提取有效文本'}), 400
        
        # 使用主题建模生成tags
        topic_result = topic_model.extract_topics_and_tags(user_text, request_type)
        
        # 保存生成的tags到数据库
        saved_tags = []
        for tag_name, confidence in topic_result.extracted_tags.items():
            # 删除旧的同名tag
            supabase.table('user_tags').delete().eq('user_id', g.current_user_id).eq('tag_name', tag_name).execute()
            
            # 插入新tag
            tag_entry = {
                'user_id': g.current_user_id,
                'tag_name': tag_name,
                'tag_category': 'generated',
                'confidence_score': confidence,
                'tag_source': 'topic_modeling',
                'created_at': datetime.datetime.utcnow().isoformat()
            }
            
            result = supabase.table('user_tags').insert(tag_entry).execute()
            if result.data:
                saved_tags.append(result.data[0])
        
        return jsonify({
            'success': True,
            'message': f'成功生成{len(saved_tags)}个标签',
            'data': {
                'generated_tags': saved_tags,
                'topics': [(int(tid), float(weight)) for tid, weight in topic_result.topics],
                'user_text_length': len(user_text),
                'request_type': request_type
            }
        })
        
    except Exception as e:
        print(f"Tag生成错误: {e}")
        traceback.print_exc()
        return jsonify({'error': 'Tag生成失败', 'message': str(e)}), 500

@app.route('/api/tags/manual', methods=['POST'])
@auth_required
def add_manual_tags():
    """手动添加tags"""
    try:
        data = request.get_json()
        if not data or 'tags' not in data:
            return jsonify({'error': '请求体格式错误，需要tags字段'}), 400
        
        tags = data['tags']
        if not isinstance(tags, list):
            return jsonify({'error': 'tags必须是数组格式'}), 400
        
        saved_tags = []
        for tag_info in tags:
            if isinstance(tag_info, str):
                tag_name = tag_info
                tag_category = 'manual'
                confidence = 1.0
            elif isinstance(tag_info, dict):
                tag_name = tag_info.get('name')
                tag_category = tag_info.get('category', 'manual')
                confidence = float(tag_info.get('confidence', 1.0))
            else:
                continue
            
            if not tag_name:
                continue
            
            # 删除旧的同名tag
            supabase.table('user_tags').delete().eq('user_id', g.current_user_id).eq('tag_name', tag_name).execute()
            
            # 插入新tag
            tag_entry = {
                'user_id': g.current_user_id,
                'tag_name': tag_name,
                'tag_category': tag_category,
                'confidence_score': confidence,
                'tag_source': 'manual',
                'created_at': datetime.datetime.utcnow().isoformat()
            }
            
            result = supabase.table('user_tags').insert(tag_entry).execute()
            if result.data:
                saved_tags.append(result.data[0])
        
        return jsonify({
            'success': True,
            'message': f'成功添加{len(saved_tags)}个标签',
            'data': saved_tags
        })
        
    except Exception as e:
        print(f"手动添加Tag错误: {e}")
        return jsonify({'error': '添加Tag失败', 'message': str(e)}), 500

@app.route('/api/tags/user', methods=['GET'])
@auth_required
def get_user_tags():
    """获取用户的所有tags"""
    try:
        result = supabase.table('user_tags').select('*').eq('user_id', g.current_user_id).order('confidence_score', desc=True).execute()
        
        return jsonify({
            'success': True,
            'data': result.data,
            'total': len(result.data)
        })
        
    except Exception as e:
        print(f"获取用户Tags错误: {e}")
        return jsonify({'error': '获取Tags失败', 'message': str(e)}), 500

# ==================== 用户匹配API ====================

@app.route('/api/match/search', methods=['POST'])
@auth_required
def search_users():
    """根据描述和tag搜索匹配用户"""
    try:
        data = request.get_json()
        description = data.get('description', '')
        user_tags = data.get('tags', [])
        match_type = data.get('match_type', '找队友')  # '找对象' 或 '找队友'
        limit = int(data.get('limit', 10))
        
        # 获取所有用户（除了当前用户）
        users_result = supabase.table('user_profile').select('*').neq('user_id', g.current_user_id).execute()
        
        if not users_result.data:
            return jsonify({
                'success': True,
                'data': [],
                'message': '暂无其他用户'
            })
        
        matched_users = []
        
        for user in users_result.data:
            user_id = user['user_id']
            
            # 获取用户的metadata
            metadata_result = supabase.table('user_metadata').select('*').eq('user_id', user_id).execute()
            
            # 获取用户的tags
            tags_result = supabase.table('user_tags').select('*').eq('user_id', user_id).execute()
            
            # 计算匹配度
            match_score = calculate_match_score(
                description, user_tags, match_type,
                metadata_result.data, tags_result.data
            )
            
            if match_score > 0.3:  # 设置最低匹配阈值
                user_info = {
                    'user_id': user_id,
                    'display_name': user['display_name'],
                    'email': user['email'],
                    'avatar_url': user.get('avatar_url'),
                    'match_score': match_score,
                    'user_tags': [tag['tag_name'] for tag in tags_result.data],
                    'metadata_summary': extract_metadata_summary(metadata_result.data)
                }
                matched_users.append(user_info)
        
        # 按匹配度排序
        matched_users.sort(key=lambda x: x['match_score'], reverse=True)
        
        return jsonify({
            'success': True,
            'data': matched_users[:limit],
            'total': len(matched_users),
            'query': {
                'description': description,
                'tags': user_tags,
                'match_type': match_type
            }
        })
        
    except Exception as e:
        print(f"用户搜索错误: {e}")
        traceback.print_exc()
        return jsonify({'error': '用户搜索失败', 'message': str(e)}), 500

def calculate_match_score(description: str, user_tags: List[str], match_type: str,
                         target_metadata: List[Dict], target_tags: List[Dict]) -> float:
    """计算用户匹配度分数"""
    score = 0.0
    
    # 标签匹配度 (40%权重)
    if user_tags and target_tags:
        target_tag_names = [tag['tag_name'] for tag in target_tags]
        common_tags = set(user_tags) & set(target_tag_names)
        tag_score = len(common_tags) / max(len(user_tags), len(target_tag_names), 1)
        score += tag_score * 0.4
    
    # 描述匹配度 (30%权重)
    if description and target_metadata:
        target_text = extract_text_from_metadata(target_metadata)
        description_score = calculate_text_similarity(description, target_text)
        score += description_score * 0.3
    
    # 类型匹配度 (20%权重)
    type_score = 0.8 if match_type in extract_request_type_from_metadata(target_metadata) else 0.2
    score += type_score * 0.2
    
    # 活跃度加分 (10%权重)
    activity_score = 0.5 + (len(target_tags) * 0.1)  # 有更多标签的用户活跃度更高
    score += min(activity_score, 1.0) * 0.1
    
    return min(score, 1.0)

def extract_metadata_summary(metadata: List[Dict]) -> Dict:
    """提取metadata摘要"""
    summary = {}
    for item in metadata:
        section_type = item['section_type']
        if section_type not in summary:
            summary[section_type] = {}
        
        content = item['content']
        if isinstance(content, str):
            try:
                content = json.loads(content)
            except json.JSONDecodeError:
                summary[section_type][item['section_key']] = content
                continue
        
        summary[section_type][item['section_key']] = content
    
    return summary

def extract_text_from_metadata(metadata: List[Dict]) -> str:
    """从metadata中提取文本"""
    text_parts = []
    for item in metadata:
        content = item['content']
        if isinstance(content, str):
            try:
                content = json.loads(content)
            except json.JSONDecodeError:
                text_parts.append(content)
                continue
        
        if isinstance(content, dict):
            for key, value in content.items():
                if isinstance(value, str):
                    text_parts.append(value)
                elif isinstance(value, list):
                    text_parts.extend([str(v) for v in value])
    
    return ' '.join(text_parts)

def extract_request_type_from_metadata(metadata: List[Dict]) -> str:
    """从metadata中提取请求类型"""
    for item in metadata:
        if item['section_type'] == 'user_request':
            content = item['content']
            if isinstance(content, str):
                try:
                    content = json.loads(content)
                except json.JSONDecodeError:
                    continue
            
            if isinstance(content, dict):
                return content.get('request_type', '找队友')
    
    return '找队友'

def calculate_text_similarity(text1: str, text2: str) -> float:
    """简单的文本相似度计算"""
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = words1 & words2
    union = words1 | words2
    
    return len(intersection) / len(union) if union else 0.0

# ==================== 兼容性分析API ====================

@app.route('/api/match/analyze', methods=['POST'])
@auth_required
def analyze_compatibility():
    """分析两个用户的兼容性"""
    try:
        data = request.get_json()
        target_user_id = data.get('target_user_id')
        
        if not target_user_id:
            return jsonify({'error': '缺少target_user_id参数'}), 400
        
        # 获取两个用户的完整信息
        current_user_data = get_user_complete_data(g.current_user_id)
        target_user_data = get_user_complete_data(target_user_id)
        
        if not current_user_data or not target_user_data:
            return jsonify({'error': '用户数据不完整'}), 400
        
        # 进行兼容性分析
        compatibility_result = perform_compatibility_analysis(current_user_data, target_user_data)
        
        return jsonify({
            'success': True,
            'data': compatibility_result
        })
        
    except Exception as e:
        print(f"兼容性分析错误: {e}")
        traceback.print_exc()
        return jsonify({'error': '兼容性分析失败', 'message': str(e)}), 500

@app.route('/api/match/detailed', methods=['POST'])
@auth_required
def detailed_compatibility_analysis():
    """使用现有算法进行详细兼容性分析"""
    try:
        init_components()
        
        data = request.get_json()
        target_user_id = data.get('target_user_id')
        
        if not target_user_id:
            return jsonify({'error': '缺少target_user_id参数'}), 400
        
        # 创建临时用户档案文件用于分析
        current_profile_data = create_profile_from_metadata(g.current_user_id)
        target_profile_data = create_profile_from_metadata(target_user_id)
        
        if not current_profile_data or not target_profile_data:
            return jsonify({'error': '无法构建用户档案数据'}), 400
        
        # 使用现有的增强分析器
        import tempfile
        import os
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f1:
            json.dump(current_profile_data, f1, ensure_ascii=False, indent=2)
            temp_file_a = f1.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f2:
            json.dump(target_profile_data, f2, ensure_ascii=False, indent=2)
            temp_file_b = f2.name
        
        try:
            # 使用增强兼容性分析器
            if not analyzer.is_model_trained:
                # 如果模型未训练，尝试加载已有模型
                try:
                    analyzer.load_models('data/models')
                except:
                    # 如果无法加载，进行快速训练
                    analyzer.train_models([temp_file_a, temp_file_b])
            
            # 进行详细兼容性分析
            detailed_result = analyzer.enhanced_compatibility_analysis(temp_file_a, temp_file_b)
            
            # 生成简洁结果
            simple_result = analyzer.generate_simple_result(detailed_result)
            
            return jsonify({
                'success': True,
                'data': {
                    'simple_result': json.loads(simple_result.to_json()),
                    'detailed_result': {
                        'overall_score': detailed_result.vector_similarity_score * 10,
                        'profile_similarity': detailed_result.profile_similarity * 10,
                        'request_similarity': detailed_result.request_similarity * 10,
                        'mutual_tags': detailed_result.mutual_tags,
                        'complementary_tags': detailed_result.complementary_tags,
                        'explanation': detailed_result.vector_explanation,
                        'recommendation': detailed_result.overall_recommendation
                    }
                }
            })
            
        finally:
            # 清理临时文件
            os.unlink(temp_file_a)
            os.unlink(temp_file_b)
            
    except Exception as e:
        print(f"详细兼容性分析错误: {e}")
        traceback.print_exc()
        return jsonify({'error': '详细兼容性分析失败', 'message': str(e)}), 500

@app.route('/api/match/batch', methods=['POST'])
@auth_required
def batch_match_analysis():
    """批量匹配分析"""
    try:
        init_components()
        
        data = request.get_json()
        target_user_ids = data.get('target_user_ids', [])
        analysis_type = data.get('analysis_type', 'simple')  # 'simple' 或 'detailed'
        
        if not target_user_ids:
            return jsonify({'error': '缺少target_user_ids参数'}), 400
        
        results = []
        
        for target_user_id in target_user_ids:
            try:
                if analysis_type == 'detailed':
                    # 详细分析
                    current_profile_data = create_profile_from_metadata(g.current_user_id)
                    target_profile_data = create_profile_from_metadata(target_user_id)
                    
                    if current_profile_data and target_profile_data:
                        # 使用现有算法进行详细分析
                        compatibility_score = calculate_enhanced_compatibility(
                            current_profile_data, target_profile_data
                        )
                    else:
                        compatibility_score = 0.0
                else:
                    # 简单分析
                    current_user_data = get_user_complete_data(g.current_user_id)
                    target_user_data = get_user_complete_data(target_user_id)
                    
                    if current_user_data and target_user_data:
                        compatibility_result = perform_compatibility_analysis(current_user_data, target_user_data)
                        compatibility_score = compatibility_result['overall_score'] / 10
                    else:
                        compatibility_score = 0.0
                
                results.append({
                    'target_user_id': target_user_id,
                    'compatibility_score': compatibility_score,
                    'analysis_type': analysis_type
                })
                
            except Exception as e:
                print(f"分析用户 {target_user_id} 失败: {e}")
                results.append({
                    'target_user_id': target_user_id,
                    'compatibility_score': 0.0,
                    'error': str(e),
                    'analysis_type': analysis_type
                })
        
        # 按兼容性分数排序
        results.sort(key=lambda x: x['compatibility_score'], reverse=True)
        
        return jsonify({
            'success': True,
            'data': results,
            'total_analyzed': len(results),
            'analysis_type': analysis_type
        })
        
    except Exception as e:
        print(f"批量匹配分析错误: {e}")
        traceback.print_exc()
        return jsonify({'error': '批量匹配分析失败', 'message': str(e)}), 500

def get_user_complete_data(user_id: str) -> Optional[Dict]:
    """获取用户的完整数据"""
    try:
        # 基本信息
        profile_result = supabase.table('user_profile').select('*').eq('user_id', user_id).execute()
        if not profile_result.data:
            return None
        
        profile = profile_result.data[0]
        
        # Metadata
        metadata_result = supabase.table('user_metadata').select('*').eq('user_id', user_id).execute()
        
        # Tags
        tags_result = supabase.table('user_tags').select('*').eq('user_id', user_id).execute()
        
        return {
            'profile': profile,
            'metadata': metadata_result.data,
            'tags': tags_result.data
        }
        
    except Exception as e:
        print(f"获取用户完整数据错误: {e}")
        return None

def perform_compatibility_analysis(user_a_data: Dict, user_b_data: Dict) -> Dict:
    """执行兼容性分析"""
    # 简化的兼容性分析逻辑
    
    # 标签相似度
    tags_a = [tag['tag_name'] for tag in user_a_data['tags']]
    tags_b = [tag['tag_name'] for tag in user_b_data['tags']]
    
    common_tags = set(tags_a) & set(tags_b)
    all_tags = set(tags_a) | set(tags_b)
    tag_similarity = len(common_tags) / len(all_tags) if all_tags else 0
    
    # Metadata相似度
    text_a = extract_text_from_metadata(user_a_data['metadata'])
    text_b = extract_text_from_metadata(user_b_data['metadata'])
    text_similarity = calculate_text_similarity(text_a, text_b)
    
    # 综合评分
    overall_score = (tag_similarity * 0.6 + text_similarity * 0.4) * 10
    
    return {
        'user_a': user_a_data['profile']['display_name'],
        'user_b': user_b_data['profile']['display_name'],
        'overall_score': round(overall_score, 2),
        'tag_similarity': round(tag_similarity * 10, 2),
        'text_similarity': round(text_similarity * 10, 2),
        'common_tags': list(common_tags),
        'total_tags_a': len(tags_a),
        'total_tags_b': len(tags_b),
        'recommendation': generate_recommendation(overall_score)
    }

def generate_recommendation(score: float) -> str:
    """生成推荐建议"""
    if score >= 8:
        return "强烈推荐：高度匹配，建议主动联系"
    elif score >= 6:
        return "推荐：较好匹配，可以尝试交流"
    elif score >= 4:
        return "一般匹配：存在一定共同点，可以了解"
    else:
        return "匹配度较低：差异较大，需谨慎考虑"

def create_profile_from_metadata(user_id: str) -> Optional[Dict]:
    """从用户metadata创建档案数据，用于兼容现有算法"""
    try:
        # 获取用户基本信息
        profile_result = supabase.table('user_profile').select('*').eq('user_id', user_id).execute()
        if not profile_result.data:
            return None
        
        user_profile = profile_result.data[0]
        
        # 获取用户metadata
        metadata_result = supabase.table('user_metadata').select('*').eq('user_id', user_id).execute()
        
        # 构建档案数据结构
        profile_data = {
            'profile': {
                'name': {
                    'display_name': user_profile['display_name'],
                    'nickname': user_profile['display_name'],
                    'greeting': 'Hi there!'
                },
                'professional': {},
                'personal': {},
                'personality': {},
                'lifestyle': {}
            },
            'user_request': {},
            'metadata': {
                'profile_type': 'generated',
                'created_date': '2024',
                'tags': {}
            }
        }
        
        # 处理metadata
        for item in metadata_result.data:
            section_type = item['section_type']
            section_key = item['section_key']
            content = item['content']
            
            # 解析content
            if isinstance(content, str):
                try:
                    content = json.loads(content)
                except json.JSONDecodeError:
                    content = {'description': content}
            
            if section_type == 'profile':
                if section_key in profile_data['profile']:
                    profile_data['profile'][section_key].update(content)
                else:
                    profile_data['profile'][section_key] = content
            elif section_type == 'user_request':
                profile_data['user_request'].update(content)
        
        # 获取用户标签
        tags_result = supabase.table('user_tags').select('*').eq('user_id', user_id).execute()
        
        # 按类别组织标签
        for tag in tags_result.data:
            tag_name = tag['tag_name']
            tag_category = tag.get('tag_category', 'general')
            
            if tag_category not in profile_data['metadata']['tags']:
                profile_data['metadata']['tags'][tag_category] = []
            
            profile_data['metadata']['tags'][tag_category].append(tag_name)
        
        return profile_data
        
    except Exception as e:
        print(f"创建档案数据失败: {e}")
        return None

def calculate_enhanced_compatibility(profile_a: Dict, profile_b: Dict) -> float:
    """使用增强算法计算兼容性分数"""
    try:
        # 基于标签的相似度
        tags_a = set()
        tags_b = set()
        
        # 收集所有标签
        for category, tag_list in profile_a.get('metadata', {}).get('tags', {}).items():
            tags_a.update(tag_list)
        
        for category, tag_list in profile_b.get('metadata', {}).get('tags', {}).items():
            tags_b.update(tag_list)
        
        # 计算标签重叠度
        common_tags = tags_a & tags_b
        all_tags = tags_a | tags_b
        tag_similarity = len(common_tags) / len(all_tags) if all_tags else 0
        
        # 基于文本的相似度
        text_a = extract_profile_text(profile_a)
        text_b = extract_profile_text(profile_b)
        text_similarity = calculate_text_similarity(text_a, text_b)
        
        # 诉求匹配度
        request_a = profile_a.get('user_request', {})
        request_b = profile_b.get('user_request', {})
        
        request_similarity = 0.5  # 默认值
        if request_a.get('request_type') == request_b.get('request_type'):
            request_similarity = 0.8
            
            # 描述相似度
            desc_a = request_a.get('description', '')
            desc_b = request_b.get('description', '')
            if desc_a and desc_b:
                desc_sim = calculate_text_similarity(desc_a, desc_b)
                request_similarity = 0.8 + (desc_sim * 0.2)
        
        # 综合评分
        overall_score = (
            tag_similarity * 0.4 +
            text_similarity * 0.3 +
            request_similarity * 0.3
        )
        
        return min(overall_score, 1.0)
        
    except Exception as e:
        print(f"增强兼容性计算失败: {e}")
        return 0.0

def extract_profile_text(profile: Dict) -> str:
    """从档案中提取所有文本内容"""
    text_parts = []
    
    # 从profile部分提取文本
    profile_section = profile.get('profile', {})
    for section_name, section_data in profile_section.items():
        if section_name == 'name':
            continue
            
        if isinstance(section_data, dict):
            for key, value in section_data.items():
                if isinstance(value, str):
                    text_parts.append(value)
                elif isinstance(value, list):
                    text_parts.extend([str(v) for v in value])
        elif isinstance(section_data, list):
            text_parts.extend([str(item) for item in section_data])
        elif isinstance(section_data, str):
            text_parts.append(section_data)
    
    # 从user_request部分提取文本
    user_request = profile.get('user_request', {})
    for key, value in user_request.items():
        if isinstance(value, str):
            text_parts.append(value)
        elif isinstance(value, list):
            text_parts.extend([str(v) for v in value])
    
    return ' '.join(text_parts)

# ==================== 系统信息API ====================

@app.route('/api/system/health', methods=['GET'])
def health_check():
    """系统健康检查"""
    return jsonify({
        'status': 'healthy',
        'message': '综合匹配系统API运行正常',
        'version': '1.0.0',
        'timestamp': datetime.datetime.utcnow().isoformat()
    })

@app.route('/api/system/stats', methods=['GET'])
def system_stats():
    """系统统计信息"""
    try:
        # 用户统计
        users_count = supabase.table('user_profile').select('user_id', count='exact').execute().count
        
        # Tags统计
        tags_count = supabase.table('user_tags').select('id', count='exact').execute().count
        
        # Metadata统计
        metadata_count = supabase.table('user_metadata').select('id', count='exact').execute().count
        
        return jsonify({
            'success': True,
            'data': {
                'total_users': users_count,
                'total_tags': tags_count,
                'total_metadata_entries': metadata_count,
                'system_status': 'operational'
            }
        })
        
    except Exception as e:
        print(f"系统统计错误: {e}")
        return jsonify({'error': '获取系统统计失败', 'message': str(e)}), 500

# ==================== 错误处理 ====================

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({
        'error': 'API接口不存在',
        'message': '请检查URL路径是否正确'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': '服务器内部错误',
        'message': '请稍后重试或联系管理员'
    }), 500

if __name__ == '__main__':
    print("🚀 启动综合匹配系统API服务器")
    print("=" * 50)
    print("🔐 用户认证: /api/auth/*")
    print("📝 Metadata建档: /api/profile/*")
    print("🏷️  Tag建模: /api/tags/*") 
    print("🔍 用户匹配: /api/match/*")
    print("📊 系统信息: /api/system/*")
    print("=" * 50)
    
    # 初始化组件
    init_components()
    
    # 启动服务器
    app.run(host='0.0.0.0', port=5003, debug=True) 