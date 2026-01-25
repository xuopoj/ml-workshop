# ML Workshop - JupyterHub 多用户环境

基于 JupyterHub 的多用户机器学习/深度学习工作坊环境，支持 NativeAuthenticator 身份验证和 Ascend NPU。用户账户持久化存储在数据库中，镜像更新不会丢失数据。

## 功能特性

- **持久化用户账户**: 用户存储在数据库中，镜像更新后账户依然存在
- **管理员功能**: 管理员可通过 Web 界面创建用户、提升权限
- **NPU 共享**: 所有用户共享所有可用的 Ascend NPU 设备
- **共享资源**: 课程、数据集、模型等资源供所有用户访问
- **用户工作空间**: 每个用户拥有独立的工作空间和私有目录
- **JupyterLab**: 现代化的 Web IDE，支持丰富的扩展
- **预装库**: PyTorch、Transformers、LangChain 等常用库
- **自动清理**: 空闲 2 小时后自动停止服务器释放资源

## 系统架构

### 身份验证 - NativeAuthenticator

用户存储在 **JupyterHub 数据库** (`jupyterhub.sqlite`) 中，而非系统用户：
- 用户账户在容器更新/重启后依然保留
- 所有 notebook 服务器以 **root 用户**运行（用于访问 NPU 设备）
- 用户隔离在 JupyterHub 数据库层面实现
- 用户工作空间存储在 `/opt/jupyterhub/users/{username}`

### 共享目录结构

- `/opt/workshop/lessons` - 课程材料（学生只读）
- `/opt/workshop/datasets` - 共享数据集（学生只读）
- `/opt/workshop/models` - 共享模型（学生只读）
- `/opt/workshop/student-work` - 学生作业提交目录（管理员可浏览）

### 用户工作空间

每个用户的工作空间位于 `/opt/jupyterhub/users/{username}`，包含：
- `lessons/` - 指向共享课程的符号链接
- `datasets/` - 指向共享数据集的符号链接
- `models/` - 指向共享模型的符号链接
- `work/` - 用户的私有工作目录
- `student-work/` - （仅管理员）指向学生作业的符号链接

### 用户角色

- **管理员 (superuser)**: 完全控制权限，可管理所有用户和服务器
- **普通用户**: 独立工作空间，对共享资源有读取权限

### NPU 配置

- **共享模式**: 所有用户共享所有可用的 NPU 设备
- **自动分配**: 通过 `NPU_COUNT` 环境变量配置 NPU 数量
- **环境变量**: 自动为所有用户设置 `ASCEND_RT_VISIBLE_DEVICES`
- **权限要求**: 所有 notebook 服务器以 root 用户运行以访问 NPU 设备

例如，如果有 4 个 NPU：
- 所有用户的 `ASCEND_RT_VISIBLE_DEVICES=0,1,2,3`
- 用户可以同时使用所有 NPU 进行计算
- Notebook 进程以 root 权限运行（Ascend NPU 设备访问要求）

## 前置要求

1. **Docker**: Docker Engine 20.10+
2. **Docker Compose**: v2.0+
3. **NPU 驱动** (可选): 主机安装 Ascend 驱动程序
4. **镜像构建**: 已构建 `ml-workshop:latest` 镜像

## 快速开始

### 1. 构建镜像

```bash
docker build -t ml-workshop:latest .
```

### 2. 准备工作坊材料

创建并填充工作坊目录：

```bash
# 创建目录
mkdir -p lessons datasets models student-work

# 添加你的工作坊材料
cp -r /path/to/your/lessons/* lessons/
cp -r /path/to/your/datasets/* datasets/
cp -r /path/to/your/models/* models/
```

### 3. 配置 NPU 数量

编辑 `docker-compose.yml`，根据可用 NPU 数量调整 `NPU_COUNT`：

```yaml
environment:
  - NPU_COUNT=4  # 设置为系统的 NPU 数量（如果没有则设为 0）
```

**NPU 设备挂载**：
- 如果有 NPU，取消注释 `docker-compose.yml` 中的设备挂载行
- 如果在 Mac 或无 NPU 环境，保持设备挂载注释状态

### 4. 启动 JupyterHub

```bash
docker compose up -d
```

### 5. 创建管理员账户（首次启动）

首次启动时需要创建管理员账户：

1. 浏览器打开 http://localhost:8000
2. 点击 "Sign up"（登录表单下方）
3. 创建用户名为 `superuser` 的账户，设置强密码（至少 8 位）
4. 该账户会自动提升为管理员

### 6. 管理员：创建用户账户

以管理员身份登录后，可以创建用户账户：

#### 方式一：通过管理面板（推荐）

1. 点击顶部导航栏的 "Admin"
2. 点击 "Add Users" 按钮
3. 输入用户名，每行一个
4. 点击 "Add Users"
5. 为用户设置密码（用户之后可以修改）

#### 方式二：用户自助注册

