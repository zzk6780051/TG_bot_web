# Telegram 群聊消息存档

这个项目使用 GitHub Actions 定时获取 Telegram 群聊消息，并自动生成静态网页展示。完全使用 GitHub API 进行文件更新，不依赖 Git 命令。

## 功能特点

- 无需服务器，完全基于 GitHub Actions 和 Pages
- 使用 GitHub API 更新文件，不依赖 Git 命令
- 定时获取 Telegram 群聊消息（每5分钟）
- 自动生成美观的消息存档网页
- 完全免费（在 GitHub 免费额度内）

## 设置步骤

### 1. 创建 Telegram 机器人

1. 在 Telegram 中联系 [@BotFather](https://t.me/BotFather)
2. 发送 `/newbot` 命令创建新机器人
3. 保存提供的 API Token

### 2. 获取群组 ID

1. 将机器人添加到群组
2. 给群组发送一条消息
3. 访问 `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
4. 查找群组 ID（通常为负数）

### 3. 创建 GitHub Personal Access Token

1. 访问 GitHub 的 [Personal Access Tokens 页面](https://github.com/settings/tokens)
2. 点击 **Generate new token** → **Generate new token (classic)**
3. 设置 Token 描述（如 "Telegram Bot Token"）
4. 选择权限：
   - `repo` (全选) - 用于读写仓库内容
   - `workflow` - 用于管理工作流
5. 点击 **Generate token**
6. **重要**：复制生成的 token 并立即保存

### 4. 配置 GitHub Repository

1. Fork 或克隆此仓库
2. 在仓库设置中添加以下 Secrets：
   - `TELEGRAM_BOT_TOKEN`: 你的 Telegram 机器人令牌
   - `CHAT_ID`: 你的 Telegram 群组 ID（可选，如不设置则获取所有聊天消息）
   - `TOKEN`: 你的 GitHub Personal Access Token

### 5. 启用 GitHub Pages

1. 进入仓库的 Settings → Pages
2. 选择 "Deploy from a branch"
3. 选择分支（通常是 main）和文件夹（通常是 /root）
4. 点击 Save

## 工作原理

1. GitHub Actions 每5分钟运行一次工作流
2. 使用 Telegram Bot API 的 getUpdates 方法获取新消息
3. 处理消息并保存到本地文件
4. 生成静态 HTML 页面
5. 使用 GitHub API 直接更新仓库文件
6. 部署到 GitHub Pages

## 自定义配置

你可以通过修改工作流文件中的环境变量来自定义：

- `SITE_TITLE`: 网页标题
- `ITEMS_PER_PAGE`: 每页显示的消息数量
- `TIMEZONE`: 显示消息时使用的时区

## 注意事项

1. 机器人需要在群组中且有权限读取消息
2. GitHub Actions 有使用限制，注意不要超过免费额度
3. 首次运行可能需要手动触发工作流
4. GitHub API 有速率限制，注意不要过于频繁地调用

## 技术支持

如有问题，请提交 Issue 或联系开发者。
