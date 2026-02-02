"""前向/反向传播可视化 / Forward and backward propagation visualizations"""

import numpy as np
import matplotlib.pyplot as plt


def plot_forward_pass(network, X, step_by_step=False):
    """
    可视化前向传播过程

    Args:
        network: 网络参数字典 {'W1': ..., 'b1': ..., 'W2': ..., 'b2': ...}
        X: 输入数据
        step_by_step: 是否逐层显示
    """
    # TODO: 实现前向传播可视化
    raise NotImplementedError


def plot_computational_graph(expression='y = sigmoid(w*x + b)'):
    """
    绘制计算图 DAG

    Args:
        expression: 表达式字符串，用于标题
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    # 简单的计算图示例: x, w, b -> multiply -> add -> sigmoid -> y
    nodes = {
        'x': (0.1, 0.5),
        'w': (0.1, 0.8),
        'b': (0.3, 0.2),
        '×': (0.3, 0.65),
        '+': (0.5, 0.5),
        'σ': (0.7, 0.5),
        'y': (0.9, 0.5),
    }

    edges = [
        ('x', '×'), ('w', '×'),
        ('×', '+'), ('b', '+'),
        ('+', 'σ'),
        ('σ', 'y'),
    ]

    # 绘制节点
    for name, (x, y) in nodes.items():
        if name in ['×', '+', 'σ']:
            circle = plt.Circle((x, y), 0.05, color='lightcoral', ec='black')
        else:
            circle = plt.Circle((x, y), 0.04, color='lightblue', ec='black')
        ax.add_patch(circle)
        ax.text(x, y, name, ha='center', va='center', fontsize=12, fontweight='bold')

    # 绘制边
    for start, end in edges:
        x1, y1 = nodes[start]
        x2, y2 = nodes[end]
        ax.annotate('', xy=(x2 - 0.05, y2), xytext=(x1 + 0.05, y1),
                    arrowprops=dict(arrowstyle='->', color='gray', lw=1.5))

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title(f'Computational Graph: {expression}', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.show()


def plot_backprop_flow(network=None, highlight_layer=None):
    """可视化梯度反向流动"""
    # TODO: 实现反向传播梯度流可视化
    raise NotImplementedError


def plot_chain_rule_demo():
    """演示链式法则"""
    # TODO: 实现链式法则可视化
    raise NotImplementedError


def plot_batch_dimensions(layers=None):
    """
    可视化批量处理的维度流动

    Args:
        layers: 网络层维度列表，如 [784, 128, 64, 10]
    """
    if layers is None:
        layers = [784, 128, 64, 10]

    fig, ax = plt.subplots(figsize=(14, 6))

    n_layers = len(layers)
    x_positions = np.linspace(0.1, 0.9, n_layers)

    # 绘制每层的数据矩阵
    for i, (x, n) in enumerate(zip(x_positions, layers)):
        # 数据矩阵高度按神经元数量缩放（对数比例，防止差异太大）
        height = 0.15 * n
        # height = 0.3 + 0.2 * np.log10(n + 1)
        width = 0.08  # 宽度代表 batch size

        # 绘制矩阵
        rect = plt.Rectangle((x - width/2, 0.5 - height/2), width, height,
                              fill=True, facecolor='lightblue', edgecolor='steelblue',
                              linewidth=2)
        ax.add_patch(rect)

        # 层标签
        if i == 0:
            label = '$X$'
            layer_name = 'Input'
        elif i == n_layers - 1:
            label = '$\\hat{Y}$'
            layer_name = 'Output'
        else:
            label = f'$A^{{[{i}]}}$'
            layer_name = f'Hidden {i}'

        # 矩阵维度标注
        ax.text(x, 0.5 - height/2 - 0.08, f'({n}, m)', ha='center', fontsize=10,
                family='monospace', color='steelblue')
        ax.text(x, 0.5 + height/2 + 0.05, label, ha='center', fontsize=12, fontweight='bold')
        ax.text(x, 0.15, layer_name, ha='center', fontsize=9, color='gray')

        # 绘制连接箭头和权重矩阵
        if i < n_layers - 1:
            next_x = x_positions[i + 1]
            mid_x = (x + next_x) / 2

            # 箭头
            ax.annotate('', xy=(next_x - 0.06, 0.5), xytext=(x + 0.06, 0.5),
                        arrowprops=dict(arrowstyle='->', color='gray', lw=2))

            # 权重矩阵标注
            w_text = f'$W^{{[{i+1}]}}$\n({layers[i+1]}, {layers[i]})'
            ax.text(mid_x, 0.65, w_text, ha='center', fontsize=9,
                    bbox=dict(boxstyle='round', facecolor='lightyellow', edgecolor='orange'))

    # 批量大小说明
    ax.text(0.5, 0.92, f'Batch Processing: m samples processed in parallel',
            ha='center', fontsize=11, style='italic',
            transform=ax.transAxes)

    # 公式说明
    ax.text(0.5, 0.02, 'Each layer: $A^{[l]} = \\sigma(W^{[l]} A^{[l-1]} + b^{[l]})$, where columns are samples',
            ha='center', fontsize=10, transform=ax.transAxes,
            bbox=dict(boxstyle='round', facecolor='white', edgecolor='gray', alpha=0.8))

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect('auto')
    ax.axis('off')
    ax.set_title('Dimension Flow in Batch Forward Propagation', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.show()
