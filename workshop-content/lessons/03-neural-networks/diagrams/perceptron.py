"""感知机与神经元可视化 / Perceptron and neuron visualizations"""

import numpy as np
import matplotlib.pyplot as plt


def plot_perceptron_boundary(w, b, X=None, y=None, ax=None):
    """
    绘制感知机决策边界

    Args:
        w: 权重向量 (2,)
        b: 偏置标量
        X: 可选数据点 (n_samples, 2)
        y: 可选标签 (n_samples,)
        ax: 可选 matplotlib axis
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 6))

    # 决策边界: w1*x1 + w2*x2 + b = 0 => x2 = -(w1*x1 + b) / w2
    x1_range = np.linspace(-3, 3, 100)
    if w[1] != 0:
        x2_boundary = -(w[0] * x1_range + b) / w[1]
        ax.plot(x1_range, x2_boundary, 'k-', linewidth=2, label='Decision Boundary')

    # 绘制数据点
    if X is not None and y is not None:
        ax.scatter(X[y == 0, 0], X[y == 0, 1], c='blue', marker='o', s=50, label='Class 0')
        ax.scatter(X[y == 1, 0], X[y == 1, 1], c='red', marker='x', s=50, label='Class 1')

    ax.set_xlabel('x₁', fontsize=12)
    ax.set_ylabel('x₂', fontsize=12)
    ax.set_title('Perceptron Decision Boundary', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xlim(-3, 3)
    ax.set_ylim(-3, 3)
    plt.tight_layout()
    plt.show()


def plot_xor_problem():
    """
    可视化 XOR 问题：展示为什么单个感知机无法解决

    XOR 数据点不是线性可分的，无法用一条直线分开
    """
    fig, axes = plt.subplots(1, 3, figsize=(14, 4))

    # XOR 数据
    X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
    y = np.array([0, 1, 1, 0])  # XOR 输出

    # 图1：XOR 数据分布
    ax = axes[0]
    ax.scatter(X[y == 0, 0], X[y == 0, 1], c='blue', marker='o', s=200, label='Output: 0', zorder=5)
    ax.scatter(X[y == 1, 0], X[y == 1, 1], c='red', marker='x', s=200, linewidths=3, label='Output: 1', zorder=5)
    ax.set_xlabel('x₁', fontsize=12)
    ax.set_ylabel('x₂', fontsize=12)
    ax.set_title('XOR Problem', fontsize=14, fontweight='bold')
    ax.set_xlim(-0.5, 1.5)
    ax.set_ylim(-0.5, 1.5)
    ax.legend()
    ax.grid(True, alpha=0.3)
    # 标注点
    for i, (x, label) in enumerate(zip(X, y)):
        ax.annotate(f'({x[0]},{x[1]})→{label}', xy=x, xytext=(x[0]+0.1, x[1]+0.15), fontsize=10)

    # 图2：尝试用不同直线分割（都失败）
    ax = axes[1]
    ax.scatter(X[y == 0, 0], X[y == 0, 1], c='blue', marker='o', s=200, zorder=5)
    ax.scatter(X[y == 1, 0], X[y == 1, 1], c='red', marker='x', s=200, linewidths=3, zorder=5)

    # 画几条尝试的决策边界
    x_line = np.linspace(-0.5, 1.5, 100)
    ax.plot(x_line, 0.5 - x_line, 'g--', alpha=0.7, linewidth=2, label='Attempt 1')
    ax.plot(x_line, x_line - 0.5, 'm--', alpha=0.7, linewidth=2, label='Attempt 2')
    ax.axhline(y=0.5, color='orange', linestyle='--', alpha=0.7, linewidth=2, label='Attempt 3')

    ax.set_xlabel('x₁', fontsize=12)
    ax.set_ylabel('x₂', fontsize=12)
    ax.set_title('No Single Line Works!', fontsize=14, fontweight='bold')
    ax.set_xlim(-0.5, 1.5)
    ax.set_ylim(-0.5, 1.5)
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3)

    # 图3：解决方案 - 需要两条线（两层网络）
    ax = axes[2]
    ax.scatter(X[y == 0, 0], X[y == 0, 1], c='blue', marker='o', s=200, zorder=5)
    ax.scatter(X[y == 1, 0], X[y == 1, 1], c='red', marker='x', s=200, linewidths=3, zorder=5)

    # 两条线可以分割
    ax.plot(x_line, x_line + 0.5, 'g-', linewidth=2, label='Line 1: x₂ = x₁ + 0.5')
    ax.plot(x_line, x_line - 0.5, 'g-', linewidth=2, label='Line 2: x₂ = x₁ - 0.5')

    # 填充中间区域
    ax.fill_between(x_line, x_line - 0.5, x_line + 0.5, alpha=0.2, color='red', label='XOR = 1 region')

    ax.set_xlabel('x₁', fontsize=12)
    ax.set_ylabel('x₂', fontsize=12)
    ax.set_title('Solution: 2 Lines (Multi-layer)', fontsize=14, fontweight='bold')
    ax.set_xlim(-0.5, 1.5)
    ax.set_ylim(-0.5, 1.5)
    ax.legend(loc='upper right', fontsize=9)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()


def plot_neuron_diagram():
    """绘制单个神经元结构图：输入、权重、求和、激活函数、输出"""
    # TODO: 实现神经元结构图
    raise NotImplementedError


def plot_perceptron_vs_neuron():
    """并排对比感知机与神经元的区别"""
    # TODO: 实现对比图
    raise NotImplementedError
