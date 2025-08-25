#!/usr/bin/env python3
"""
使用 GitHub API 更新文件的脚本
不使用 Git 命令，直接通过 API 更新文件
"""

import os
import json
import base64
import requests
from pathlib import Path

def get_file_sha(file_path):
    """获取文件的 SHA 值"""
    owner = os.environ.get('REPO_OWNER')
    repo = os.environ.get('REPO_NAME')
    token = os.environ.get('TOKEN')  # 修改为使用 TOKEN 环境变量
    
    if not all([owner, repo, token]):
        print("Missing required environment variables")
        return None
    
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json().get('sha')
        elif response.status_code == 404:
            return None  # 文件不存在
        else:
            print(f"Error getting file SHA: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Exception getting file SHA: {e}")
        return None

def update_file_via_api(file_path, content, message):
    """通过 GitHub API 更新文件"""
    owner = os.environ.get('REPO_OWNER')
    repo = os.environ.get('REPO_NAME')
    token = os.environ.get('TOKEN')  # 修改为使用 TOKEN 环境变量
    
    if not all([owner, repo, token]):
        print("Missing required environment variables")
        return False
    
    # 获取文件当前 SHA
    sha = get_file_sha(file_path)
    
    # 准备 API 请求
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # 编码内容
    if isinstance(content, str):
        content = content.encode('utf-8')
    encoded_content = base64.b64encode(content).decode('utf-8')
    
    # 准备数据
    data = {
        "message": message,
        "content": encoded_content,
        "branch": "main"  # 默认分支
    }
    
    if sha:
        data["sha"] = sha
    
    try:
        response = requests.put(url, headers=headers, json=data)
        if response.status_code in [200, 201]:
            print(f"Successfully updated {file_path}")
            return True
        else:
            print(f"Error updating {file_path}: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Exception updating {file_path}: {e}")
        return False

def read_file_content(file_path):
    """读取文件内容"""
    try:
        with open(file_path, 'rb') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

def should_update_file(file_path):
    """检查文件是否需要更新"""
    # 检查是否有变化标志文件
    if os.path.exists('no_changes.flag'):
        return False
    
    # 检查文件是否存在
    if not os.path.exists(file_path):
        return False
        
    # 对于消息文件，检查是否有内容
    if file_path == 'data/messages.json':
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
                return len(content) > 0
        except:
            return False
            
    return True

def main():
    """主函数"""
    # 检查是否有变化
    if os.path.exists('no_changes.flag'):
        print("No changes detected, skipping update")
        os.remove('no_changes.flag')
        return True
    
    # 检查哪些文件需要更新
    files_to_update = []
    
    # 检查消息文件
    messages_path = 'data/messages.json'
    if should_update_file(messages_path):
        files_to_update.append({
            'path': messages_path,
            'message': 'Update Telegram messages'
        })
    
    # 检查最后更新ID文件
    last_update_path = 'data/last_update_id.txt'
    if should_update_file(last_update_path):
        files_to_update.append({
            'path': last_update_path,
            'message': 'Update last update ID'
        })
    
    # 检查HTML文件
    html_path = 'index.html'
    if should_update_file(html_path):
        files_to_update.append({
            'path': html_path,
            'message': 'Update message archive page'
        })
    
    # 如果没有文件需要更新
    if not files_to_update:
        print("No files need updating")
        return True
    
    # 更新文件
    success = True
    for file_info in files_to_update:
        content = read_file_content(file_info['path'])
        if content is not None:
            if not update_file_via_api(file_info['path'], content, file_info['message']):
                success = False
    
    return success

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
