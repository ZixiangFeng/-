# Render 部署步骤

## 1. 上传到 GitHub

把 `RelationshipRepairChatbot` 这个文件夹上传到一个 GitHub 仓库。

如果 `git` 提示 Xcode license 错误，先在终端运行：

```bash
sudo xcodebuild -license
```

## 2. 在 Render 创建 Web Service

1. 打开 Render Dashboard。
2. 点击 `New`。
3. 选择 `Web Service`。
4. 连接你的 GitHub 仓库。
5. Root Directory 如果仓库里只放这个项目，就留空；如果仓库里有多个文件夹，填：

```text
RelationshipRepairChatbot
```

## 3. Render 配置

Render 会读取 `render.yaml`。如果需要手动填：

Build Command:

```bash
pip install -r requirements.txt
```

Start Command:

```bash
gunicorn app:app
```

## 4. 环境变量

在 Render 的 Environment 里填：

```env
OPENAI_API_KEY=你的 DeepSeek API Key
OPENAI_BASE_URL=https://api.deepseek.com
OPENAI_MODEL=deepseek-v4-flash
FLASK_SECRET_KEY=随便生成一串复杂字符串
```

不要上传本地 `.env` 文件。

## 5. 打开网址

部署成功后，Render 会给你一个网址，例如：

```text
https://relationship-repair-chatbot.onrender.com
```

别人用手机浏览器打开这个网址就能使用。

## 6. 检查 API 是否成功

聊天一次后，打开：

```text
https://你的-render-url/api/llm_status
```

如果看到：

```json
"used_api": true
```

说明 DeepSeek 已经接入成功。
