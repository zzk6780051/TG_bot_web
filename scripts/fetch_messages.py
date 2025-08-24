#!/usr/bin/env python3
"""
获取 Telegram 消息的脚本
使用 getUpdates API 方法获取最新消息
"""

import os
import json
import requests
from datetime import datetime
import pytz

# 存储上次处理的 update_id
LAST_UPDATE_FILE = 'data/last_update_id.txt'

def get_updates(bot_token, offset=None):
    """获取 Telegram 更新"""
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    params = {'timeout': 30}
    if offset:
        params['offset'] = offset
    
    try:
        response = requests.get(url, params=params, timeout=35)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching updates: {e}")
        return None

def load_messages():
    """加载现有消息"""
    if not os.path.exists('data/messages.json'):
        return []
    
    try:
        with open('data/messages.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_messages(messages):
    """保存消息到文件"""
    with open('data/messages.json', 'w', encoding='utf-8') as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)

def get_last_update_id():
    """获取上次处理的 update_id"""
    if os.path.exists(LAST_UPDATE_FILE):
        try:
            with open(LAST_UPDATE_FILE, 'r') as f:
                return int(f.read().strip())
        except (ValueError, FileNotFoundError):
            return None
    return None

def save_last_update_id(update_id):
    """保存最后处理的 update_id"""
    with open(LAST_UPDATE_FILE, 'w') as f:
        f.write(str(update_id))

def process_messages(bot_token, chat_id=None):
    """处理消息"""
    # 获取上次处理的 update_id
    last_update_id = get_last_update_id()
    
    # 获取更新
    result = get_updates(bot_token, offset=last_update_id)
    if not result or not result.get('ok'):
        print("Failed to get updates")
        return
    
    updates = result.get('result', [])
    if not updates:
        print("No new updates")
        return
    
    # 加载现有消息
    messages = load_messages()
    message_ids = {msg['message_id'] for msg in messages}
    
    # 处理新消息
    new_messages = 0
    max_update_id = last_update_id or 0
    
    for update in updates:
        update_id = update.get('update_id')
        if update_id > max_update_id:
            max_update_id = update_id
        
        message = update.get('message') or update.get('channel_post')
        if not message:
            continue
        
        # 检查是否来自指定聊天
        message_chat_id = message.get('chat', {}).get('id')
        if chat_id and int(chat_id) != message_chat_id:
            continue
        
        # 只处理文本消息
        if 'text' not in message:
            continue
        
        # 检查是否已存在
        msg_id = message.get('message_id')
        if msg_id in message_ids:
            continue
        
        # 提取消息信息
        sender = message.get('from', {})
        message_data = {
            "message_id": msg_id,
            "chat_id": message_chat_id,
            "sender_id": sender.get('id'),
            "sender_name": f"{sender.get('first_name', '')} {sender.get('last_name', '')}".strip() or "Unknown",
            "text": message.get('text', ''),
            "timestamp": message.get('date'),
            "processed_at": datetime.now(pytz.timezone('UTC')).isoformat()
        }
        
        messages.append(message_data)
        message_ids.add(msg_id)
        new_messages += 1
    
    # 保存消息和最后 update_id
    if new_messages > 0:
        # 按时间排序
        messages.sort(key=lambda x: x.get('timestamp', 0))
        save_messages(messages)
        print(f"Added {new_messages} new messages")
    
    if max_update_id > (last_update_id or 0):
        save_last_update_id(max_update_id + 1)  # Telegram API 要求 offset 是下一个 update_id
        print(f"Updated last_update_id to {max_update_id + 1}")

if __name__ == '__main__':
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = os.environ.get('CHAT_ID')
    
    if not bot_token:
        print("Error: TELEGRAM_BOT_TOKEN environment variable is required")
        exit(1)
    
    process_messages(bot_token, chat_id)
