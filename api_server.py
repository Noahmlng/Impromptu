#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
用户匹配系统 API 服务器

提供 RESTful API 接口用于用户匹配分析
基于 LDA 主题建模 + Faiss 向量相似度计算
"""

import os
import json
import tempfile
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
from tag_compatibility_analyzer import EnhancedCompatibilityAnalyzer
import traceback

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 全局分析器实例
analyzer = None
UPLOAD_FOLDER = 'temp_uploads'
ALLOWED_EXTENSIONS = {'json'}

# 确保上传目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """检查文件扩展名是否被允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def init_analyzer():
    """初始化分析器"""
    global analyzer
    if analyzer is None:
        analyzer = EnhancedCompatibilityAnalyzer()
        print("✅ 分析器初始化完成")

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        "status": "healthy",
        "message": "用户匹配系统 API 运行正常",
        "version": "1.0.0"
    })

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
        from models.tag_pool import TagPool
        
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
    print("🌐 API 文档: http://localhost:5000/api/docs")
    print("🎯 演示接口: http://localhost:5000/api/demo")
    print("❤️ 健康检查: http://localhost:5000/health")
    print("=" * 50)
    
    # 初始化分析器
    init_analyzer()
    
    # 启动服务器
    app.run(host='0.0.0.0', port=5000, debug=True) 