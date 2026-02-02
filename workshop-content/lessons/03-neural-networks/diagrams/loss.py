"""损失函数与优化可视化 / Loss function and optimization visualizations"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


def plot_loss_landscape(w_range=(-2, 2), b_range=(-2, 2), loss_fn=None):
    """
    绘制 3D 损失曲面

    Args:
        w_range: 权重范围 (min, max)
        b_range: 偏置范围 (min, max)
        loss_fn: 损失函数 loss_fn(w, b) -> scalar，默认使用示例函数
    """
    if loss_fn is None:
        # 示例损失函数：简单的二次函数
        loss_fn = lambda w, b: w**2 + b**2 + 0.5 * w * b

    w = np.linspace(w_range[0], w_range[1], 50)
    b = np.linspace(b_range[0], b_range[1], 50)
    W, B = np.meshgrid(w, b)
    L = np.vectorize(loss_fn)(W, B)

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    ax.plot_surface(W, B, L, cmap='viridis', alpha=0.8)
    ax.set_xlabel('w', fontsize=12)
    ax.set_ylabel('b', fontsize=12)
    ax.set_zlabel('Loss', fontsize=12)
    ax.set_title('Loss Landscape', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.show()


def plot_loss_contour(w_range=(-2, 2), b_range=(-2, 2), loss_fn=None, path=None):
    """
    绘制损失等高线图

    Args:
        w_range: 权重范围
        b_range: 偏置范围
        loss_fn: 损失函数
        path: 可选的优化路径 [(w0, b0), (w1, b1), ...]
    """
    if loss_fn is None:
        loss_fn = lambda w, b: w**2 + b**2 + 0.5 * w * b

    w = np.linspace(w_range[0], w_range[1], 100)
    b = np.linspace(b_range[0], b_range[1], 100)
    W, B = np.meshgrid(w, b)
    L = np.vectorize(loss_fn)(W, B)

    fig, ax = plt.subplots(figsize=(8, 6))
    contour = ax.contour(W, B, L, levels=20, cmap='viridis')
    ax.clabel(contour, inline=True, fontsize=8)

    # 绘制优化路径
    if path is not None:
        path = np.array(path)
        ax.plot(path[:, 0], path[:, 1], 'ro-', markersize=4, linewidth=1.5, label='Optimization Path')
        ax.plot(path[0, 0], path[0, 1], 'go', markersize=10, label='Start')
        ax.plot(path[-1, 0], path[-1, 1], 'r*', markersize=15, label='End')
        ax.legend()

    ax.set_xlabel('w', fontsize=12)
    ax.set_ylabel('b', fontsize=12)
    ax.set_title('Loss Contour', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.show()


def plot_gradient_descent_path(history):
    """
    绘制梯度下降优化轨迹

    Args:
        history: 优化历史 {'w': [...], 'b': [...], 'loss': [...]}
    """
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # 损失曲线
    axes[0].plot(history['loss'], linewidth=2)
    axes[0].set_xlabel('Iteration', fontsize=12)
    axes[0].set_ylabel('Loss', fontsize=12)
    axes[0].set_title('Loss Curve', fontsize=14, fontweight='bold')
    axes[0].grid(True, alpha=0.3)

    # 参数轨迹
    axes[1].plot(history['w'], label='w', linewidth=2)
    axes[1].plot(history['b'], label='b', linewidth=2)
    axes[1].set_xlabel('Iteration', fontsize=12)
    axes[1].set_ylabel('Parameter Value', fontsize=12)
    axes[1].set_title('Parameter Trajectory', fontsize=14, fontweight='bold')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()


def plot_loss_comparison():
    """
    对比 MSE 与交叉熵损失

    展示当真实标签 y=1 时，两种损失函数随预测值变化的曲线
    """
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    y_pred = np.linspace(0.001, 0.999, 200)

    # 左图：y=1 时的损失曲线
    ax = axes[0]
    y_true = 1

    # MSE: (y_pred - y_true)^2
    mse = (y_pred - y_true) ** 2

    # Cross-entropy: -[y*log(p) + (1-y)*log(1-p)]
    # 当 y=1 时：-log(p)
    ce = -np.log(y_pred)

    ax.plot(y_pred, mse, 'b-', linewidth=2.5, label='MSE: $(\\hat{y} - 1)^2$')
    ax.plot(y_pred, ce, 'r-', linewidth=2.5, label='Cross-Entropy: $-\\log(\\hat{y})$')

    ax.set_xlabel('Prediction $\\hat{y}$', fontsize=12)
    ax.set_ylabel('Loss', fontsize=12)
    ax.set_title('Loss when True Label $y = 1$', fontsize=14, fontweight='bold')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 5)
    ax.axvline(x=1, color='green', linestyle='--', alpha=0.5, label='Target')
    ax.legend(loc='upper left', fontsize=10)
    ax.grid(True, alpha=0.3)

    # 添加说明
    ax.annotate('CE penalizes\nconfident wrong\npredictions heavily',
                xy=(0.1, 2.3), fontsize=9, color='red', ha='center')
    ax.annotate('MSE has\nsmall gradient\nnear 0',
                xy=(0.15, 0.8), fontsize=9, color='blue', ha='center')

    # 右图：y=0 时的损失曲线
    ax = axes[1]
    y_true = 0

    # MSE: (y_pred - 0)^2 = y_pred^2
    mse = y_pred ** 2

    # Cross-entropy 当 y=0 时：-log(1-p)
    ce = -np.log(1 - y_pred)

    ax.plot(y_pred, mse, 'b-', linewidth=2.5, label='MSE: $\\hat{y}^2$')
    ax.plot(y_pred, ce, 'r-', linewidth=2.5, label='Cross-Entropy: $-\\log(1-\\hat{y})$')

    ax.set_xlabel('Prediction $\\hat{y}$', fontsize=12)
    ax.set_ylabel('Loss', fontsize=12)
    ax.set_title('Loss when True Label $y = 0$', fontsize=14, fontweight='bold')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 5)
    ax.axvline(x=0, color='green', linestyle='--', alpha=0.5, label='Target')
    ax.legend(loc='upper right', fontsize=10)
    ax.grid(True, alpha=0.3)

    # 添加说明
    ax.annotate('CE: $-\\log(1-\\hat{y})$\ngoes to infinity\nas $\\hat{y} \\to 1$',
                xy=(0.85, 2.5), fontsize=9, color='red', ha='center')

    plt.tight_layout()
    plt.show()


def plot_learning_rate_effect(lrs=None):
    """演示不同学习率的效果：太小 / 合适 / 太大"""
    # TODO: 实现学习率效果对比图
    raise NotImplementedError
