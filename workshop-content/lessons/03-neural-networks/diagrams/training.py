"""训练技巧可视化 / Training techniques visualizations

包含：初始化、归一化、正则化、优化器
"""

import numpy as np
import matplotlib.pyplot as plt


# =============================================================================
# 初始化 (Initialization)
# =============================================================================

def plot_init_distributions(methods=None):
    """
    对比不同初始化方法的权重分布

    Args:
        methods: 初始化方法列表，默认 ['zero', 'random', 'xavier', 'he']
    """
    if methods is None:
        methods = ['zero', 'random', 'xavier', 'he']

    n_weights = 1000
    fan_in, fan_out = 256, 128

    distributions = {
        'zero': np.zeros(n_weights),
        'random': np.random.randn(n_weights),
        'xavier': np.random.randn(n_weights) * np.sqrt(2.0 / (fan_in + fan_out)),
        'he': np.random.randn(n_weights) * np.sqrt(2.0 / fan_in),
    }

    n = len(methods)
    fig, axes = plt.subplots(1, n, figsize=(4 * n, 4))
    if n == 1:
        axes = [axes]

    for ax, method in zip(axes, methods):
        weights = distributions.get(method, distributions['random'])
        ax.hist(weights, bins=50, density=True, alpha=0.7, color='steelblue')
        ax.axvline(x=0, color='red', linestyle='--', linewidth=1)
        ax.set_xlabel('Weight Value', fontsize=11)
        ax.set_ylabel('Density', fontsize=11)
        ax.set_title(f'{method.upper()} Init', fontsize=12, fontweight='bold')
        ax.set_xlim(-2, 2)

    plt.tight_layout()
    plt.show()


def plot_activation_histograms(network, X, init_method='xavier'):
    """绘制每层激活值分布直方图，诊断梯度消失/爆炸"""
    # TODO: 实现逐层激活值分布图
    raise NotImplementedError


# =============================================================================
# 归一化 (Normalization)
# =============================================================================

def plot_batch_norm_effect(before, after):
    """
    对比 Batch Normalization 前后的分布

    Args:
        before: BN 前的激活值 (n_samples,)
        after: BN 后的激活值 (n_samples,)
    """
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))

    axes[0].hist(before, bins=50, density=True, alpha=0.7, color='coral')
    axes[0].axvline(x=np.mean(before), color='red', linestyle='--', label=f'mean={np.mean(before):.2f}')
    axes[0].set_xlabel('Activation Value', fontsize=11)
    axes[0].set_ylabel('Density', fontsize=11)
    axes[0].set_title('Before Batch Norm', fontsize=12, fontweight='bold')
    axes[0].legend()

    axes[1].hist(after, bins=50, density=True, alpha=0.7, color='steelblue')
    axes[1].axvline(x=np.mean(after), color='red', linestyle='--', label=f'mean={np.mean(after):.2f}')
    axes[1].set_xlabel('Activation Value', fontsize=11)
    axes[1].set_ylabel('Density', fontsize=11)
    axes[1].set_title('After Batch Norm', fontsize=12, fontweight='bold')
    axes[1].legend()

    plt.tight_layout()
    plt.show()


def plot_internal_covariate_shift():
    """可视化内部协变量偏移问题"""
    # TODO: 实现协变量偏移可视化
    raise NotImplementedError