用户可以自行创建账户：
1. 访问 http://localhost:8000
2. 点击 "Sign up"
3. 输入用户名和密码（至少 8 位）
4. 账户立即创建（无需审批）

**注意**：如需禁用自助注册并要求管理员审批，编辑 `jupyterhub_config.py`：
```python
c.NativeAuthenticator.open_signup = False
```

## 用户管理

### 提升用户为管理员

1. 以管理员身份登录
2. 进入 Admin 面板
3. 在列表中找到用户
4. 勾选用户旁边的 "Admin" 复选框
5. 用户现在拥有管理员权限

### 删除用户

1. 进入 Admin 面板
2. 在列表中找到用户
3. 点击 "Delete" 按钮
4. **注意**：这会删除用户账户，但不会删除其工作空间文件

### 重置用户密码

管理员可通过管理面板重置密码：
1. 进入 Admin 面板
2. 点击 "Edit User" 按钮
3. 设置新密码

用户可自行修改密码：
1. 点击用户名下拉菜单（右上角）
2. 选择 "Change Password"
3. 输入当前密码和新密码

### 查看用户服务器

管理面板显示：
- 所有用户及其服务器状态
- 启动/停止任何用户的服务器
- 访问用户服务器（用于故障排查）

## 镜像更新

更新 ml-workshop 镜像时，用户数据会保留：

```bash
# 1. 停止容器
docker compose down

# 2. 使用新更改重新构建镜像
docker build -t ml-workshop:latest .

# 3. 使用更新后的镜像启动
docker compose up -d
```

**会保留的内容：**
✅ 用户账户和密码
✅ 用户工作空间文件
✅ 管理员设置

**不会保留的内容：**
❌ 用户环境中安装的 Python 包（需要重新安装）
❌ 容器内的系统级更改

## 运维管理

### 查看日志

```bash
# 查看 JupyterHub 日志
docker compose logs -f jupyterhub

# 查看最近 100 行日志
docker compose logs --tail=100 jupyterhub
```

### 停止 JupyterHub

```bash
docker compose down
```

### 重启 JupyterHub

```bash
docker compose restart
```

### 备份用户数据

```bash
# 备份所有数据（用户账户 + 工作空间）
docker run --rm -v jupyterhub-data:/data -v $(pwd):/backup \
  alpine tar czf /backup/jupyterhub-backup-$(date +%Y%m%d).tar.gz -C /data .
```

### 恢复用户数据

```bash
# 从备份恢复
docker run --rm -v jupyterhub-data:/data -v $(pwd):/backup \
  alpine sh -c "cd /data && tar xzf /backup/jupyterhub-backup-YYYYMMDD.tar.gz"
```

### 导出用户列表

```bash
docker exec -it ml-workshop-jupyterhub sqlite3 /opt/jupyterhub/jupyterhub.sqlite \
  "SELECT name, admin, created FROM users;"
```

## 管理功能

### 管理面板

访问管理面板：http://localhost:8000/hub/admin

可以执行的操作：
- 查看所有用户及其服务器
- 启动/停止用户服务器
- 添加新用户
- 删除用户
- 提升用户为管理员
- 访问任何用户的服务器

### NPU 使用查看

查看 NPU 配置：

```bash
docker exec ml-workshop-jupyterhub python3 -c "
import os
npu_count = int(os.environ.get('NPU_COUNT', '0'))
if npu_count > 0:
    npu_list = ','.join(str(i) for i in range(npu_count))
    print(f'NPU 数量: {npu_count}')
    print(f'所有用户共享的 NPU: {npu_list}')
    print(f'ASCEND_RT_VISIBLE_DEVICES={npu_list}')
else:
    print('未配置 NPU')
"
```

## 配置自定义

### 修改资源限制

编辑 `jupyterhub_config.py`：

```python
# CPU 限制（核心数）
c.Spawner.cpu_limit = 4

# 内存限制
c.Spawner.mem_limit = '8G'
```

### 修改空闲超时时间

编辑 `jupyterhub_config.py`：

```python
c.JupyterHub.services = [
    {
        'name': 'idle-culler',
        'admin': True,
        'command': [
            sys.executable,
            '-m', 'jupyterhub_idle_culler',
            '--timeout=7200',  # 修改为所需的秒数
        ],
    }
]
```

### 禁用自助注册

编辑 `jupyterhub_config.py`：

```python
# 要求管理员审批新注册
c.NativeAuthenticator.open_signup = False
```

### 修改密码要求

编辑 `jupyterhub_config.py`：

```python
# 最小密码长度
c.NativeAuthenticator.minimum_password_length = 12

# 检查常见密码
c.NativeAuthenticator.check_common_password = True
```

### 修改 NPU 共享配置

编辑 `docker-compose.yml` 中的环境变量：

```yaml
environment:
  - NPU_COUNT=4  # 改为实际的 NPU 数量
```

