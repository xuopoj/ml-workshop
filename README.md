# ML Workshop

基于 JupyterHub + DockerSpawner 的多用户机器学习工作坊环境，支持 Ascend NPU。

## 快速开始

```bash
./docker-run.sh                        # 构建镜像并启动服务
docker logs ml-workshop-hub            # 查看 Hub 日志
```

访问: http://localhost:8000

## 架构

```
docker-run.sh           # 启动脚本
jupyterhub_config.py    # Hub 配置 (DockerSpawner + NativeAuthenticator)
Dockerfile.hub          # JupyterHub 编排器
Dockerfile.proxy        # 缓存代理服务器
Dockerfile.user         # 用户容器镜像
templates/              # 自定义 JupyterHub 模板
```

### 容器

| 容器 | 说明 |
|------|------|
| `ml-workshop-hub` | JupyterHub 编排器 |
| `ml-workshop-proxy` | 缓存代理 (whistle, devpi, apt-cacher-ng) |
| `ml-workshop-user-{username}` | 用户 Jupyter 容器 (按需创建) |

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

## 预构建镜像

镜像保存在 `images/` 目录：

| 文件 | 大小 | 说明 |
|------|------|------|
| `ml-workshop-hub.tar.gz` | ~146MB | JupyterHub |
| `ml-workshop-proxy.tar.gz` | ~111MB | 缓存代理 |
| `ml-workshop-user.tar.gz` | ~5.5GB | 用户环境 (PyTorch + NPU) |

### 导出镜像

```bash
docker save ml-workshop-hub:latest | gzip > images/ml-workshop-hub.tar.gz
docker save ml-workshop-proxy:latest | gzip > images/ml-workshop-proxy.tar.gz
docker save ml-workshop-user:latest | gzip > images/ml-workshop-user.tar.gz
```

### 导入镜像

```bash
gunzip -c images/ml-workshop-hub.tar.gz | docker load
gunzip -c images/ml-workshop-proxy.tar.gz | docker load
gunzip -c images/ml-workshop-user.tar.gz | docker load
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

- `jupyterhub_config.py` → Hub 配置
- `templates/` → 自定义模板
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