def plot_norm_comparison():
    """
    对比 Batch Norm vs Layer Norm 的归一化方向

    呼应 2.1 节的批处理维度图，展示归一化操作的维度
    """
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    n_features = 4  # 特征数（神经元数）
    batch_size = 6  # 批量大小

    # 颜色
    color_batch = '#4ECDC4'  # 青色 - batch 方向
    color_layer = '#FF6B6B'  # 红色 - layer 方向
    color_neutral = '#E8E8E8'  # 灰色 - 未选中

    def draw_matrix(ax, title, highlight='none', highlight_idx=1):
        """绘制激活矩阵，高亮归一化方向"""
        cell_width = 0.12
        cell_height = 0.15
        start_x = 0.2
        start_y = 0.25

        for i in range(n_features):  # 行 = 特征
            for j in range(batch_size):  # 列 = 样本
                x = start_x + j * cell_width
                y = start_y + (n_features - 1 - i) * cell_height

                if highlight == 'batch' and i == highlight_idx:
                    # Batch Norm: 只高亮一行（一个特征跨所有样本）
                    color = color_batch
                elif highlight == 'layer' and j == highlight_idx:
                    # Layer Norm: 只高亮一列（一个样本跨所有特征）
                    color = color_layer
                else:
                    color = color_neutral

                rect = plt.Rectangle((x, y), cell_width * 0.9, cell_height * 0.9,
                                     facecolor=color, edgecolor='black', linewidth=1)
                ax.add_patch(rect)
                # 显示值
                ax.text(x + cell_width * 0.45, y + cell_height * 0.45,
                       f'$a_{{{i+1}}}^{{({j+1})}}$', ha='center', va='center', fontsize=8)

        # 维度标注
        ax.text(start_x + batch_size * cell_width / 2, start_y - 0.08,
               f'Batch size: m={batch_size}', ha='center', fontsize=10, color='blue')
        ax.text(start_x - 0.08, start_y + n_features * cell_height / 2,
               f'Features: n={n_features}', ha='center', va='center', fontsize=10,
               color='blue', rotation=90)

        # 矩阵标签
        ax.text(start_x + batch_size * cell_width / 2, start_y + n_features * cell_height + 0.05,
               '$A^{[l]}$: (n, m)', ha='center', fontsize=12, fontweight='bold')

        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_title(title, fontsize=12, fontweight='bold', pad=10)

    # 左图：激活矩阵
    draw_matrix(axes[0], 'Activation Matrix\n(from forward prop)', highlight='none')
    axes[0].text(0.5, 0.08, 'Each column = one sample\nEach row = one feature',
                ha='center', fontsize=9, style='italic', color='gray')

    # 中图：Batch Norm - 高亮第2行（feature index 1）
    draw_matrix(axes[1], 'Batch Normalization\nNormalize across batch (→)', highlight='batch', highlight_idx=1)
    # 添加箭头表示归一化方向（在矩阵右侧）
    row_y = 0.25 + (n_features - 1 - 1) * 0.15 + 0.075  # 第2行的y位置
    axes[1].annotate('', xy=(0.95, row_y), xytext=(0.92, row_y),
                    arrowprops=dict(arrowstyle='->', color=color_batch, lw=3))
    axes[1].text(0.97, row_y, '→', fontsize=16, ha='left', va='center', color=color_batch, fontweight='bold')
    axes[1].text(0.5, 0.08, 'For each feature (row):\ncompute $\\mu, \\sigma$ across all samples',
                ha='center', fontsize=9)

    # 右图：Layer Norm - 高亮第3列（sample index 2）
    draw_matrix(axes[2], 'Layer Normalization\nNormalize across features (↓)', highlight='layer', highlight_idx=2)
    # 添加箭头表示归一化方向（在矩阵下方）
    col_x = 0.2 + 2 * 0.12 + 0.054  # 第3列的x位置
    axes[2].annotate('', xy=(col_x, 0.18), xytext=(col_x, 0.21),
                    arrowprops=dict(arrowstyle='->', color=color_layer, lw=3))
    axes[2].text(col_x, 0.13, '↓', fontsize=16, ha='center', va='center', color=color_layer, fontweight='bold')
    axes[2].text(0.5, 0.08, 'For each sample (column):\ncompute $\\mu, \\sigma$ across all features',
                ha='center', fontsize=9)

    fig.suptitle('Batch Norm vs Layer Norm: Different normalization axes',
                fontsize=13, fontweight='bold', y=0.98)
    plt.tight_layout()
    plt.show()


# =============================================================================
# 正则化 (Regularization)
# =============================================================================