所有用户会自动共享所有 NPU（`ASCEND_RT_VISIBLE_DEVICES=0,1,2,3`）。

## 故障排查

### 无法以 Superuser 登录

`superuser` 账户必须在首次访问时通过注册创建：
1. 访问 http://localhost:8000
2. 点击 "Sign up"
3. 创建用户名为 `superuser` 的账户
4. 会自动提升为管理员

### 用户服务器无法启动

1. 检查 spawner 日志：
```bash
docker compose logs jupyterhub | grep -i spawn
```

2. 验证用户工作空间是否存在：
```bash
docker exec -it ml-workshop-jupyterhub ls -la /opt/jupyterhub/users/
```

3. 检查磁盘空间：
```bash
docker exec -it ml-workshop-jupyterhub df -h
```

### NPU 未分配

1. 验证 NPU 设备是否已挂载：
```bash
docker exec -it ml-workshop-jupyterhub ls -l /dev/davinci*
```

2. 检查 NPU_COUNT 环境变量：
```bash
docker exec -it ml-workshop-jupyterhub env | grep NPU
```

3. 检查启动日志：
```bash
docker compose logs jupyterhub | grep -i npu
```

### 数据库损坏

如果数据库损坏：

```bash
# 停止容器
docker compose down

# 删除损坏的数据库（这会删除所有用户！）
docker run --rm -v jupyterhub-data:/data alpine rm /data/jupyterhub.sqlite

# 重启（会创建新数据库）
docker compose up -d
```

**注意**：这会删除所有用户账户，但不会删除用户工作空间文件。

### 重置所有数据

```bash
# 停止并移除所有内容
docker compose down

# 删除所有数据（用户 + 工作空间）
docker volume rm jupyterhub-data

# 全新启动
docker compose up -d
```

## 安全注意事项

1. **更改默认管理员**: 为 superuser 账户设置强密码
2. **使用 HTTPS**: 生产环境配置 SSL 证书
3. **网络隔离**: 使用防火墙规则限制访问
4. **定期更新**: 保持镜像和依赖项更新
5. **定期备份**: 定期备份 `jupyterhub-data` 卷
6. **用户隔离**: 注意所有用户以 **root 用户**运行（为访问 NPU 设备所需，OS 级隔离有限）
7. **NPU 访问**: 在 Ascend 服务器上需要 root 权限访问 NPU 设备

## 高级配置

### 启用 HTTPS

1. 生成 SSL 证书（或使用 Let's Encrypt）
2. 编辑 `jupyterhub_config.py`：

```python
c.JupyterHub.bind_url = 'https://0.0.0.0:443'
c.JupyterHub.ssl_cert = '/etc/jupyterhub/cert.pem'
c.JupyterHub.ssl_key = '/etc/jupyterhub/key.pem'
```

3. 在 docker-compose.yml 中挂载证书：
```yaml
volumes:
  - ./certs:/etc/jupyterhub/certs:ro
```

4. 更新 docker-compose.yml 中的端口映射以暴露 443

### 外部数据库（PostgreSQL）

生产环境建议使用 PostgreSQL 替代 SQLite：

1. 设置 PostgreSQL 服务器
2. 编辑 `jupyterhub_config.py`：

```python
c.JupyterHub.db_url = 'postgresql://user:password@host:5432/jupyterhub'
```

### 自定义身份验证

使用其他认证方式替代 NativeAuthenticator：

- **OAuth** (GitHub, Google 等): 安装 `oauthenticator`
- **LDAP**: 安装 `jupyterhub-ldapauthenticator`
- **自定义**: 继承 `Authenticator` 类

## 课程材料

本工作坊包含 4 节课程：

1. **机器学习基础** (`lessons/01-ml-fundamentals/`)
   - 机器学习概念和分类
   - 监督学习、无监督学习、强化学习
   - 分类 vs 回归

2. **神经网络与深度学习** (`lessons/02-neural-networks/`)
   - 感知机和神经元
   - 反向传播算法
   - MNIST 手写数字识别实战

3. **Transformer 架构** (`lessons/03-transformer-architecture/`)
   - Self-Attention 机制
   - Multi-Head Attention
   - 位置编码、Layer Normalization
   - Mixture of Experts (MoE)

4. **主流大语言模型** (`lessons/04-llm-overview/`)
   - GPT、LLaMA、Qwen 系列
   - 思考模型（DeepSeek-R1、QwQ）
   - 代码模型、多模态模型
   - 模型选择指南

所有课程均为中文 Jupyter Notebook，包含理论讲解、代码示例和可视化。

## 许可证

查看父项目的许可证信息。

## 支持

遇到问题时：
1. 查看上方的故障排查部分
2. 检查 JupyterHub 日志
3. 参考 JupyterHub 官方文档: https://jupyterhub.readthedocs.io
4. NativeAuthenticator 文档: https://native-authenticator.readthedocs.io
