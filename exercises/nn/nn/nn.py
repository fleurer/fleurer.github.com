import numpy as np
from nn.layers import Dense, ReLU, Sigmoid, SoftmaxWithLoss


class TwoLayerNN:
    def __init__(self):
        self.W1 = np.random.randn(2, 3)
        self.b1 = np.zeros((3, 1))
        self.W2 = np.random.randn(3, 2)
        self.b2 = np.zeros((2, 1))
        self.layer1 = Dense(self.W1, self.b1, ReLU)
        self.layer2 = Dense(self.W2, self.b2, Sigmoid)
        self.last_layer = SoftmaxWithLoss()

    def predict(self, x):
        a1 = self.layer1.forward(x)
        a2 = self.layer2.forward(a1)
        return a2

    def loss(self, X, Y):
        Yhat = self.predict(X)
        return self.last_layer.forward(Yhat, Y)