def plot_overfitting_curves(train_loss, val_loss):
    """
    绘制训练/验证损失曲线，展示过拟合

    Args:
        train_loss: 训练损失列表
        val_loss: 验证损失列表
    """
    fig, ax = plt.subplots(figsize=(8, 5))

    epochs = range(1, len(train_loss) + 1)
    ax.plot(epochs, train_loss, 'b-', linewidth=2, label='Training Loss')
    ax.plot(epochs, val_loss, 'r-', linewidth=2, label='Validation Loss')

    # 标记过拟合开始点
    if len(val_loss) > 1:
        min_val_idx = np.argmin(val_loss)
        ax.axvline(x=min_val_idx + 1, color='gray', linestyle='--', alpha=0.7,
                   label=f'Best Epoch: {min_val_idx + 1}')

    ax.set_xlabel('Epoch', fontsize=12)
    ax.set_ylabel('Loss', fontsize=12)
    ax.set_title('Training vs Validation Loss', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


def plot_dropout_network(drop_prob=0.5):
    """
    可视化 Dropout：显示被丢弃的连接

    Args:
        drop_prob: 丢弃概率
    """
    np.random.seed(42)
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    layers = [4, 6, 6, 3]

    for ax_idx, (ax, title, show_dropout) in enumerate(zip(
        axes,
        ['Without Dropout (Inference)', f'With Dropout (Training, p={drop_prob})'],
        [False, True]
    )):
        n_layers = len(layers)

        # 决定哪些神经元被丢弃
        dropped = {}
        if show_dropout:
            for i, n in enumerate(layers[1:-1], start=1):  # 不丢弃输入和输出层
                dropped[i] = np.random.rand(n) < drop_prob

        # 绘制神经元和连接
        for i, n_neurons in enumerate(layers):
            x = i / (n_layers - 1)
            y_positions = np.linspace(0.15, 0.85, n_neurons)

            for j, y in enumerate(y_positions):
                # 判断是否被丢弃
                is_dropped = show_dropout and i in dropped and dropped[i][j]

                # 绘制连接到下一层
                if i < n_layers - 1:
                    next_n = layers[i + 1]
                    next_x = (i + 1) / (n_layers - 1)
                    next_y_positions = np.linspace(0.15, 0.85, next_n)

                    for k, next_y in enumerate(next_y_positions):
                        next_dropped = show_dropout and (i + 1) in dropped and dropped[i + 1][k]
                        if is_dropped or next_dropped:
                            # 被丢弃的连接用虚线
                            ax.plot([x + 0.03, next_x - 0.03], [y, next_y],
                                    color='lightgray', linewidth=0.5, linestyle=':', alpha=0.3)
                        else:
                            ax.plot([x + 0.03, next_x - 0.03], [y, next_y],
                                    color='gray', linewidth=0.5, alpha=0.5)

                # 绘制神经元
                if is_dropped:
                    circle = plt.Circle((x, y), 0.025, color='lightgray',
                                         ec='gray', linewidth=1, linestyle='--')
                    ax.text(x, y, '×', ha='center', va='center', fontsize=10, color='red')
                else:
                    circle = plt.Circle((x, y), 0.025, color='steelblue', ec='black', linewidth=1)
                ax.add_patch(circle)

        ax.set_xlim(-0.1, 1.1)
        ax.set_ylim(0, 1)
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_title(title, fontsize=12, fontweight='bold')

    fig.suptitle('Dropout: Randomly "dropping" neurons during training prevents co-adaptation',
                 fontsize=11, style='italic', y=0.02)
    plt.tight_layout()
    plt.show()


def plot_l2_regularization_effect():
    """可视化 L2 正则化对权重的影响"""
    # TODO: 实现 L2 正则化效果图
    raise NotImplementedError


# =============================================================================
# 优化器 (Optimizers)
# =============================================================================

def plot_optimizer_comparison(optimizers=None):
    """对比不同优化器的收敛路径"""
    # TODO: 实现优化器对比图
    raise NotImplementedError


def plot_momentum_visualization():
    """
    可视化动量：对比 SGD vs SGD+Momentum 的优化路径

    展示动量如何帮助加速收敛和穿越平坦区域
    """
    np.random.seed(42)
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # 创建一个细长的椭圆形损失曲面（模拟病态条件数）
    def loss_fn(w1, w2):
        return 0.1 * w1**2 + 2 * w2**2  # 椭圆形：w2 方向更陡

    # 生成等高线数据
    w1_range = np.linspace(-3, 3, 100)
    w2_range = np.linspace(-2, 2, 100)
    W1, W2 = np.meshgrid(w1_range, w2_range)
    Z = loss_fn(W1, W2)

    # SGD 路径（无动量）
    def sgd_path(start, lr=0.1, steps=30):
        path = [start]
        w = np.array(start, dtype=float)
        for _ in range(steps):
            grad = np.array([0.2 * w[0], 4 * w[1]])  # 梯度
            w = w - lr * grad
            path.append(w.copy())
        return np.array(path)

    # SGD + Momentum 路径
    def momentum_path(start, lr=0.1, beta=0.9, steps=30):
        path = [start]
        w = np.array(start, dtype=float)
        v = np.zeros(2)  # 速度
        for _ in range(steps):
            grad = np.array([0.2 * w[0], 4 * w[1]])
            v = beta * v + (1 - beta) * grad  # 更新速度
            w = w - lr * v
            path.append(w.copy())
        return np.array(path)

    start = np.array([2.5, 1.5])

    # 左图：SGD
    ax = axes[0]
    ax.contour(W1, W2, Z, levels=15, cmap='Blues', alpha=0.7)
    path_sgd = sgd_path(start, lr=0.3, steps=25)
    ax.plot(path_sgd[:, 0], path_sgd[:, 1], 'ro-', markersize=4, linewidth=1.5, label='SGD path')
    ax.plot(start[0], start[1], 'go', markersize=10, label='Start')
    ax.plot(0, 0, 'g*', markersize=15, label='Optimum')
    ax.set_xlabel('$w_1$', fontsize=12)
    ax.set_ylabel('$w_2$', fontsize=12)
    ax.set_title('SGD (no momentum)\nOscillates in steep direction', fontsize=12, fontweight='bold')
    ax.legend(loc='upper right', fontsize=9)
    ax.set_xlim(-3, 3)
    ax.set_ylim(-2, 2)
    ax.set_aspect('equal')

    # 右图：SGD + Momentum
    ax = axes[1]
    ax.contour(W1, W2, Z, levels=15, cmap='Blues', alpha=0.7)
    path_mom = momentum_path(start, lr=0.3, beta=0.9, steps=25)
    ax.plot(path_mom[:, 0], path_mom[:, 1], 'ro-', markersize=4, linewidth=1.5, label='Momentum path')
    ax.plot(start[0], start[1], 'go', markersize=10, label='Start')
    ax.plot(0, 0, 'g*', markersize=15, label='Optimum')
    ax.set_xlabel('$w_1$', fontsize=12)
    ax.set_ylabel('$w_2$', fontsize=12)
    ax.set_title('SGD + Momentum (β=0.9)\nSmooths oscillations, faster convergence', fontsize=12, fontweight='bold')
    ax.legend(loc='upper right', fontsize=9)
    ax.set_xlim(-3, 3)
    ax.set_ylim(-2, 2)
    ax.set_aspect('equal')

    fig.suptitle('Momentum: $v_t = βv_{t-1} + (1-β)∇L$,  $w = w - αv_t$',
                 fontsize=11, y=0.02, style='italic')
    plt.tight_layout()
    plt.show()


def plot_learning_rate_schedule(schedule='cosine'):
    """
    绘制学习率调度曲线

    Args:
        schedule: 调度类型 ('step', 'cosine', 'exponential')
    """
    epochs = 100
    initial_lr = 0.1
    x = np.arange(epochs)

    schedules = {
        'step': initial_lr * (0.1 ** (x // 30)),
        'cosine': initial_lr * 0.5 * (1 + np.cos(np.pi * x / epochs)),
        'exponential': initial_lr * (0.95 ** x),
    }

    lr = schedules.get(schedule, schedules['cosine'])

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(x, lr, linewidth=2)
    ax.set_xlabel('Epoch', fontsize=12)
    ax.set_ylabel('Learning Rate', fontsize=12)
    ax.set_title(f'{schedule.upper()} Learning Rate Schedule', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()
