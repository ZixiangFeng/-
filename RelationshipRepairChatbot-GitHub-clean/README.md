# Relationship Repair Chatbot

Relationship Repair Chatbot 是一个用于关系修复沟通实验的 Flask Web 应用。项目面向行为实验场景，重点不是开放式闲聊，而是在固定实验流程中提供半结构化、可控的大语言模型回复。

应用包含实验封面页、条件选择页和手机聊天界面，支持 DeepSeek 或其他 OpenAI-compatible API。

## 核心特点

- 实验封面页：点击“开始体验”后进入测试
- 角色条件：受伤害者任务 / 过错方任务
- 信息框架：Gain frame / Loss frame
- 共情水平：High empathy / Low empathy
- 半结构化 LLM 回复：在固定流程、固定标签和约束提示下生成自然语言
- 手机聊天 UI：模拟移动端聊天体验
- 输入有效性检查：避免用户输入无意义内容后继续推进流程
- 对话结束规则：用户表达采纳、信任或行动意向后自动停止继续建议
- 数据记录：对话记录保存到 `data/conversations.csv`

## 页面流程

```text
/             实验封面页
/setup        选择关系角色
/conditions   选择信息框架和共情条件
/chat         聊天机器人界面
/finish       结束页
```

## 实验条件

### 角色条件

- `victim`：受伤害者任务
- `transgressor`：过错方任务

### 信息框架

- `gain`：强调采纳建议后的积极结果
- `loss`：强调不采纳建议或继续不当行为可能带来的负面后果

### 共情水平

- `high`：高共情表达，包含感谢、关怀、人称代词和主动支持表达
- `low`：低共情表达，减少拟人化和显性同理心线索，但仍保留 IMA 情感支持功能

## 项目结构

```text
RelationshipRepairChatbot/
├── app.py
├── requirements.txt
├── Procfile
├── render.yaml
├── README.md
├── DEPLOY_RENDER.md
├── .env.example
├── data/
│   └── .gitkeep
├── dialogue/
│   ├── advice.py
│   ├── empathy.py
│   ├── exploration.py
│   ├── llm.py
│   └── scenarios.py
├── static/
│   ├── css/style.css
│   ├── js/chat.js
│   └── img/lab-cover.png
└── templates/
    ├── index.html
    ├── setup.html
    ├── conditions.html
    ├── chat.html
    └── finish.html
```

## 本地运行

进入项目目录：

```bash
cd RelationshipRepairChatbot
```

安装依赖：

```bash
pip install -r requirements.txt
```

配置环境变量：

```bash
cp .env.example .env
```

然后在 `.env` 中填写 API Key。

启动应用：

```bash
python app.py
```

浏览器打开：

```text
http://127.0.0.1:5000/
```

## DeepSeek API 设置

`.env` 示例：

```env
OPENAI_API_KEY=你的 DeepSeek API Key
OPENAI_BASE_URL=https://api.deepseek.com
OPENAI_MODEL=deepseek-v4-flash
FLASK_SECRET_KEY=换成一串复杂随机字符
```

项目使用 OpenAI SDK 调用 OpenAI-compatible API，因此可以通过 `OPENAI_BASE_URL` 接入 DeepSeek。

检查 API 是否接入成功：

```text
http://127.0.0.1:5000/api/llm_status
```

如果聊天后看到：

```json
{
  "used_api": true
}
```

说明 API 调用成功。

## Render 部署

Render Web Service 配置：

```text
Build Command: pip install -r requirements.txt
Start Command: gunicorn app:app
```

环境变量：

```env
OPENAI_API_KEY=你的 DeepSeek API Key
OPENAI_BASE_URL=https://api.deepseek.com
OPENAI_MODEL=deepseek-v4-flash
FLASK_SECRET_KEY=换成一串复杂随机字符
```

如果 GitHub 仓库中项目位于子文件夹，例如：

```text
RelationshipRepairChatbot-GitHub-clean
```

则 Render 的 `Root Directory` 填：

```text
RelationshipRepairChatbot-GitHub-clean
```

如果仓库根目录直接就是 `app.py`、`requirements.txt`、`templates/` 等文件，则 `Root Directory` 留空。

## GitHub 上传注意事项

不要上传以下文件：

```text
.env
data/conversations.csv
__pycache__/
*.pyc
.DS_Store
```

这些文件已经写入 `.gitignore`。

上传前建议确认项目中包含：

```text
app.py
requirements.txt
Procfile
render.yaml
templates/
static/
dialogue/
README.md
```

## 数据保存

实验对话会保存到：

```text
data/conversations.csv
```

该文件用于本地实验记录，不建议上传到 GitHub。

## 说明

本项目用于关系修复聊天机器人实验 demo。为了保证实验控制，系统回复受到预设流程、角色条件、共情条件和框架条件约束。LLM 主要用于在这些约束内生成更自然的中文表达，而不是自由对话。
