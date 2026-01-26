# ModelScope CLI 使用指南

## 安装

```bash
pip install modelscope
```

## 登录

```bash
modelscope login
# 输入你的 Access Token，获取地址：https://modelscope.cn/my/myaccesstoken
```

---

## 上传 (Upload)

### 命令格式

```bash
modelscope upload <repo_id> [local_path] [path_in_repo]
```

- `repo_id`: 仓库 ID，格式为 `username/repo-name`
- `local_path`: 本地文件或文件夹路径（默认当前目录）
- `path_in_repo`: 仓库中的目标路径（默认与本地路径相同）

### 常用选项

| 选项 | 说明 |
|------|------|
| `--repo-type {model,dataset}` | 仓库类型，默认 `model` |
| `--include` | 匹配要上传的文件（glob 模式） |
| `--exclude` | 排除不上传的文件（glob 模式） |
| `--commit-message` | 提交信息 |
| `--max-workers` | 并行上传的线程数 |

### 示例

```bash
# 上传整个文件夹
modelscope upload xuopoj/ascend-factory ./model_files

# 上传单个文件
modelscope upload xuopoj/ascend-factory ./weights.bin weights.bin

# 上传文件夹到仓库指定路径
modelscope upload xuopoj/ascend-factory ./local_dir remote_dir

# 指定提交信息
modelscope upload xuopoj/ascend-factory ./model --commit-message "Add model weights"

# 排除某些文件
modelscope upload xuopoj/ascend-factory ./model --exclude "*.log" "*.tmp"

# 后台上传大文件
nohup modelscope upload xuopoj/ascend-factory ./large_file.tar.gz > upload.log 2>&1 &
tail -f upload.log
```

### this project

```bash
modelscope upload xuopoj/ascend-factory  ml-workshop-user.tar.gz images/
```
---

## 下载 (Download)

### 命令格式

```bash
modelscope download [repo_id] [files...]
```

### 常用选项

| 选项 | 说明 |
|------|------|
| `--model MODEL` | 模型仓库 ID |
| `--dataset DATASET` | 数据集仓库 ID |
| `--local_dir` | 下载到指定本地目录 |
| `--cache_dir` | 缓存目录 |
| `--include` | 匹配要下载的文件（glob 模式） |
| `--exclude` | 排除不下载的文件（glob 模式） |
| `--revision` | 指定版本/分支 |
| `--max-workers` | 并行下载的线程数 |

### 示例

```bash
# 下载整个模型仓库到指定目录
modelscope download --model xuopoj/ascend-factory --local_dir ./models

# 简写形式
modelscope download xuopoj/ascend-factory --local_dir ./models

# 下载到缓存目录（会自动管理）
modelscope download --model xuopoj/ascend-factory --cache_dir ./cache

# 下载单个文件
modelscope download xuopoj/ascend-factory config.json

# 下载多个指定文件
modelscope download xuopoj/ascend-factory config.json model.safetensors

# 使用 glob 模式下载
modelscope download xuopoj/ascend-factory --include "*.json" "*.safetensors"

# 排除大文件
modelscope download xuopoj/ascend-factory --exclude "*.bin"

# 下载数据集
modelscope download --dataset username/my-dataset --local_dir ./data
```

---

## 其他命令

```bash
# 查看缓存
modelscope scan-cache

# 清理缓存
modelscope clear-cache

# 查看帮助
modelscope --help
modelscope upload --help
modelscope download --help
```

---

## 示例：上传和下载 Docker 镜像

### 创建仓库

在 ModelScope 网页上创建模型仓库：https://modelscope.cn/models/create

### 上传镜像

```bash
# 导出 Docker 镜像
docker save ml-workshop-hub | gzip > images/ml-workshop-hub.tar.gz
docker save ml-workshop-user | gzip > images/ml-workshop-user.tar.gz

# 上传到 ModelScope
modelscope upload username/ml-workshop-images ./images
```

### 下载镜像

```bash
# 下载全部
modelscope download username/ml-workshop-images --local_dir ./images

# 下载单个文件
modelscope download username/ml-workshop-images ml-workshop-hub.tar.gz --local_dir ./images
```

### 加载镜像

```bash
gunzip -c images/ml-workshop-hub.tar.gz | docker load
gunzip -c images/ml-workshop-user.tar.gz | docker load

# 验证
docker images | grep ml-workshop
```
