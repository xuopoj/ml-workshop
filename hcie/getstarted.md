# HCIE Ascend NPU 开发环境

使用本地 VSCode 通过 SSH 连接到 HCIE Ascend NPU 开发容器。

## SSH 连接信息

```
Host: SSH_HOST_PLACEHOLDER
Port: SSH_PORT_PLACEHOLDER
User: root
Password: SSH_PASSWORD_PLACEHOLDER
```

**密码说明**：运行 `passwd` 可修改密码（会自动持久化）。

## 配置 SSH

编辑 `~/.ssh/config`，添加：

```
Host hcie
    HostName SSH_HOST_PLACEHOLDER
    Port SSH_PORT_PLACEHOLDER
    User root
```

## 连接

1. 打开 VSCode
2. 按 `Ctrl+Shift+P`（Mac 上按 `Cmd+Shift+P`）
3. 输入 "Remote-SSH: Connect to Host"
4. 选择 `hcie`
5. 输入密码

### 打开工作区

连接成功后，打开 `/root/share` 作为工作区。

## Conda 环境

容器预装了两个 conda 环境：

| 环境 | Python | 说明 |
|------|--------|------|
| `env0` | 3.9 | NLP / LLM（transformers 4.29、mindformers、deepspeed） |
| `env1` | 3.9 | CV（mindcv、scikit-image、einops、transformers 4.39） |

默认激活 `env0`。两个环境均已注册为 Jupyter Notebook 内核，可在 JupyterHub 中直接选择使用。

### 在 Notebook 中切换环境

打开 Notebook 后，点击右上角的内核名称，选择 `env0` 或 `env1`。

### 常用命令（终端）

```bash
# 切换环境
conda activate env1

# 查看已安装的包
conda list

# 安装 conda 包
conda install scipy

# 安装 pip 包（在当前 conda 环境中）
pip install some-package

# 查看所有环境
conda env list
```

### 在 VSCode 中选择 Python 解释器

1. 按 `Ctrl+Shift+P`
2. 输入 "Python: Select Interpreter"
3. 选择 `/opt/conda/envs/env0/bin/python` 或 `/opt/conda/envs/env1/bin/python`

## 代理配置

远程环境已预配置代理，大部分工具可以直接联网。

### curl / wget / git

环境变量已自动设置，直接使用即可：

```bash
curl -fsSL https://example.com
git clone https://github.com/user/repo
```

如需手动设置：

```bash
export HTTP_PROXY=http://ml-workshop-proxy:8899
export HTTPS_PROXY=http://ml-workshop-proxy:8899
export NO_PROXY=localhost,127.0.0.1,ml-workshop-hub,ml-workshop-proxy,*.huawei.com
```

### pip

已配置使用本地 devpi 缓存索引，首次安装从 PyPI 拉取并缓存，后续安装直接从本地读取：

```bash
pip install numpy                         # 自动使用本地缓存索引
```

如需临时使用官方源：

```bash
pip install --index-url https://pypi.org/simple/ <package>
```

### apt

已配置使用本地 apt-cacher-ng 缓存代理：

```bash
apt-get update && apt-get install -y <package>
```

### VSCode 代理设置

通过 SSH 连接后，打开设置（`Ctrl+,`）搜索 `proxy`，设置：

- `Http: Proxy` → `http://ml-workshop-proxy:8899`
- `Http: Proxy Strict SSL` → 取消勾选

或在 `settings.json` 中添加：

```json
{
    "http.proxy": "http://ml-workshop-proxy:8899",
    "http.proxyStrictSSL": false
}
```

## 常见问题

### 连接被拒绝
- 确认容器正在运行：`docker ps | grep hcie`
- 查看容器日志：`docker logs ml-workshop-hcie`

### Host key 变更警告
- 容器首次启动会生成 SSH host key 并持久化
- 如果收到警告，运行 `ssh-keygen -R "[SSH_HOST_PLACEHOLDER]:SSH_PORT_PLACEHOLDER"` 清除旧 key

### conda 环境未激活
- VS Code 终端默认激活 `env0`
- 如未激活，手动运行：`conda activate env0`
