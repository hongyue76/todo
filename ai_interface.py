#!/usr/bin/env python3
"""
TODO应用 AI工具接口
支持OpenCLAW、ClaudeCode等AI工具调用
"""

from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import json

app = FastAPI(
    title="TODO AI Interface",
    description="AI工具调用的TODO系统接口",
    version="1.0.0"
)

# 模拟数据库（实际应该连接真实数据库）
todos_db = {}
users_db = {"admin": "password123"}

class TodoCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str = "MEDIUM"
    category: str = "默认"
    due_date: Optional[str] = None

class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
    priority: Optional[str] = None
    category: Optional[str] = None
    parent_id: Optional[int] = None

@app.get("/ai/auth/login")
async def ai_login(username: str, password: str):
    """AI工具登录接口"""
    if username in users_db and users_db[username] == password:
        return {
            "access_token": f"ai_token_{username}",
            "token_type": "bearer",
            "expires_in": 86400
        }
    raise HTTPException(status_code=401, detail="用户名或密码错误")

@app.get("/ai/todos")
async def ai_list_todos(authorization: Optional[str] = Header(None)):
    """获取任务列表 - AI工具专用"""
    todos_list = list(todos_db.values())
    return {
        "success": True,
        "data": todos_list,
        "count": len(todos_list)
    }

@app.post("/ai/todos")
async def ai_create_todo(todo: TodoCreate, authorization: Optional[str] = Header(None)):
    """创建任务 - AI工具专用"""
    todo_id = len(todos_db) + 1
    todo_data = {
        "id": todo_id,
        **todo.dict(),
        "completed": False,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    todos_db[todo_id] = todo_data
    
    return {
        "success": True,
        "data": todo_data,
        "message": f"任务已创建: #{todo_id}"
    }

@app.get("/ai/todos/{todo_id}")
async def ai_get_todo(todo_id: int, authorization: Optional[str] = Header(None)):
    """获取任务详情 - AI工具专用"""
    if todo_id not in todos_db:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    return {
        "success": True,
        "data": todos_db[todo_id]
    }

@app.put("/ai/todos/{todo_id}")
async def ai_update_todo(todo_id: int, todo_update: TodoUpdate, authorization: Optional[str] = Header(None)):
    """更新任务 - AI工具专用"""
    if todo_id not in todos_db:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    todo = todos_db[todo_id]
    update_data = todo_update.dict(exclude_unset=True)
    
    for key, value in update_data.items():
        if value is not None:
            todo[key] = value
    
    todo["updated_at"] = datetime.utcnow().isoformat()
    
    return {
        "success": True,
        "data": todo,
        "message": f"任务 #{todo_id} 已更新"
    }

@app.delete("/ai/todos/{todo_id}")
async def ai_delete_todo(todo_id: int, authorization: Optional[str] = Header(None)):
    """删除任务 - AI工具专用"""
    if todo_id not in todos_db:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    del todos_db[todo_id]
    
    return {
        "success": True,
        "message": f"任务 #{todo_id} 已删除"
    }

@app.post("/ai/todos/search")
async def ai_search_todos(query: str, priority: Optional[str] = None, authorization: Optional[str] = Header(None)):
    """搜索任务 - AI工具专用"""
    results = []
    
    for todo in todos_db.values():
        match = False
        
        # 文本搜索
        if query and (query.lower() in todo["title"].lower() or 
                     query.lower() in todo.get("description", "").lower()):
            match = True
        
        # 优先级筛选
        if priority and todo["priority"] != priority:
            match = False
        
        if match:
            results.append(todo)
    
    return {
        "success": True,
        "data": results,
        "count": len(results)
    }

@app.get("/ai/stats")
async def ai_get_stats(authorization: Optional[str] = Header(None)):
    """获取统计信息 - AI工具专用"""
    total = len(todos_db)
    completed = sum(1 for t in todos_db.values() if t["completed"])
    pending = total - completed
    
    return {
        "success": True,
        "data": {
            "total": total,
            "completed": completed,
            "pending": pending,
            "completion_rate": (completed / total * 100) if total > 0 else 0
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
