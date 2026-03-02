#!/usr/bin/env python3
"""
TODO应用命令行接口 (CLI)
支持通过命令行直接操作TODO系统
"""

import click
import requests
import json
from typing import Optional, List
from datetime import datetime
import sys

# API配置
API_BASE_URL = "http://localhost:8000/api"
TOKEN_FILE = "~/.todo_app_token"

def get_token() -> Optional[str]:
    """获取存储的认证令牌"""
    try:
        with open(TOKEN_FILE, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

def save_token(token: str):
    """保存认证令牌"""
    with open(TOKEN_FILE, 'w') as f:
        f.write(token)

@click.group()
def cli():
    """TODO应用命令行接口"""
    pass

@cli.command()
@click.option('--username', required=True, help='用户名')
@click.option('--password', required=True, help='密码', hide_input=True)
def login(username: str, password: str):
    """登录到TODO系统"""
    try:
        response = requests.post(f"{API_BASE_URL}/auth/login", data={
            "username": username,
            "password": password
        })
        
        if response.status_code == 200:
            token = response.json()["access_token"]
            save_token(token)
            click.echo(click.style("✓ 登录成功", fg="green"))
        else:
            click.echo(click.style(f"✗ 登录失败: {response.text}", fg="red"))
    except Exception as e:
        click.echo(click.style(f"✗ 错误: {str(e)}", fg="red"))

@cli.command()
@click.option('--title', required=True, help='任务标题')
@click.option('--description', default='', help='任务描述')
@click.option('--priority', type=click.Choice(['HIGH', 'MEDIUM', 'LOW']), default='MEDIUM', help='优先级')
@click.option('--category', default='默认', help='分类')
@click.option('--due-date', default=None, help='截止日期 (YYYY-MM-DD)')
def add(title: str, description: str, priority: str, category: str, due_date: Optional[str]):
    """添加新任务"""
    token = get_token()
    if not token:
        click.echo(click.style("✗ 请先登录", fg="red"))
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "title": title,
        "description": description,
        "priority": priority,
        "category": category,
        "due_date": due_date
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/todos", json=data, headers=headers)
        if response.status_code == 200:
            todo = response.json()
            click.echo(click.style(f"✓ 任务已创建: #{todo['id']} - {todo['title']}", fg="green"))
        else:
            click.echo(click.style(f"✗ 创建失败: {response.text}", fg="red"))
    except Exception as e:
        click.echo(click.style(f"✗ 错误: {str(e)}", fg="red"))

@cli.command()
@click.option('--status', type=click.Choice(['all', 'active', 'completed']), default='active', help='筛选状态')
@click.option('--limit', default=20, help='返回数量限制')
def list(status: str, limit: int):
    """列出任务"""
    token = get_token()
    if not token:
        click.echo(click.style("✗ 请先登录", fg="red"))
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    params = {"skip": 0, "limit": limit}
    
    try:
        response = requests.get(f"{API_BASE_URL}/todos", params=params, headers=headers)
        if response.status_code == 200:
            todos = response.json()
            
            if not todos:
                click.echo("暂无任务")
                return
            
            for todo in todos:
                status_icon = "✅" if todo["completed"] else "⬜"
                priority_icon = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(todo["priority"], "")
                
                click.echo(f"{status_icon} {priority_icon} #{todo['id']} {todo['title']}")
                if todo.get('description'):
                    click.echo(f"   📝 {todo['description']}")
        else:
            click.echo(click.style(f"✗ 获取失败: {response.text}", fg="red"))
    except Exception as e:
        click.echo(click.style(f"✗ 错误: {str(e)}", fg="red"))

@cli.command()
@click.argument('todo_id', type=int)
@click.option('--complete/--no-complete', default=True, help='标记为完成')
def complete(todo_id: int, complete: bool):
    """标记任务完成/未完成"""
    token = get_token()
    if not token:
        click.echo(click.style("✗ 请先登录", fg="red"))
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    data = {"completed": complete}
    
    try:
        response = requests.put(f"{API_BASE_URL}/todos/{todo_id}", json=data, headers=headers)
        if response.status_code == 200:
            status = "已完成" if complete else "未完成"
            click.echo(click.style(f"✓ 任务 #{todo_id} 已标记为{status}", fg="green"))
        else:
            click.echo(click.style(f"✗ 更新失败: {response.text}", fg="red"))
    except Exception as e:
        click.echo(click.style(f"✗ 错误: {str(e)}", fg="red"))

@cli.command()
@click.argument('todo_id', type=int)
def delete(todo_id: int):
    """删除任务"""
    token = get_token()
    if not token:
        click.echo(click.style("✗ 请先登录", fg="red"))
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.delete(f"{API_BASE_URL}/todos/{todo_id}", headers=headers)
        if response.status_code == 200:
            click.echo(click.style(f"✓ 任务 #{todo_id} 已删除", fg="green"))
        else:
            click.echo(click.style(f"✗ 删除失败: {response.text}", fg="red"))
    except Exception as e:
        click.echo(click.style(f"✗ 错误: {str(e)}", fg="red"))

@cli.command()
@click.option('--query', default='', help='搜索关键词')
@click.option('--priority', type=click.Choice(['HIGH', 'MEDIUM', 'LOW']), help='优先级筛选')
@click.option('--category', default='', help='分类筛选')
def search(query: str, priority: Optional[str], category: str):
    """搜索任务"""
    token = get_token()
    if not token:
        click.echo(click.style("✗ 请先登录", fg="red"))
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    params = {}
    
    if query:
        params["q"] = query
    if priority:
        params["priority"] = priority
    if category:
        params["category"] = category
    
    try:
        response = requests.get(f"{API_BASE_URL}/todos/search", params=params, headers=headers)
        if response.status_code == 200:
            todos = response.json()
            
            if not todos:
                click.echo("未找到匹配的任务")
                return
            
            click.echo(f"找到 {len(todos)} 个匹配的任务:")
            for todo in todos:
                status_icon = "✅" if todo["completed"] else "⬜"
                priority_icon = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(todo["priority"], "")
                click.echo(f"{status_icon} {priority_icon} #{todo['id']} {todo['title']}")
        else:
            click.echo(click.style(f"✗ 搜索失败: {response.text}", fg="red"))
    except Exception as e:
        click.echo(click.style(f"✗ 错误: {str(e)}", fg="red"))

@cli.command()
@click.argument('todo_id', type=int)
def show(todo_id: int):
    """显示任务详情"""
    token = get_token()
    if not token:
        click.echo(click.style("✗ 请先登录", fg="red"))
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{API_BASE_URL}/todos/{todo_id}", headers=headers)
        if response.status_code == 200:
            todo = response.json()
            
            click.echo(f"\n{'='*50}")
            click.echo(f"任务 #{todo['id']}: {todo['title']}")
            click.echo(f"{'='*50}")
            click.echo(f"状态: {'✅ 已完成' if todo['completed'] else '⬜ 未完成'}")
            click.echo(f"优先级: {todo['priority']}")
            click.echo(f"分类: {todo['category']}")
            if todo.get('description'):
                click.echo(f"描述: {todo['description']}")
            if todo.get('due_date'):
                click.echo(f"截止日期: {todo['due_date']}")
            click.echo(f"创建时间: {todo['created_at']}")
            click.echo(f"更新时间: {todo['updated_at']}")
            click.echo(f"{'='*50}\n")
        else:
            click.echo(click.style(f"✗ 获取失败: {response.text}", fg="red"))
    except Exception as e:
        click.echo(click.style(f"✗ 错误: {str(e)}", fg="red"))

@cli.command()
@click.argument('todo_id', type=int)
@click.option('--parent-id', type=int, help='父任务ID')
def move(todo_id: int, parent_id: Optional[int]):
    """移动任务（设置父任务）"""
    token = get_token()
    if not token:
        click.echo(click.style("✗ 请先登录", fg="red"))
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    data = {"parent_id": parent_id}
    
    try:
        response = requests.put(f"{API_BASE_URL}/todos/{todo_id}", json=data, headers=headers)
        if response.status_code == 200:
            if parent_id:
                click.echo(click.style(f"✓ 任务 #{todo_id} 已移动到任务 #{parent_id} 下", fg="green"))
            else:
                click.echo(click.style(f"✓ 任务 #{todo_id} 已移出子任务", fg="green"))
        else:
            click.echo(click.style(f"✗ 移动失败: {response.text}", fg="red"))
    except Exception as e:
        click.echo(click.style(f"✗ 错误: {str(e)}", fg="red"))

@cli.command()
def stats():
    """显示统计信息"""
    token = get_token()
    if not token:
        click.echo(click.style("✗ 请先登录", fg="red"))
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{API_BASE_URL}/todos/stats", headers=headers)
        if response.status_code == 200:
            stats = response.json()
            
            click.echo(f"\n📊 TODO统计信息")
            click.echo(f"{'='*30}")
            click.echo(f"总任务数: {stats.get('total', 0)}")
            click.echo(f"已完成: {stats.get('completed', 0)}")
            click.echo(f"未完成: {stats.get('pending', 0)}")
            click.echo(f"完成率: {stats.get('completion_rate', 0):.1f}%")
            click.echo(f"{'='*30}\n")
        else:
            click.echo(click.style(f"✗ 获取统计失败: {response.text}", fg="red"))
    except Exception as e:
        click.echo(click.style(f"✗ 错误: {str(e)}", fg="red"))

if __name__ == '__main__':
    cli()
