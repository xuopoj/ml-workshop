# VSCode 远程开发环境配置

使用本地 VSCode 连接到研讨会的远程开发容器。


## 方式一：浏览器访问（最简单）

| 服务 | 地址 |
|------|------|
| VSCode (浏览器) | `http://VSCODE_SSH_HOST_PLACEHOLDER:28000/user/JUPYTERHUB_USER_PLACEHOLDER/vscode/?folder=/root/work` |
| JupyterLab | `http://VSCODE_SSH_HOST_PLACEHOLDER:28000/user/JUPYTERHUB_USER_PLACEHOLDER/lab` |
| JupyterHub 控制面板 | `http://VSCODE_SSH_HOST_PLACEHOLDER:28000/hub/home` |

## 方式二：本地 VSCode 通过 SSH 连接

### 前置条件

- 本地安装 [Visual Studio Code](https://code.visualstudio.com/)
- 安装 [Remote - SSH](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-ssh) 扩展


### SSH 连接信息

```
Host: VSCODE_SSH_HOST_PLACEHOLDER
Port: VSCODE_SSH_PORT_PLACEHOLDER
User: VSCODE_USER_PLACEHOLDER
Password: VSCODE_PASSWORD_PLACEHOLDER
```

**密码说明**：首次启动时自动生成。运行 `passwd` 可修改密码（会自动持久化）。

### 配置 SSH

编辑 `~/.ssh/config`，添加：

```
Host ml-workshop
    HostName VSCODE_SSH_HOST_PLACEHOLDER
    Port VSCODE_SSH_PORT_PLACEHOLDER
    User VSCODE_USER_PLACEHOLDER
```

### 连接

1. 打开 VSCode
2. 按 `Ctrl+Shift+P`（Mac 上按 `Cmd+Shift+P`）
3. 输入 "Remote-SSH: Connect to Host"
4. 选择 `ml-workshop`
5. 输入密码

### 打开工作区

连接成功后，打开 `~/work` 作为工作区。

## 代理配置

远程环境已预配置代理，大部分工具可以直接联网。以下是各工具的代理说明：

### curl / wget / git

环境变量已自动设置，直接使用即可：

```bash
curl -fsSL https://example.com            # 自动走代理
wget https://example.com/file.tar.gz      # 自动走代理
git clone https://github.com/user/repo    # 自动走代理
```

如需手动设置（如环境变量丢失）：

```bash
export HTTP_PROXY=http://ml-workshop-proxy:8899
export HTTPS_PROXY=http://ml-workshop-proxy:8899
export NO_PROXY=localhost,127.0.0.1,ml-workshop-hub,ml-workshop-proxy,*.huawei.com
```

### pip

已配置使用本地 [devpi](http://ml-workshop-proxy:3141) 缓存索引，首次安装从 PyPI 拉取并缓存，后续安装直接从本地读取：

```bash
pip install numpy                         # 自动使用本地缓存索引
```

配置文件：`/etc/pip/pip.conf`

```ini
[global]
index-url = http://ml-workshop-proxy:3141/root/pypi/+simple/
trusted-host = ml-workshop-proxy
```

如需临时使用官方源：

```bash
pip install --index-url https://pypi.org/simple/ <package>
```

### uv

同样配置使用本地 devpi 缓存索引：

```bash
uv pip install numpy                      # 自动使用本地缓存索引
```

通过环境变量配置：`UV_INDEX_URL=http://ml-workshop-proxy:3141/root/pypi/+simple/`

如需临时使用官方源：

```bash
UV_INDEX_URL=https://pypi.org/simple/ uv pip install <package>
```

### apt

已配置使用本地 [apt-cacher-ng](http://ml-workshop-proxy:3142) 代理仓库，所有 apt 请求自动经过缓存，相同包只下载一次：

```bash
apt-get update && apt-get install -y <package>   # 自动使用缓存代理
```

配置文件：`/etc/apt/apt.conf.d/00proxy`

```
Acquire::http::Proxy "http://ml-workshop-proxy:3142";
```

如需临时绕过缓存：

```bash
apt-get -o Acquire::http::Proxy=false update
```

### VSCode 代理设置

VSCode（浏览器版和 SSH 远程）已自动配置代理。如需手动修改，打开设置（`Ctrl+,`）搜索 `proxy`，设置：

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
- 确认容器正在运行（检查 JupyterHub）
- 向管理员确认主机地址和端口

### 扩展不同步
- 扩展存储在 `~/work/.vscode-server/extensions`
- 容器重启后会保留

### 性能较慢
- 检查到服务器的网络延迟
- 高延迟情况下建议使用浏览器方式
