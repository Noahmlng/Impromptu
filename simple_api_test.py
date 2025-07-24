#!/usr/bin/env python3
# Simple API test server

from flask import Flask, jsonify
from flask_cors import CORS
from supabase import create_client

app = Flask(__name__)
CORS(app)

# Supabase 配置
SUPABASE_URL = 'https://anxbbsrnjgmotxzysqwf.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFueGJic3Juamdtb3R4enlzcXdmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTA0MDY0OTIsImV4cCI6MjA2NTk4MjQ5Mn0.a0t-pgH-Z2Fbs6JuMNWX8_kpqkQsBag3-COAUZVF6-0'

# 初始化 Supabase 客户端
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "message": "Simple API is running"})

@app.route('/api/database/test', methods=['GET'])
def test_db():
    try:
        # 简单测试数据库连接
        result = supabase.table('profiles').select('count', count='exact').execute()
        return jsonify({
            "success": True,
            "message": "Database connection OK",
            "profiles_count": result.count if hasattr(result, 'count') else 0
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/database/users', methods=['GET'])
def get_users():
    try:
        # 获取所有用户
        profiles = supabase.table('profiles').select('id, username').execute()
        metadata = supabase.table('user_metadata').select('*').execute()
        
        # 简单合并数据
        users = []
        metadata_dict = {m['id']: m for m in metadata.data} if metadata.data else {}
        
        for profile in profiles.data or []:
            user_meta = metadata_dict.get(profile['id'], {})
            users.append({
                'id': profile['id'],
                'username': profile['username'],
                'age': user_meta.get('age'),
                'gender': user_meta.get('gender'),
                'location_city': user_meta.get('location_city'),
                'bio': user_meta.get('bio'),
                'occupation': user_meta.get('occupation'),
                'looking_for': user_meta.get('looking_for', [])
            })
        
        return jsonify({
            "success": True,
            "data": users,
            "total": len(users)
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    print("🚀 Starting Simple API Test Server on port 5002")
    app.run(host='0.0.0.0', port=5002, debug=True) 