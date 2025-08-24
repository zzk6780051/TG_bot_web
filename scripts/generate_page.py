#!/usr/bin/env python3
"""
生成显示 Telegram 消息的 HTML 页面
"""

import json
import os
from datetime import datetime
import pytz

def load_messages():
    """加载消息数据"""
    if not os.path.exists('data/messages.json'):
        return []
    
    try:
        with open('data/messages.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def generate_html():
    # 加载消息数据
    messages = load_messages()
    
    # 按时间倒序排列
    messages.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
    
    # 限制显示的消息数量
    items_per_page = int(os.environ.get('ITEMS_PER_PAGE', 50))
    display_messages = messages[:items_per_page]
    
    # 生成 HTML
    site_title = os.environ.get('SITE_TITLE', 'Telegram 群聊消息存档')
    timezone = os.environ.get('TIMEZONE', 'UTC')
    tz = pytz.timezone(timezone)
    
    html_content = f"""<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{site_title}</title>
    <style>
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            max-width: 1000px; 
            margin: 0 auto; 
            padding: 20px;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
        }}
        .container {{
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 20px;
        }}
        .header {{ 
            text-align: center; 
            margin-bottom: 30px;
            border-bottom: 1px solid #eee;
            padding-bottom: 20px;
        }}
        .message {{ 
            border-left: 4px solid #4a90e2; 
            padding: 15px; 
            margin-bottom: 15px;
            background-color: #f9f9f9;
            border-radius: 0 4px 4px 0;
        }}
        .sender {{ 
            font-weight: bold; 
            color: #4a90e2;
            margin-right: 8px;
        }}
        .timestamp {{ 
            color: #888; 
            font-size: 0.85em;
            display: block;
            margin-top: 5px;
        }}
        .text {{ 
            margin: 8px 0;
            white-space: pre-wrap;
            line-height: 1.5;
        }}
        .footer {{
            text-align: center;
            margin-top: 30px;
            color: #888;
            font-size: 0.9em;
            border-top: 1px solid #eee;
            padding-top: 20px;
        }}
        .stats {{
            background: #e8f4fc;
            padding: 10px;
            border-radius: 4px;
            margin-bottom: 20px;
        }}
        @media (max-width: 600px) {{
            body {{ padding: 15px; }}
            .container {{ padding: 15px; }}
            .message {{ padding: 10px; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{site_title}</h1>
            <p>自动从 Telegram 群组获取并展示消息</p>
        </div>
        
        <div class="stats">
            总共收录了 <strong>{len(messages)}</strong> 条消息，显示最近 <strong>{len(display_messages)}</strong> 条
        </div>
        
        <div id="messages">"""
    
    for msg in display_messages:
        timestamp = msg.get('timestamp', 0)
        if timestamp:
            dt = datetime.fromtimestamp(timestamp, tz).strftime('%Y-%m-%d %H:%M:%S')
        else:
            dt = "未知时间"
            
        sender_name = msg.get('sender_name', '未知用户')
        text = msg.get('text', '')
        
        html_content += f"""
            <div class="message">
                <span class="sender">{sender_name}</span>
                <div class="text">{text}</div>
                <span class="timestamp">{dt}</span>
            </div>"""

    html_content += f"""
        </div>
        
        <div class="footer">
            <p>由 GitHub Actions 自动生成 | 最后更新: <span id="updateTime">{datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')}</span></p>
            <p>每5分钟自动检查新消息</p>
        </div>
    </div>
    
    <script>
        // 自动更新页面时间
        function updateTime() {{
            document.getElementById('updateTime').textContent = new Date().toLocaleString();
        }}
        setInterval(updateTime, 1000);
        updateTime();
        
        // 自动滚动到最新消息
        window.addEventListener('load', function() {{
            if (window.location.hash === '') {{
                window.scrollTo(0, 0);
            }}
        }});
    </script>
</body>
</html>"""

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Generated HTML page with {len(display_messages)} of {len(messages)} total messages")

if __name__ == '__main__':
    generate_html()
