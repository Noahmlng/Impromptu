# 综合匹配系统 API 文档

## 概述

综合匹配系统提供用户认证、metadata建档、标签建模和用户匹配等完整功能的REST API接口。所有API都支持JSON格式的请求和响应。

**基础URL**: `http://localhost:5003`  
**API版本**: `v1.0.0`  
**认证方式**: JWT Bearer Token

## 目录

1. [用户认证 API](#用户认证-api)
2. [用户 Metadata 建档 API](#用户-metadata-建档-api)
3. [标签建模 API](#标签建模-api)
4. [用户匹配 API](#用户匹配-api)
5. [系统信息 API](#系统信息-api)
6. [数据模型](#数据模型)
7. [错误处理](#错误处理)
8. [使用示例](#使用示例)

---

## 用户认证 API

### 1. 用户注册

**POST** `/api/auth/register`

创建新用户账户。

**请求体**:
```json
{
  "email": "user@example.com",
  "password": "password123",
  "display_name": "张三",
  "avatar_url": "https://example.com/avatar.jpg" // 可选
}
```

**响应**:
```json
{
  "success": true,
  "message": "注册成功",
  "data": {
    "user_id": "user_1704000000",
    "email": "user@example.com",
    "display_name": "张三",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

**状态码**:
- `201`: 注册成功
- `400`: 请求参数错误
- `409`: 邮箱已被注册
- `500`: 服务器错误

### 2. 用户登录

**POST** `/api/auth/login`

用户登录获取访问令牌。

**请求体**:
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**响应**:
```json
{
  "success": true,
  "message": "登录成功",
  "data": {
    "user_id": "user_1704000000",
    "email": "user@example.com",
    "display_name": "张三",
    "avatar_url": "https://example.com/avatar.jpg",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

**状态码**:
- `200`: 登录成功
- `400`: 请求参数错误
- `401`: 密码错误
- `403`: 账户被禁用
- `404`: 用户不存在

### 3. 获取当前用户信息

**GET** `/api/auth/me`

获取当前登录用户的详细信息。

**请求头**:
```
Authorization: Bearer <token>
```

**响应**:
```json
{
  "success": true,
  "data": {
    "user_id": "user_1704000000",
    "email": "user@example.com",
    "display_name": "张三",
    "avatar_url": "https://example.com/avatar.jpg",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "last_login_at": "2024-01-01T12:00:00Z",
    "is_active": true
  }
}
```

---

## 用户 Metadata 建档 API

### 1. 创建/更新 Metadata

**POST** `/api/profile/metadata`

创建或更新用户的metadata信息。

**请求头**:
```
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "section_type": "profile",
  "section_key": "personal",
  "content": {
    "age_range": "25-30岁",
    "location": "深圳",
    "living_situation": "独居",
    "pets": "无宠物"
  },
  "data_type": "nested_object",
  "display_order": 1
}
```

**参数说明**:
- `section_type`: 数据分类 (如: 'profile', 'user_request')
- `section_key`: 具体子分类 (如: 'personal', 'professional')
- `content`: 具体内容，可以是对象或字符串
- `data_type`: 数据类型 (默认: 'nested_object')
- `display_order`: 显示顺序 (默认: 1)

**响应**:
```json
{
  "success": true,
  "message": "Metadata创建成功",
  "data": {
    "id": 123,
    "user_id": "user_1704000000",
    "section_type": "profile",
    "section_key": "personal",
    "content": "{\"age_range\":\"25-30岁\",\"location\":\"深圳\"}",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

### 2. 获取用户 Metadata

**GET** `/api/profile/metadata`

获取当前用户的所有metadata信息。

**请求头**:
```
Authorization: Bearer <token>
```

**响应**:
```json
{
  "success": true,
  "data": {
    "profile": {
      "personal": {
        "content": {
          "age_range": "25-30岁",
          "location": "深圳",
          "living_situation": "独居"
        },
        "data_type": "nested_object",
        "display_order": 1,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
      },
      "professional": {
        "content": {
          "current_role": "后端开发工程师",
          "industry": "互联网/技术"
        },
        "data_type": "nested_object",
        "display_order": 2,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
      }
    },
    "user_request": {
      "main": {
        "content": {
          "request_type": "找队友",
          "description": "寻找技术合作伙伴"
        },
        "data_type": "nested_object",
        "display_order": 1,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
      }
    }
  }
}
```

### 3. 批量更新 Metadata

**POST** `/api/profile/metadata/batch`

批量创建或更新多个metadata条目。

**请求头**:
```
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "metadata_entries": [
    {
      "section_type": "profile",
      "section_key": "personal",
      "content": {
        "age_range": "25-30岁",
        "location": "深圳"
      }
    },
    {
      "section_type": "profile", 
      "section_key": "professional",
      "content": {
        "current_role": "后端开发工程师",
        "industry": "互联网/技术"
      }
    }
  ]
}
```

**响应**:
```json
{
  "success": true,
  "message": "成功处理2条记录",
  "data": {
    "success_count": 2,
    "error_count": 0,
    "results": [...],
    "errors": []
  }
}
```

---

## 标签建模 API

### 1. 基于 Metadata 生成标签

**POST** `/api/tags/generate`

使用AI算法基于用户的metadata自动生成标签。

**请求头**:
```
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "request_type": "找队友"  // 或 "找对象"
}
```

**响应**:
```json
{
  "success": true,
  "message": "成功生成15个标签",
  "data": {
    "generated_tags": [
      {
        "id": 1,
        "user_id": "user_1704000000",
        "tag_name": "后端开发",
        "tag_category": "generated",
        "confidence_score": 0.95,
        "tag_source": "topic_modeling",
        "created_at": "2024-01-01T00:00:00Z"
      }
    ],
    "topics": [
      [1, 0.3],
      [5, 0.25],
      [8, 0.2]
    ],
    "user_text_length": 1250,
    "request_type": "找队友"
  }
}
```

### 2. 手动添加标签

**POST** `/api/tags/manual`

手动为用户添加标签。

**请求头**:
```
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "tags": [
    "Python开发",
    "创业经验",
    {
      "name": "产品设计",
      "category": "skill",
      "confidence": 0.8
    }
  ]
}
```

**响应**:
```json
{
  "success": true,
  "message": "成功添加3个标签",
  "data": [
    {
      "id": 2,
      "user_id": "user_1704000000", 
      "tag_name": "Python开发",
      "tag_category": "manual",
      "confidence_score": 1.0,
      "tag_source": "manual",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### 3. 获取用户标签

**GET** `/api/tags/user`

获取用户的所有标签。

**请求头**:
```
Authorization: Bearer <token>
```

**响应**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "user_id": "user_1704000000",
      "tag_name": "后端开发", 
      "tag_category": "generated",
      "confidence_score": 0.95,
      "tag_source": "topic_modeling",
      "created_at": "2024-01-01T00:00:00Z",
      "status": active
    }
  ],
  "total": 15
}
```

---

## 用户匹配 API

### 1. 搜索匹配用户

**POST** `/api/match/search`

根据描述和标签搜索匹配的用户。

**请求头**:
```
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "description": "寻找一起做产品的技术合伙人",
  "tags": ["Python开发", "创业经验", "产品思维"],
  "match_type": "找队友",
  "limit": 10
}
```

**响应**:
```json
{
  "success": true,
  "data": [
    {
      "user_id": "user_1704000001",
      "display_name": "李四",
      "email": "lisi@example.com",
      "avatar_url": "https://example.com/avatar2.jpg",
      "match_score": 0.85,
      "user_tags": ["Python开发", "产品设计", "创业经验"],
      "metadata_summary": {
        "profile": {
          "personal": {
            "age_range": "28-32岁",
            "location": "深圳"
          },
          "professional": {
            "current_role": "产品经理",
            "industry": "互联网/技术"
          }
        }
      }
    }
  ],
  "total": 5,
  "query": {
    "description": "寻找一起做产品的技术合伙人",
    "tags": ["Python开发", "创业经验", "产品思维"],
    "match_type": "找队友"
  }
}
```

### 2. 兼容性分析

**POST** `/api/match/analyze`

分析当前用户与指定用户的兼容性。

**请求头**:
```
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "target_user_id": "user_1704000001"
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "user_a": "张三",
    "user_b": "李四", 
    "overall_score": 8.2,
    "tag_similarity": 7.5,
    "text_similarity": 8.8,
    "common_tags": ["Python开发", "创业经验"],
    "total_tags_a": 12,
    "total_tags_b": 10,
    "recommendation": "强烈推荐：高度匹配，建议主动联系"
  }
}
```

---

## 系统信息 API

### 1. 健康检查

**GET** `/api/system/health`

检查系统运行状态。

**响应**:
```json
{
  "status": "healthy",
  "message": "综合匹配系统API运行正常",
  "version": "1.0.0", 
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### 2. 系统统计

**GET** `/api/system/stats`

获取系统统计信息。

**响应**:
```json
{
  "success": true,
  "data": {
    "total_users": 42,
    "total_tags": 1250,
    "total_metadata_entries": 168,
    "system_status": "operational"
  }
}
```

---

## 数据模型

### 用户档案 (User Profile)
```json
{
  "user_id": "string",
  "email": "string",
  "display_name": "string", 
  "avatar_url": "string",
  "created_at": "datetime",
  "updated_at": "datetime",
  "last_login_at": "datetime",
  "is_active": "boolean"
}
```

### 用户元数据 (User Metadata)
```json
{
  "id": "integer",
  "user_id": "string",
  "section_type": "string",    // 'profile', 'user_request'
  "section_key": "string",     // 'personal', 'professional'
  "content": "json_string",     // 实际内容
  "data_type": "string",       // 数据类型
  "display_order": "integer",  // 显示顺序
  "is_active": "boolean",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### 用户标签 (User Tags)
```json
{
  "id": "integer",
  "user_id": "string",
  "tag_name": "string",
  "tag_category": "string",      // 'generated', 'manual'
  "confidence_score": "float",   // 0.0-1.0
  "tag_source": "string",        // 'topic_modeling', 'manual'
  "created_at": "datetime",
  "is_active": "boolean"
}
```

---

## 错误处理

### 标准错误响应格式

```json
{
  "error": "错误类型",
  "message": "详细错误信息"
}
```

### 常见错误码

| 状态码 | 错误类型 | 说明 |
|--------|----------|------|
| 400 | Bad Request | 请求参数错误 |
| 401 | Unauthorized | 未提供认证token或token无效 |
| 403 | Forbidden | 权限不足 |
| 404 | Not Found | 资源不存在 |
| 409 | Conflict | 资源冲突（如邮箱已存在） |
| 500 | Internal Server Error | 服务器内部错误 |

---

## 使用示例

### 完整用户流程示例

#### 1. 用户注册

```bash
curl -X POST http://localhost:5003/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "zhang@example.com",
    "password": "password123",
    "display_name": "张三"
  }'
```

#### 2. 用户登录

```bash
curl -X POST http://localhost:5003/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "zhang@example.com", 
    "password": "password123"
  }'
```

#### 3. 创建用户 Metadata

```bash
curl -X POST http://localhost:5003/api/profile/metadata \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "section_type": "profile",
    "section_key": "personal", 
    "content": {
      "age_range": "25-30岁",
      "location": "深圳",
      "living_situation": "独居"
    }
  }'
```

#### 4. 生成标签

```bash
curl -X POST http://localhost:5003/api/tags/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "request_type": "找队友"
  }'
```

#### 5. 搜索匹配用户

```bash
curl -X POST http://localhost:5003/api/match/search \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "description": "寻找技术合作伙伴",
    "tags": ["Python开发", "创业经验"],
    "match_type": "找队友",
    "limit": 5
  }'
