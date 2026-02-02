# 神经网络与深度学习 - 课程导航

本课程分为9个独立的章节，每个章节都是一个独立的Jupyter Notebook。

## 章节列表

### 基础概念
1. [从感知机到神经元](01-perceptron-and-neuron.ipynb)
   - 直线方程到超平面
   - 感知机原理与局限性
   - XOR问题的重要性
   - 神经元与激活函数的必要性

2. [激活函数](02-activation-functions.ipynb)
   - 常见激活函数（Sigmoid, Tanh, ReLU, Leaky ReLU）
   - 激活函数对比与选择
   - 可视化展示

3. [神经网络的架构](03-network-architecture.ipynb)
   - 多层感知机（MLP）结构
   - 各层的作用
   - 记号约定
   - MNIST网络架构示例

### 训练原理
4. [前向传播](04-forward-propagation.ipynb)
   - 单个神经元的前向传播
   - 整层的向量化计算
   - 代码实现示例

5. [损失函数](05-loss-functions.ipynb)
   - 回归任务损失函数（MSE, MAE）
   - 分类任务损失函数（交叉熵）
   - 为什么分类用交叉熵而不是MSE

6. [反向传播与梯度下降](06-backpropagation.ipynb)
   - 梯度下降原理
   - 链式法则
   - 反向传播的四个基本方程
   - 计算图与梯度流
   - 常见问题（梯度消失/爆炸）
   - 完整的反向传播演示

### 实战演练
7. [MNIST实战](07-mnist-practice.ipynb)
   - MNIST数据集介绍
   - 从零实现神经网络
   - 训练与可视化
   - 预测结果分析

8. [练习与挑战](08-exercises.ipynb)
   - 调整网络架构
   - 实现不同激活函数
   - 添加多层网络
   - 学习率调度
   - L2正则化

9. [总结与展望](09-summary.ipynb)
   - 核心知识点回顾
   - 深度学习关键要素
   - 从MLP到现代深度学习
   - 延伸阅读资源

## 学习建议

- **顺序学习**：建议按1-9的顺序学习，每个章节都建立在前面的基础上
- **动手实践**：每个章节都包含代码示例，建议运行并修改代码加深理解
- **重点章节**：
  - 第1章（理解基础概念）
  - 第6章（反向传播是核心）
  - 第7章（实战应用）

## 参考资料

- [Neural Networks and Deep Learning](http://neuralnetworksanddeeplearning.com/) - Michael Nielsen
- 《深度学习》(Deep Learning Book) - Ian Goodfellow

---

**提示**: 原完整版notebook已备份为 `神经网络与深度学习.ipynb`
