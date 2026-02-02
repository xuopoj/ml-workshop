"""网络架构可视化 / Network architecture visualizations"""

import numpy as np
import matplotlib.pyplot as plt


def plot_network(layers=None, ax=None):
    """
    绘制神经网络架构图

    Args:
        layers: 每层神经元数量列表，例如 [2, 4, 3, 1]
        ax: 可选 matplotlib axis
    """
    if layers is None:
        layers = [2, 4, 3, 1]

    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 6))

    n_layers = len(layers)
    max_neurons = max(layers)

    # 绘制每一层的神经元
    for i, n_neurons in enumerate(layers):
        x = i / (n_layers - 1) if n_layers > 1 else 0.5
        y_positions = np.linspace(0.1, 0.9, n_neurons) if n_neurons > 1 else [0.5]

        for j, y in enumerate(y_positions):
            circle = plt.Circle((x, y), 0.03, color='steelblue', ec='black', linewidth=1.5)
            ax.add_patch(circle)

            # 绘制连接线到下一层
            if i < n_layers - 1:
                next_n = layers[i + 1]
                next_x = (i + 1) / (n_layers - 1)
                next_y_positions = np.linspace(0.1, 0.9, next_n) if next_n > 1 else [0.5]
                for next_y in next_y_positions:
                    ax.plot([x + 0.03, next_x - 0.03], [y, next_y],
                            color='gray', linewidth=0.5, alpha=0.5)

    # 添加层标签
    layer_names = ['Input'] + [f'Hidden {i}' for i in range(1, n_layers - 1)] + ['Output']
    for i, name in enumerate(layer_names):
        x = i / (n_layers - 1) if n_layers > 1 else 0.5
        ax.text(x, -0.05, name, ha='center', fontsize=10)
        ax.text(x, 1.0, f'n={layers[i]}', ha='center', fontsize=9, color='gray')

    ax.set_xlim(-0.1, 1.1)
    ax.set_ylim(-0.15, 1.1)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('Neural Network Architecture', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.show()


def plot_layer_dimensions(n_in, n_out, show_batch=False):
    """
    可视化矩阵维度：W(n_out, n_in) @ X(n_in, 1) + b(n_out, 1) = Z(n_out, 1)

    Args:
        n_in: 输入维度
        n_out: 输出维度
        show_batch: 是否显示批量处理版本
    """
    fig, ax = plt.subplots(figsize=(12, 5))

    # 缩放因子：将维度映射到可视化高度/宽度
    scale = 0.15
    col_width = 0.25  # 列向量的宽度
    base_y = 0.5      # 基准 y 位置（居中对齐）

    def draw_matrix(ax, x, width, height, label, dim_text, color='lightblue'):
        """绘制矩阵，以 base_y 为中心垂直居中"""
        y = base_y - height / 2
        rect = plt.Rectangle((x, y), width, height, fill=True,
                              facecolor=color, edgecolor='black', linewidth=2)
        ax.add_patch(rect)
        # 矩阵名称（上方）
        ax.text(x + width/2, base_y + height/2 + 0.12, label, ha='center', va='bottom',
                fontsize=14, fontweight='bold')
        # 维度标注（中心）
        ax.text(x + width/2, base_y, dim_text, ha='center', va='center',
                fontsize=11, family='monospace')
        # 行数标注（左侧）
        ax.annotate('', xy=(x - 0.05, y), xytext=(x - 0.05, y + height),
                    arrowprops=dict(arrowstyle='<->', color='red', lw=1.5))
        # 列数标注（底部）
        ax.annotate('', xy=(x, y - 0.08), xytext=(x + width, y - 0.08),
                    arrowprops=dict(arrowstyle='<->', color='blue', lw=1.5))

    # 计算各矩阵的高度（按维度比例）
    h_out = n_out * scale  # W 的行数、b 的行数、z 的行数
    h_in = n_in * scale    # W 的列数、a 的行数
    w_W = n_in * scale     # W 的宽度

    if show_batch:
        # 批量版本: W @ A + b = Z  (带 m 个样本)
        m_width = 0.6  # m 列的可视化宽度

        x = 0.3
        draw_matrix(ax, x, w_W, h_out, '$W^{[l]}$', f'({n_out}, {n_in})', 'lightyellow')
        x += w_W + 0.15
        ax.text(x, base_y, '@', fontsize=16, ha='center', va='center')
        x += 0.15
        draw_matrix(ax, x, m_width, h_in, '$a^{[l-1]}$', f'({n_in}, m)', 'lightgreen')
        x += m_width + 0.15
        ax.text(x, base_y, '+', fontsize=16, ha='center', va='center')
        x += 0.15
        draw_matrix(ax, x, col_width, h_out, '$b^{[l]}$', f'({n_out}, 1)', 'lightcoral')
        x += col_width + 0.15
        ax.text(x, base_y, '=', fontsize=16, ha='center', va='center')
        x += 0.15
        draw_matrix(ax, x, m_width, h_out, '$z^{[l]}$', f'({n_out}, m)', 'plum')

        ax.set_xlim(0, x + m_width + 0.3)
        ax.set_title('Batch Matrix Dimensions: $z^{[l]} = W^{[l]} a^{[l-1]} + b^{[l]}$',
                     fontsize=14, fontweight='bold')
    else:
        # 单样本版本
        x = 0.3
        draw_matrix(ax, x, w_W, h_out, '$W^{[l]}$', f'({n_out}, {n_in})', 'lightyellow')
        x += w_W + 0.15
        ax.text(x, base_y, '@', fontsize=16, ha='center', va='center')
        x += 0.15
        draw_matrix(ax, x, col_width, h_in, '$a^{[l-1]}$', f'({n_in}, 1)', 'lightgreen')
        x += col_width + 0.15
        ax.text(x, base_y, '+', fontsize=16, ha='center', va='center')
        x += 0.15
        draw_matrix(ax, x, col_width, h_out, '$b^{[l]}$', f'({n_out}, 1)', 'lightcoral')
        x += col_width + 0.15
        ax.text(x, base_y, '=', fontsize=16, ha='center', va='center')
        x += 0.15
        draw_matrix(ax, x, col_width, h_out, '$z^{[l]}$', f'({n_out}, 1)', 'plum')

        ax.set_xlim(0, x + col_width + 0.3)
        ax.set_title('Matrix Dimensions: $z^{[l]} = W^{[l]} a^{[l-1]} + b^{[l]}$',
                     fontsize=14, fontweight='bold')

    # 图例说明
    ax.text(0.5, 0.02, 'Height = row count (red arrow) | Width = column count (blue arrow)',
            fontsize=10, style='italic', color='gray', transform=ax.transAxes, ha='center')

    max_h = max(h_out, h_in)
    ax.set_ylim(base_y - max_h/2 - 0.3, base_y + max_h/2 + 0.4)
    ax.set_aspect('equal')
    ax.axis('off')
    plt.tight_layout()
    plt.show()


def plot_depth_vs_width():
    """
    对比深度网络与宽度网络

    左：浅而宽 (1 hidden layer, many neurons)
    右：深而窄 (multiple hidden layers, fewer neurons each)
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # 左图：浅而宽 [3, 16, 1]
    wide_layers = [3, 16, 1]
    ax = axes[0]
    n_layers = len(wide_layers)
    max_neurons = max(wide_layers)

    for i, n_neurons in enumerate(wide_layers):
        x = i / (n_layers - 1) if n_layers > 1 else 0.5
        y_positions = np.linspace(0.1, 0.9, n_neurons) if n_neurons > 1 else [0.5]

        for j, y in enumerate(y_positions):
            circle = plt.Circle((x, y), 0.025, color='steelblue', ec='black', linewidth=1)
            ax.add_patch(circle)

            if i < n_layers - 1:
                next_n = wide_layers[i + 1]
                next_x = (i + 1) / (n_layers - 1)
                next_y_positions = np.linspace(0.1, 0.9, next_n) if next_n > 1 else [0.5]
                for next_y in next_y_positions:
                    ax.plot([x + 0.025, next_x - 0.025], [y, next_y],
                            color='gray', linewidth=0.3, alpha=0.5)

    ax.set_xlim(-0.1, 1.1)
    ax.set_ylim(-0.1, 1.1)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('Shallow & Wide\n[3, 16, 1]', fontsize=14, fontweight='bold')
    ax.text(0.5, -0.05, f'Parameters: {3*16 + 16 + 16*1 + 1} = 81',
            ha='center', fontsize=11, transform=ax.transAxes)

    # 右图：深而窄 [3, 4, 4, 4, 1]
    deep_layers = [3, 4, 4, 4, 1]
    ax = axes[1]
    n_layers = len(deep_layers)

    for i, n_neurons in enumerate(deep_layers):
        x = i / (n_layers - 1) if n_layers > 1 else 0.5
        y_positions = np.linspace(0.3, 0.7, n_neurons) if n_neurons > 1 else [0.5]

        for j, y in enumerate(y_positions):
            circle = plt.Circle((x, y), 0.025, color='coral', ec='black', linewidth=1)
            ax.add_patch(circle)

            if i < n_layers - 1:
                next_n = deep_layers[i + 1]
                next_x = (i + 1) / (n_layers - 1)
                next_y_positions = np.linspace(0.3, 0.7, next_n) if next_n > 1 else [0.5]
                for next_y in next_y_positions:
                    ax.plot([x + 0.025, next_x - 0.025], [y, next_y],
                            color='gray', linewidth=0.5, alpha=0.6)

    ax.set_xlim(-0.1, 1.1)
    ax.set_ylim(-0.1, 1.1)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('Deep & Narrow\n[3, 4, 4, 4, 1]', fontsize=14, fontweight='bold')
    # 参数: 3*4+4 + 4*4+4 + 4*4+4 + 4*1+1 = 16+20+20+5 = 61
    ax.text(0.5, -0.05, f'Parameters: {3*4+4 + 4*4+4 + 4*4+4 + 4*1+1} = 61',
            ha='center', fontsize=11, transform=ax.transAxes)

    fig.suptitle('Depth vs Width: Same expressive power, different parameter counts',
                 fontsize=13, style='italic', y=0.02)
    plt.tight_layout()
    plt.show()


def plot_feature_hierarchy():
    """
    可视化特征层次：边缘 → 纹理 → 部件 → 物体

    展示深度网络如何逐层构建抽象特征
    """
    fig, ax = plt.subplots(figsize=(12, 7))

    # 层次结构数据
    levels = [
        ('Layer 1', 'Edges & Gradients', ['—', '|', '/', '\\', '○'], 'lightblue'),
        ('Layer 2', 'Textures & Corners', ['⌐', '└', '┌', '▢', '◠'], 'lightgreen'),
        ('Layer 3', 'Parts & Patterns', ['👁', '👃', '👄', '◉', '▣'], 'lightyellow'),
        ('Layer 4', 'Objects & Concepts', ['😀', '🚗', '🏠', '🐱', '✋'], 'lightcoral'),
    ]

    n_levels = len(levels)
    box_height = 0.18
    box_width = 0.7

    for i, (layer_name, description, symbols, color) in enumerate(levels):
        y = 0.8 - i * 0.22

        # 绘制层框
        rect = plt.Rectangle((0.15, y - box_height/2), box_width, box_height,
                              facecolor=color, edgecolor='black', linewidth=2,
                              alpha=0.7)
        ax.add_patch(rect)

        # 层名称（左侧）
        ax.text(0.12, y, layer_name, ha='right', va='center',
                fontsize=12, fontweight='bold')

        # 描述（框内左侧）
        ax.text(0.18, y, description, ha='left', va='center', fontsize=11)

        # 示例符号（框内右侧）
        symbol_text = '  '.join(symbols)
        ax.text(0.82, y, symbol_text, ha='right', va='center', fontsize=14)

        # 绘制向上的箭头（除了最后一层）
        if i < n_levels - 1:
            ax.annotate('', xy=(0.5, y - box_height/2 - 0.01),
                       xytext=(0.5, y - box_height/2 - 0.04),
                       arrowprops=dict(arrowstyle='->', color='gray', lw=2))

    # 添加说明
    ax.text(0.5, 0.95, 'Feature Hierarchy in Deep Networks',
            ha='center', va='top', fontsize=14, fontweight='bold')
    ax.text(0.5, 0.05, 'Each layer builds more abstract features from the previous layer',
            ha='center', va='bottom', fontsize=11, style='italic', color='gray')

    # 左侧标注：具体 → 抽象
    ax.annotate('', xy=(0.05, 0.85), xytext=(0.05, 0.15),
                arrowprops=dict(arrowstyle='->', color='darkblue', lw=2))
    ax.text(0.03, 0.5, 'Concrete → Abstract', ha='center', va='center',
            fontsize=10, rotation=90, color='darkblue')

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    plt.tight_layout()
    plt.show()
