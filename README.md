# ML Workshop

基于 JupyterHub + DockerSpawner 的多用户机器学习工作坊环境，支持 Ascend NPU。

## 快速开始

```bash
./start-docker.sh                      # 启动所有容器
docker logs ml-workshop-hub            # 查看 Hub 日志
docker stop ml-workshop-hub ml-workshop-proxy && docker rm ml-workshop-hub ml-workshop-proxy  # 停止
```

访问: http://localhost:28000


## 架构

```
start-docker.sh              # 启动脚本
hub/                         # JupyterHub 编排器
├── Dockerfile
├── jupyterhub_config.py     # Hub 配置 (DockerSpawner + NativeAuthenticator)
└── templates/               # 自定义 JupyterHub 模板
proxy/                       # 缓存代理服务器
├── Dockerfile
├── start.sh
└── supervisord.conf
user/                        # 用户容器镜像
├── Dockerfile
├── start-notebook.sh
├── start-vscode.sh
└── getstarted.md
openclaw/                    # OpenClaw 容器
├── Dockerfile
├── start.sh
├── openclaw.json
└── getting-started.md
hcie/                        # HCIE Ascend NPU 容器
├── Dockerfile
├── entrypoint.sh
├── requirements-env0.txt
└── requirements-env1.txt
```

### 容器

| 容器 | 说明 |
|------|------|
| `ml-workshop-hub` | JupyterHub 编排器 |
| `ml-workshop-proxy` | 缓存代理 (whistle, devpi, apt-cacher-ng) |
| `ml-workshop-user-{username}` | 用户 Jupyter 容器 (按需创建) |
| `ml-workshop-hcie` | HCIE Ascend NPU 环境 (conda + env0/env1) |

### 目录结构

```
workshop-content/       # 工作坊内容 (挂载到用户容器)
├── lessons/           # 课程材料
├── datasets/          # 共享数据集
└── models/            # 共享模型

student-work/          # 学生作业目录
└── {username}/        # 每个学生的独立目录
```

## 用户管理

使用 NativeAuthenticator，需要管理员审批：

1. 用户在 `/hub/signup` 注册
2. 管理员在 `/hub/authorize` 审批
3. 审批后用户可登录

默认管理员: `superuser`

### SSH 连接 (VS Code Remote)

每个用户容器自动启动 SSH 服务，端口从 22222 开始递增分配。

```
Host: <VSCODE_SSH_HOST>
Port: 22222+
User: root
Password: 首次启动自动生成（见容器日志），重启后自动恢复，可运行 passwd 修改
```

## 预构建镜像

通过 [ModelScope](https://modelscope.cn) 分发预构建镜像。

### 上传镜像

```bash
# 导出 + 上传
docker save ml-workshop-hub:latest | gzip > ml-workshop-hub.tar.gz
docker save ml-workshop-proxy:latest | gzip > ml-workshop-proxy.tar.gz
docker save ml-workshop-user:latest | gzip > ml-workshop-user.tar.gz
docker save ml-workshop-openclaw:latest | gzip > ml-workshop-openclaw.tar.gz
docker save ml-workshop-hcie:latest | gzip > ml-workshop-hcie.tar.gz

modelscope upload xuopoj/ascend-factory ml-workshop-hub.tar.gz ml-workshop/ml-workshop-hub.tar.gz
modelscope upload xuopoj/ascend-factory ml-workshop-proxy.tar.gz ml-workshop/ml-workshop-proxy.tar.gz
modelscope upload xuopoj/ascend-factory ml-workshop-user.tar.gz ml-workshop/ml-workshop-user.tar.gz
modelscope upload xuopoj/ascend-factory ml-workshop-openclaw.tar.gz ml-workshop/ml-workshop-openclaw.tar.gz
modelscope upload xuopoj/ascend-factory ml-workshop-hcie.tar.gz ml-workshop/ml-workshop-hcie.tar.gz
```

### 下载镜像

```bash
modelscope download xuopoj/ascend-factory ml-workshop/ml-workshop-hub.tar.gz --local_dir ./
modelscope download xuopoj/ascend-factory ml-workshop/ml-workshop-proxy.tar.gz --local_dir ./
modelscope download xuopoj/ascend-factory ml-workshop/ml-workshop-user.tar.gz --local_dir ./
modelscope download xuopoj/ascend-factory ml-workshop/ml-workshop-openclaw.tar.gz --local_dir ./
modelscope download xuopoj/ascend-factory ml-workshop/ml-workshop-hcie.tar.gz --local_dir ./

# 导入
gunzip -c ml-workshop/ml-workshop-hub.tar.gz | docker load
gunzip -c ml-workshop/ml-workshop-proxy.tar.gz | docker load
gunzip -c ml-workshop/ml-workshop-user.tar.gz | docker load
gunzip -c ml-workshop/ml-workshop-openclaw.tar.gz | docker load
gunzip -c ml-workshop/ml-workshop-hcie.tar.gz | docker load
```

## NPU 配置

通过环境变量启用 Ascend NPU：

```bash
# 挂载指定 NPU
ASCEND_VISIBLE_DEVICES=0,1 ./docker-run.sh

# 挂载所有 NPU (0-7)
ASCEND_VISIBLE_DEVICES=all ./docker-run.sh
```

## 开发模式

本地文件自动挂载到容器（如果存在）：

- `hub/jupyterhub_config.py` → Hub 配置
- `hub/templates/` → 自定义模板
- `workshop-content/` → 工作坊内容
- `student-work/` → 学生作业

修改配置后重启 Hub：

```bash
docker restart ml-workshop-hub
```

## 常用命令

```bash
# 查看日志
docker logs -f ml-workshop-hub
docker logs -f ml-workshop-proxy

# 停止服务
docker stop ml-workshop-hub ml-workshop-proxy
docker rm ml-workshop-hub ml-workshop-proxy

# 重建并启动
./docker-run.sh
```

## 代理配置

Whistle 代理 UI: http://localhost:8900

用于配置上游代理，支持离线环境。
