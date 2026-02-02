"""神经网络可视化工具"""

import numpy as np
import matplotlib.pyplot as plt


def plot_training_history(history, figsize=(12, 4)):
    """绘制训练过程的损失和准确率曲线"""
    fig, axes = plt.subplots(1, 2, figsize=figsize)

    # 损失曲线
    axes[0].plot(history['loss'], 'b-', linewidth=1.5)
    axes[0].set_xlabel('Epoch', fontsize=12)
    axes[0].set_ylabel('Loss', fontsize=12)
    axes[0].set_title('Training Loss', fontsize=14, fontweight='bold')
    axes[0].grid(alpha=0.3)

    # 准确率曲线
    axes[1].plot(history['train_acc'], 'b-', linewidth=1.5, label='Train')
    axes[1].plot(history['test_acc'], 'r--', linewidth=1.5, label='Test')
    axes[1].set_xlabel('Epoch', fontsize=12)
    axes[1].set_ylabel('Accuracy', fontsize=12)
    axes[1].set_title('Accuracy', fontsize=14, fontweight='bold')
    axes[1].legend()
    axes[1].grid(alpha=0.3)
    axes[1].set_ylim([0, 1.05])

    plt.tight_layout()
    plt.show()


def plot_result_matrix(model, encode_fn, num_range=10, max_sum=None, figsize=(8, 7)):
    """
    绘制加法预测结果矩阵

    参数:
        model: 训练好的模型
        encode_fn: 输入编码函数 encode_fn(a, b) -> vector
        num_range: 数字范围 (0 到 num_range-1)
        max_sum: 最大和限制，None 表示无限制
    """
    matrix = np.zeros((num_range, num_range))
    correct = np.zeros((num_range, num_range))
    valid = np.zeros((num_range, num_range))

    for a in range(num_range):
        for b in range(num_range):
            if max_sum is not None and a + b >= max_sum:
                continue
            valid[a, b] = 1
            x = encode_fn(a, b).reshape(-1, 1)
            pred = model.predict(x)[0]
            true = a + b
            matrix[a, b] = pred
            correct[a, b] = (pred == true)

    fig, ax = plt.subplots(figsize=figsize)

    # 背景：有效区域绿/红，无效区域灰色
    display = np.where(valid, correct, 0.5)
    ax.imshow(display, cmap='RdYlGn', vmin=0, vmax=1)

    for i in range(num_range):
        for j in range(num_range):
            if valid[i, j]:
                pred = int(matrix[i, j])
                color = 'black' if correct[i, j] else 'white'
                ax.text(j, i, str(pred), ha='center', va='center',
                        fontsize=10, color=color, fontweight='bold')
            else:
                ax.text(j, i, '-', ha='center', va='center',
                        fontsize=10, color='gray')

    ax.set_ylabel('a', fontsize=12)
    ax.set_title('a + b Predictions', fontsize=14, fontweight='bold')
    ax.set_xticks(range(num_range))
    ax.set_yticks(range(num_range))

    # 只计算有效区域的准确率
    valid_correct = correct[valid == 1]
    acc = np.mean(valid_correct) if len(valid_correct) > 0 else 0
    ax.set_xlabel(f'b\n(Accuracy: {acc:.1%})', fontsize=12)

    plt.tight_layout()
    plt.show()

    return acc


