"""激活函数可视化 / Activation function visualizations"""

import numpy as np
import matplotlib.pyplot as plt


# 激活函数定义
def sigmoid(x):
    return 1 / (1 + np.exp(-x))

def tanh(x):
    return np.tanh(x)

def relu(x):
    return np.maximum(0, x)

def leaky_relu(x, alpha=0.01):
    return np.where(x > 0, x, alpha * x)

ACTIVATIONS = {
    'sigmoid': sigmoid,
    'tanh': tanh,
    'relu': relu,
    'leaky_relu': leaky_relu,
}


def plot_activation(name='sigmoid', ax=None):
    """
    绘制单个激活函数

    Args:
        name: 激活函数名称 ('sigmoid', 'tanh', 'relu', 'leaky_relu')
        ax: 可选 matplotlib axis
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(6, 4))

    x = np.linspace(-5, 5, 200)
    func = ACTIVATIONS.get(name, sigmoid)
    y = func(x)

    ax.plot(x, y, linewidth=2)
    ax.axhline(y=0, color='k', linewidth=0.5)
    ax.axvline(x=0, color='k', linewidth=0.5)
    ax.set_xlabel('x', fontsize=12)
    ax.set_ylabel(f'{name}(x)', fontsize=12)
    ax.set_title(f'{name.upper()} Activation', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


def plot_activation_comparison(funcs=None):
    """
    并排比较多个激活函数

    Args:
        funcs: 激活函数名称列表，默认 ['sigmoid', 'tanh', 'relu', 'leaky_relu']
    """
    if funcs is None:
        funcs = ['sigmoid', 'tanh', 'relu', 'leaky_relu']

    n = len(funcs)
    fig, axes = plt.subplots(1, n, figsize=(4 * n, 4))
    if n == 1:
        axes = [axes]

    x = np.linspace(-5, 5, 200)

    for ax, name in zip(axes, funcs):
        func = ACTIVATIONS.get(name, sigmoid)
        y = func(x)
        ax.plot(x, y, linewidth=2)
        ax.axhline(y=0, color='k', linewidth=0.5)
        ax.axvline(x=0, color='k', linewidth=0.5)
        ax.set_xlabel('x', fontsize=11)
        ax.set_ylabel('y', fontsize=11)
        ax.set_title(name.upper(), fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()


def plot_activation_derivatives(funcs=None):
    """绘制激活函数及其导数"""
    # TODO: 实现导数对比图
    raise NotImplementedError


def plot_dying_relu(negative_slope=0):
    """演示 ReLU 死亡神经元问题"""
    # TODO: 实现 dying ReLU 可视化
    raise NotImplementedError
