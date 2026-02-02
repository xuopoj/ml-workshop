"""简单的全连接神经网络实现"""

import numpy as np


class SimpleNN:
    """简单的全连接神经网络"""

    def __init__(self, layer_dims):
        """
        参数:
            layer_dims: 每层神经元数量，如 [2, 16, 16, 19]
        """
        self.layer_dims = layer_dims
        self.params = {}
        self.L = len(layer_dims) - 1

        # He 初始化
        for l in range(1, self.L + 1):
            self.params[f'W{l}'] = np.random.randn(
                layer_dims[l], layer_dims[l-1]
            ) * np.sqrt(2.0 / layer_dims[l-1])
            self.params[f'b{l}'] = np.zeros((layer_dims[l], 1))

    def relu(self, z):
        return np.maximum(0, z)

    def relu_deriv(self, z):
        return (z > 0).astype(float)

    def softmax(self, z):
        exp_z = np.exp(z - np.max(z, axis=0, keepdims=True))
        return exp_z / np.sum(exp_z, axis=0, keepdims=True)

    def forward(self, X):
        """前向传播"""
        self.cache = {'A0': X}
        A = X

        # 隐藏层: ReLU
        for l in range(1, self.L):
            Z = self.params[f'W{l}'] @ A + self.params[f'b{l}']
            A = self.relu(Z)
            self.cache[f'Z{l}'] = Z
            self.cache[f'A{l}'] = A

        # 输出层: Softmax
        Z = self.params[f'W{self.L}'] @ A + self.params[f'b{self.L}']
        A = self.softmax(Z)
        self.cache[f'Z{self.L}'] = Z
        self.cache[f'A{self.L}'] = A

        return A

    def loss(self, Y):
        """交叉熵损失"""
        m = Y.shape[1]
        AL = self.cache[f'A{self.L}']
        return -np.sum(Y * np.log(AL + 1e-8)) / m

    def backward(self, Y):
        """反向传播"""
        m = Y.shape[1]
        self.grads = {}

        # 输出层
        dZ = self.cache[f'A{self.L}'] - Y
        self.grads[f'dW{self.L}'] = dZ @ self.cache[f'A{self.L-1}'].T / m
        self.grads[f'db{self.L}'] = np.sum(dZ, axis=1, keepdims=True) / m

        # 隐藏层
        for l in reversed(range(1, self.L)):
            dA = self.params[f'W{l+1}'].T @ dZ
            dZ = dA * self.relu_deriv(self.cache[f'Z{l}'])
            self.grads[f'dW{l}'] = dZ @ self.cache[f'A{l-1}'].T / m
            self.grads[f'db{l}'] = np.sum(dZ, axis=1, keepdims=True) / m

    def update(self, lr):
        """梯度下降更新"""
        for l in range(1, self.L + 1):
            self.params[f'W{l}'] -= lr * self.grads[f'dW{l}']
            self.params[f'b{l}'] -= lr * self.grads[f'db{l}']

    def predict(self, X):
        """预测类别"""
        A = self.forward(X)
        return np.argmax(A, axis=0)

    def param_count(self):
        """总参数量"""
        return sum(p.size for p in self.params.values())


def train(model, X_train, y_train, X_test, y_test, epochs=500, lr=0.5, print_every=100):
    """
    训练模型并记录过程

    返回:
        history: 包含 loss, train_acc, test_acc 的字典
    """
    history = {'loss': [], 'train_acc': [], 'test_acc': []}

    for epoch in range(epochs):
        # 前向 + 反向 + 更新
        model.forward(X_train)
        loss = model.loss(y_train)
        model.backward(y_train)
        model.update(lr)

        # 计算准确率
        train_pred = model.predict(X_train)
        train_true = np.argmax(y_train, axis=0)
        train_acc = np.mean(train_pred == train_true)

        test_pred = model.predict(X_test)
        test_true = np.argmax(y_test, axis=0)
        test_acc = np.mean(test_pred == test_true)

        history['loss'].append(loss)
        history['train_acc'].append(train_acc)
        history['test_acc'].append(test_acc)

        if print_every and (epoch + 1) % print_every == 0:
            print(f"Epoch {epoch+1:3d} | Loss: {loss:.4f} | Train: {train_acc:.2%} | Test: {test_acc:.2%}")

    return history
