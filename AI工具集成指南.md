# TODO应用 AI工具集成指南

## 🤖 AI工具接口说明

本项目提供两种AI工具调用方式：
1. **命令行接口 (CLI)** - 适合脚本调用
2. **REST API接口** - 适合OpenCLAW、ClaudeCode等工具

---

## 📟 命令行接口 (CLI)

### 安装依赖
```bash
pip install click requests
```

### 快速开始

#### 1. 登录
```bash
python cli.py login --username admin --password password123
```

#### 2. 添加任务
```bash
python cli.py add --title "完成项目报告" --priority HIGH --due-date 2024-12-31
```

#### 3. 查看任务列表
```bash
python cli.py list --status active --limit 10
```

#### 4. 完成任务
```bash
python cli.py complete 1
```

#### 5. 搜索任务
```bash
python cli.py search --query "报告" --priority HIGH
```

### 完整命令列表

| 命令 | 说明 | 示例 |
|------|------|------|
| `login` | 用户登录 | `python cli.py login --username admin` |
| `add` | 添加任务 | `python cli.py add --title "任务"` |
| `list` | 列出任务 | `python cli.py list --status active` |
| `complete` | 完成任务 | `python cli.py complete 1` |
| `delete` | 删除任务 | `python cli.py delete 1` |
| `search` | 搜索任务 | `python cli.py search --query "关键词"` |
| `show` | 显示详情 | `python cli.py show 1` |
| `stats` | 统计信息 | `python cli.py stats` |

---

## 🔌 REST API接口

### 启动AI接口服务
```bash
python ai_interface.py
# 服务运行在 http://localhost:8001
```

### API端点

#### 认证
```http
POST /ai/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "password123"
}

Response:
{
  "access_token": "ai_token_admin",
  "token_type": "bearer",
  "expires_in": 86400
}
```

#### 获取任务列表
```http
GET /ai/todos
Authorization: Bearer {token}

Response:
{
  "success": true,
  "data": [...],
  "count": 10
}
```

#### 创建任务
```http
POST /ai/todos
Authorization: Bearer {token}
Content-Type: application/json

{
  "title": "完成项目报告",
  "description": "需要包含Q4数据",
  "priority": "HIGH",
  "category": "工作",
  "due_date": "2024-12-31"
}
```

#### 更新任务
```http
PUT /ai/todos/{todo_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "completed": true,
  "priority": "MEDIUM"
}
```

#### 删除任务
```http
DELETE /ai/todos/{todo_id}
Authorization: Bearer {token}
```

#### 搜索任务
```http
POST /ai/todos/search
Authorization: Bearer {token}
Content-Type: application/json

{
  "query": "项目报告",
  "priority": "HIGH"
}
```

#### 获取统计
```http
GET /ai/stats
Authorization: Bearer {token}

Response:
{
  "success": true,
  "data": {
    "total": 50,
    "completed": 30,
    "pending": 20,
    "completion_rate": 60.0
  }
}
```

---

## 🤖 AI工具集成示例

### OpenCLAW集成
```yaml
tools:
  todo:
    type: http
    base_url: http://localhost:8001/ai
    auth:
      type: bearer
      token: ${TODO_TOKEN}
    
    commands:
      list_todos:
        method: GET
        path: /todos
      
      create_todo:
        method: POST
        path: /todos
        body:
          title: "{{title}}"
          priority: "{{priority}}"
      
      complete_todo:
        method: PUT
        path: /todos/{{id}}
        body:
          completed: true
```

### ClaudeCode集成
```javascript
// claude_config.json
{
  "tools": {
    "todo_system": {
      "endpoint": "http://localhost:8001/ai",
      "auth_header": "Authorization",
      "auth_value": "Bearer YOUR_TOKEN_HERE",
      "operations": {
        "create": "POST /todos",
        "read": "GET /todos/{id}",
        "update": "PUT /todos/{id}",
        "delete": "DELETE /todos/{id}",
        "search": "POST /todos/search"
      }
    }
  }
}
```

### 使用示例对话
```
User: 帮我创建一个高优先级的任务，明天要完成项目报告

AI: 好的，我来为您创建任务。
[调用: POST /ai/todos]
{
  "title": "完成项目报告",
  "priority": "HIGH",
  "due_date": "2024-12-20"
}
✓ 任务已创建 #1

User: 显示我所有未完成的任务

AI: 让我查询一下。
[调用: GET /ai/todos?status=active]
找到以下任务:
⬜ 🔴 #1 完成项目报告
⬜ 🟡 #2 准备会议材料
```

---

## 🔧 配置说明

### 环境变量
```bash
# .env
TODO_API_URL=http://localhost:8001/ai
TODO_AUTH_TOKEN=your_token_here
TODO_DEFAULT_PRIORITY=MEDIUM
TODO_DEFAULT_CATEGORY=默认
```

### 配置文件
```json
// todo_config.json
{
  "api": {
    "base_url": "http://localhost:8001/ai",
    "timeout": 30,
    "retry_attempts": 3
  },
  "auth": {
    "token_file": "~/.todo_app_token",
    "auto_refresh": true
  },
  "defaults": {
    "priority": "MEDIUM",
    "category": "默认",
    "reminder_enabled": false
  }
}
```

---

## 📊 响应格式规范

所有API响应遵循统一格式：
```json
{
  "success": true/false,
  "data": {...},
  "message": "操作结果说明",
  "timestamp": "2024-12-19T10:30:00Z"
}
```

错误响应：
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "详细错误信息"
  }
}
```

---

## 🎯 最佳实践

1. **错误处理**: AI工具应检查`success`字段
2. **令牌管理**: 定期刷新访问令牌
3. **速率限制**: 建议每秒不超过10次请求
4. **数据缓存**: 本地缓存常用数据减少API调用
5. **日志记录**: 记录所有API调用便于调试

---

## 🚀 快速测试

```bash
# 1. 启动服务
python ai_interface.py

# 2. 获取令牌
curl -X POST http://localhost:8001/ai/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password123"}'

# 3. 创建任务
curl -X POST http://localhost:8001/ai/todos \
  -H "Authorization: Bearer ai_token_admin" \
  -H "Content-Type: application/json" \
  -d '{"title":"测试任务","priority":"HIGH"}'

# 4. 查看任务
curl http://localhost:8001/ai/todos \
  -H "Authorization: Bearer ai_token_admin"
```

现在您的TODO系统已经完全支持AI工具调用了！🎉