```

### Python 客户端示例

```python
import requests
import json

class MatchingAPIClient:
    def __init__(self, base_url="http://localhost:5003"):
        self.base_url = base_url
        self.token = None
    
    def register(self, email, password, display_name):
        """用户注册"""
        response = requests.post(f"{self.base_url}/api/auth/register", json={
            "email": email,
            "password": password,
            "display_name": display_name
        })
        if response.status_code == 201:
            data = response.json()
            self.token = data['data']['token']
            return data
        return response.json()
    
    def login(self, email, password):
        """用户登录"""
        response = requests.post(f"{self.base_url}/api/auth/login", json={
            "email": email,
            "password": password
        })
        if response.status_code == 200:
            data = response.json()
            self.token = data['data']['token']
            return data
        return response.json()
    
    def headers(self):
        """获取认证头"""
        return {"Authorization": f"Bearer {self.token}"}
    
    def create_metadata(self, section_type, section_key, content):
        """创建metadata"""
        response = requests.post(f"{self.base_url}/api/profile/metadata",
            headers=self.headers(),
            json={
                "section_type": section_type,
                "section_key": section_key,
                "content": content
            }
        )
        return response.json()
    
    def generate_tags(self, request_type="找队友"):
        """生成标签"""
        response = requests.post(f"{self.base_url}/api/tags/generate",
            headers=self.headers(),
            json={"request_type": request_type}
        )
        return response.json()
    
    def search_users(self, description, tags, match_type="找队友", limit=10):
        """搜索用户"""
        response = requests.post(f"{self.base_url}/api/match/search",
            headers=self.headers(),
            json={
                "description": description,
                "tags": tags,
                "match_type": match_type,
                "limit": limit
            }
        )
        return response.json()

# 使用示例
client = MatchingAPIClient()

# 注册用户
result = client.register("test@example.com", "password123", "测试用户")
print("注册结果:", result)

# 创建metadata
client.create_metadata("profile", "personal", {
    "age_range": "25-30岁",
    "location": "深圳"
})

# 生成标签
tags_result = client.generate_tags("找队友")
print("生成标签:", tags_result)

# 搜索用户
search_result = client.search_users(
    "寻找技术合作伙伴", 
    ["Python开发", "创业经验"],
    "找队友"
)
print("搜索结果:", search_result)
```

---

## 部署说明

### 环境要求

- Python 3.8+
- Flask 2.0+
- Supabase
- JWT 库

### 启动服务

```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务器
python src/services/comprehensive_api.py

# 服务器将运行在 http://localhost:5003
```

### 环境变量

创建 `.env` 文件：

```bash
JWT_SECRET=your_jwt_secret_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
```

---

## 版本更新记录

### v1.0.0 (2024-01-01)
- 初始版本发布
- 支持用户认证、metadata建档、标签建模、用户匹配
- 完整的JWT认证机制
- RESTful API设计

---

**联系方式**: 如有问题或建议，请联系开发团队。 