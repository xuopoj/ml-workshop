# VSCode 远程开发环境配置

使用本地 VSCode 连接到研讨会的远程开发容器。


## 方式一：浏览器访问（最简单）

| 服务 | 地址 |
|------|------|
| VSCode (浏览器) | `http://VSCODE_SSH_HOST_PLACEHOLDER:28000/user/JUPYTERHUB_USER_PLACEHOLDER/vscode/?folder=/home/VSCODE_USER_PLACEHOLDER/work` |
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

远程环境已预配置以下代理：

| 服务 | 地址 |
|------|------|
| HTTP/HTTPS 代理 | `http://ml-workshop-proxy:8899` |
| pip 缓存 | `http://ml-workshop-proxy:3141` |
| apt 缓存 | `http://ml-workshop-proxy:3142` |

环境变量已自动设置。如需为其他工具配置：

```bash
export HTTP_PROXY=http://ml-workshop-proxy:8899
export HTTPS_PROXY=http://ml-workshop-proxy:8899
export NO_PROXY=localhost,127.0.0.1,ml-workshop-hub,ml-workshop-proxy
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
