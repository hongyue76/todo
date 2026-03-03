#!/usr/bin/env python3
"""
测试AI工具接口
"""

import requests
import json

BASE_URL = "http://localhost:8001/ai"

def test_login():
    """测试登录"""
    print("=" * 50)
    print("测试 1: 用户登录")
    print("=" * 50)
    
    response = requests.get(f"{BASE_URL}/auth/login", params={
        "username": "admin",
        "password": "password123"
    })
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        print(f"✓ 登录成功，令牌：{token}")
        return token
    else:
        print(f"✗ 登录失败：{response.text}")
        return None

def test_create_todo(token):
    """测试创建任务"""
    print("\n" + "=" * 50)
    print("测试 2: 创建任务")
    print("=" * 50)
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/todos", json={
        "title": "测试AI调用",
        "description": "这是一个通过API创建的任务",
        "priority": "HIGH",
        "category": "测试"
    }, headers=headers)
    
    if response.status_code == 200:
        todo = response.json()
        print(f"✓ 任务创建成功：{json.dumps(todo, indent=2, ensure_ascii=False)}")
        return todo["data"]["id"]
    else:
        print(f"✗ 创建失败：{response.text}")
        return None

def test_list_todos(token):
    """测试获取任务列表"""
    print("\n" + "=" * 50)
    print("测试 3: 获取任务列表")
    print("=" * 50)
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/todos", headers=headers)
    
    if response.status_code == 200:
        todos = response.json()
        print(f"✓ 获取成功，共 {todos['count']} 个任务:")
        for todo in todos["data"]:
            status = "✅" if todo["completed"] else "⬜"
            priority = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(todo["priority"], "")
            print(f"  {status} {priority} #{todo['id']} {todo['title']}")
    else:
        print(f"✗ 获取失败：{response.text}")

def test_complete_todo(token, todo_id):
    """测试完成任务"""
    print("\n" + "=" * 50)
    print(f"测试 4: 完成任务 #{todo_id}")
    print("=" * 50)
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.put(f"{BASE_URL}/todos/{todo_id}", json={
        "completed": True
    }, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ 完成成功：{result['message']}")
    else:
        print(f"✗ 完成失败：{response.text}")

def test_search(token):
    """测试搜索"""
    print("\n" + "=" * 50)
    print("测试 5: 搜索任务")
    print("=" * 50)
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/todos/search", params={
        "query": "AI"
    }, headers=headers)
    
    if response.status_code == 200:
        results = response.json()
        print(f"✓ 搜索成功，找到 {results['count']} 个匹配项:")
        for todo in results["data"]:
            print(f"  - #{todo['id']} {todo['title']}")
    else:
        print(f"✗ 搜索失败：{response.text}")

def test_stats(token):
    """测试统计"""
    print("\n" + "=" * 50)
    print("测试 6: 获取统计信息")
    print("=" * 50)
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/stats", headers=headers)
    
    if response.status_code == 200:
        stats = response.json()["data"]
        print(f"✓ 统计信息:")
        print(f"  总任务数：{stats['total']}")
        print(f"  已完成：{stats['completed']}")
        print(f"  未完成：{stats['pending']}")
        print(f"  完成率：{stats['completion_rate']:.1f}%")
    else:
        print(f"✗ 获取失败：{response.text}")

if __name__ == "__main__":
    print("\n🤖 TODO系统 AI工具接口测试\n")
    
    # 1. 登录
    token = test_login()
    if not token:
        print("\n❌ 登录失败，终止测试")
        exit(1)
    
    # 2. 创建任务
    todo_id = test_create_todo(token)
    
    # 3. 获取列表
    test_list_todos(token)
    
    # 4. 完成任务
    if todo_id:
        test_complete_todo(token, todo_id)
    
    # 5. 搜索
    test_search(token)
    
    # 6. 统计
    test_stats(token)
    
    print("\n" + "=" * 50)
    print("✅ 所有测试完成！")
    print("=" * 50)
