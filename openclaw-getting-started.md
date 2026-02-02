# OpenClaw 快速入门

## 你的连接信息

| 项目 | 值 |
|------|-----|
| **Gateway 地址** | `http://GATEWAY_HOST:OPENCLAW_PORT?token=OPENCLAW_TOKEN` |
| **WebSocket 地址** | `ws://GATEWAY_HOST:OPENCLAW_PORT?token=OPENCLAW_TOKEN` |
| **Gateway Token** | `OPENCLAW_TOKEN` |

> Token 也保存在 `~/.openclaw/token` 文件中

---

## 1. 浏览器访问 (Control UI)

直接打开：**http://GATEWAY_HOST:OPENCLAW_PORT?token=OPENCLAW_TOKEN**

## 2. CLI 连接

在终端中运行：

```bash
# 查看 token
cat ~/.openclaw/token

# 连接到 gateway
openclaw connect --gateway-url ws://GATEWAY_HOST:OPENCLAW_PORT --token $(cat ~/.openclaw/token)
```

## 3. VS Code 扩展

1. 安装 OpenClaw 扩展
2. 设置 Gateway URL: `ws://GATEWAY_HOST:OPENCLAW_PORT`
3. 输入 Token

## 4. 可用模型

| 模型 | Provider | 说明 |
|------|----------|------|
| Qwen3 32B | Huawei API | 默认模型 |
| Qwen3 0.6B | Ollama (本地) | 轻量级，本地推理 |
| DeepSeek R1(0528) | Huawei API | 推理模型 |

---

## 常用命令

```bash
# 查看 gateway 日志
cat /tmp/openclaw.log

# 查看 gateway 状态
curl -s http://127.0.0.1:18789/ | head

# 查看配置
cat ~/.openclaw/openclaw.json
```