def plot_hidden_activations(model, encode_fn, test_cases, figsize=(12, 6)):
    """
    绘制不同输入的隐藏层激活模式

    参数:
        model: 训练好的模型
        encode_fn: 输入编码函数
        test_cases: [(a, b), ...] 测试用例列表
    """
    n_cases = len(test_cases)
    n_cols = min(3, n_cases)
    n_rows = (n_cases + n_cols - 1) // n_cols

    fig, axes = plt.subplots(n_rows, n_cols, figsize=figsize)
    axes = np.atleast_2d(axes).flatten()

    for ax, (a, b) in zip(axes, test_cases):
        x = encode_fn(a, b).reshape(-1, 1)
        model.forward(x)
        act = model.cache['A1'].flatten()
        result = a + b

        ax.bar(range(len(act)), act, color='steelblue', alpha=0.7)
        ax.set_title(f'{a} + {b} = {result}', fontsize=12, fontweight='bold')
        ax.set_xlabel('Neuron Index')
        ax.set_ylabel('Activation')
        ax.set_ylim([0, max(act) * 1.2 if max(act) > 0 else 1])

    # 隐藏多余的子图
    for ax in axes[n_cases:]:
        ax.set_visible(False)

    plt.suptitle('Hidden Layer Activations', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.show()


def plot_forward_pass(model, a, b, encode_fn, figsize=(14, 10), max_neurons=10):
    """
    可视化前向传播：在网络图上显示每个神经元的激活值

    参数:
        model: 训练好的模型
        a, b: 输入数字
        encode_fn: 输入编码函数
        max_neurons: 每层最多显示的神经元数（超过则采样显示）
    """
    x = encode_fn(a, b).reshape(-1, 1)
    model.forward(x)

    true_result = a + b
    pred_result = model.predict(x)[0]

    # 收集每层激活值
    layer_activations = [x.flatten()]  # 输入层
    for l in range(1, model.L + 1):
        layer_activations.append(model.cache[f'A{l}'].flatten())

    layer_sizes = [len(act) for act in layer_activations]
    n_layers = len(layer_sizes)

    # 计算显示的神经元数量（采样大层）
    display_sizes = []
    display_indices = []
    for size in layer_sizes:
        if size <= max_neurons:
            display_sizes.append(size)
            display_indices.append(list(range(size)))
        else:
            display_sizes.append(max_neurons)
            # 均匀采样
            indices = np.linspace(0, size - 1, max_neurons, dtype=int).tolist()
            display_indices.append(indices)

    fig, ax = plt.subplots(figsize=figsize)
    ax.set_xlim(-0.5, n_layers - 0.5)

    max_display = max(display_sizes)
    ax.set_ylim(-0.5, max_display + 0.5)
    ax.axis('off')

    # 神经元位置
    neuron_positions = []
    x_spacing = 1.0
    neuron_radius = 0.3

    for layer_idx, (n_display, indices) in enumerate(zip(display_sizes, display_indices)):
        x_pos = layer_idx * x_spacing
        # 垂直居中
        y_offset = (max_display - n_display) / 2
        positions = []
        for i in range(n_display):
            y_pos = y_offset + i
            positions.append((x_pos, y_pos))
        neuron_positions.append(positions)

    # 绘制连接线（先画，在神经元下面）
    for layer_idx in range(n_layers - 1):
        for pos1 in neuron_positions[layer_idx]:
            for pos2 in neuron_positions[layer_idx + 1]:
                ax.plot([pos1[0], pos2[0]], [pos1[1], pos2[1]],
                        color='lightgray', linewidth=0.5, zorder=1)

    # 颜色映射：激活值 -> 颜色
    cmap = plt.cm.Blues

    # 绘制神经元
    layer_names = ['Input'] + [f'Hidden {l}' for l in range(1, model.L)] + ['Output']

    for layer_idx, (positions, indices, activations) in enumerate(
            zip(neuron_positions, display_indices, layer_activations)):

        # 归一化激活值用于颜色
        act_values = activations[indices]
        if act_values.max() > act_values.min():
            act_normalized = (act_values - act_values.min()) / (act_values.max() - act_values.min())
        else:
            act_normalized = np.ones_like(act_values) * 0.5

        for i, (pos, idx, act, act_norm) in enumerate(
                zip(positions, indices, act_values, act_normalized)):

            # 神经元颜色基于激活值
            if layer_idx == n_layers - 1 and idx == pred_result:
                # 预测结果高亮
                color = 'gold'
                edgecolor = 'darkorange'
                linewidth = 3
            else:
                color = cmap(act_norm)
                edgecolor = 'steelblue'
                linewidth = 1.5

            circle = plt.Circle(pos, neuron_radius, color=color,
                                ec=edgecolor, linewidth=linewidth, zorder=2)
            ax.add_patch(circle)

            # 显示激活值
            if layer_idx == 0:
                # 输入层：显示哪个位置被激活（one-hot）
                if act > 0.5:
                    # 判断是 a 还是 b（前10维是a，后10维是b）
                    if idx < 10:
                        label = f'a={idx}'
                    else:
                        label = f'b={idx-10}'
                    ax.text(pos[0], pos[1], label, ha='center', va='center',
                            fontsize=8, fontweight='bold', zorder=3)
            elif layer_idx == n_layers - 1:
                # 输出层显示类别和概率
                if layer_sizes[layer_idx] <= max_neurons or idx == pred_result:
                    ax.text(pos[0], pos[1], f'{idx}', ha='center', va='center',
                            fontsize=9, fontweight='bold', zorder=3)
                    ax.text(pos[0], pos[1] - neuron_radius - 0.15, f'{act:.2f}',
                            ha='center', va='top', fontsize=7, color='gray')
            else:
                # 隐藏层显示激活值
                if act > 0.01:
                    ax.text(pos[0], pos[1], f'{act:.1f}', ha='center', va='center',
                            fontsize=8, zorder=3)

        # 层标签
        x_pos = layer_idx * x_spacing
        ax.text(x_pos, max_display + 0.3, f'{layer_names[layer_idx]}\n({layer_sizes[layer_idx]})',
                ha='center', va='bottom', fontsize=10, fontweight='bold')

        # 如果有采样，显示省略号
        if layer_sizes[layer_idx] > max_neurons:
            ax.text(x_pos, -0.3, '...', ha='center', va='top', fontsize=12, color='gray')

    # 标题
    status = '✓' if pred_result == true_result else '✗'
    ax.set_title(f'{a} + {b} = {pred_result}  (True: {true_result}) {status}',
                 fontsize=16, fontweight='bold', pad=20)

    # 添加颜色条
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(0, 1))
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, shrink=0.5, aspect=20, pad=0.02)
    cbar.set_label('Activation (normalized)', fontsize=10)

    plt.tight_layout()
    plt.show()

    # 打印摘要
    print(f"\n{'='*50}")
    print(f"输入: {a} + {b}")
    print(f"预测: {pred_result}  |  正确答案: {true_result}  |  {'✓ 正确' if pred_result == true_result else '✗ 错误'}")
    print(f"{'='*50}")

    for l in range(1, model.L + 1):
        act = layer_activations[l]
        print(f"\nLayer {l}: {len(act)} neurons")
        print(f"  activation: min={act.min():.3f}, max={act.max():.3f}, mean={act.mean():.3f}")
        if l == model.L:
            top3_idx = np.argsort(act)[-3:][::-1]
            print(f"  Top 3: {[(idx, f'{act[idx]:.3f}') for idx in top3_idx]}")
