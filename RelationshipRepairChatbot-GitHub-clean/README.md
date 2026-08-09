# Relationship Repair Chatbot

一个用于关系修复沟通实验的 Flask Web 应用。应用支持手机样式聊天界面、角色条件、信息框架条件、共情水平条件，以及 DeepSeek/OpenAI-compatible API 接入。

## 功能

- 角色条件：受伤害者任务 / 过错方任务
- 信息框架：Gain frame / Loss frame
- 共情水平：High empathy / Low empathy
- 半结构化 LLM 回复：在固定实验流程内调用大语言模型
- 手机聊天 UI
- 对话数据保存到 `data/conversations.csv`
- Render 部署支持

## 本地运行

```bash
cd RelationshipRepairChatbot
pip install -r requirements.txt
python app.py
```

打开：

```text
http://127.0.0.1:5000/
```

## API Key 设置

复制 `.env.example` 为 `.env`，然后填写自己的 DeepSeek API Key：

```env
OPENAI_API_KEY=你的 DeepSeek API Key
OPENAI_BASE_URL=https://api.deepseek.com
OPENAI_MODEL=deepseek-v4-flash
FLASK_SECRET_KEY=换成一串复杂随机字符
```

注意：不要把 `.env` 上传到 GitHub。

## Render 部署

Render 配置：

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

如果仓库里项目文件夹叫 `RelationshipRepairChatbot`，Render 的 Root Directory 填：

```text
RelationshipRepairChatbot
```

## 不要上传的文件

- `.env`
- `data/conversations.csv`
- `__pycache__/`
- `.DS_Store`

这些文件已经写入 `.gitignore`。
