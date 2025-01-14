import unittest
import numpy as np
from matplotlib import pyplot as plt
from nn.layers import (
    softmax,
    Dense,
    Sigmoid,
    cross_entropy_error,
    ReLU,
    SoftmaxWithLoss,
)
from nn.nn import numerical_gradient, TwoLayerNN, LayeredNN, load_mnist


class TestLayer(unittest.TestCase):
    def test_dense(self):
        W = np.array([[1, 2, 3], [4, 5, 6]]).T  # 3 x 2
        b = np.array([7, 8])  # 2
        l = Dense(W, b)
        X = np.array(
            [[0.1, 0.2, 0.3], [0.4, 0.4, 0.4], [0.9, 0.9, 0.9], [0.8, 0.8, 0.8]]
        )  # 4 x 3
        l.forward(X)
        W = np.array([[1, 2, 3]]).T  # 3 x 1
        b = np.array(
            [
                4,
            ]
        )  # 1
        l = Dense(W, b)
        r = l.forward(np.array([[2, 2, 2]]))
        self.assertEqual(r[0][0], 16)
        grad = l.backward(
            np.array(
                [
                    [
                        1,
                    ]
                ]
            )
        )
        self.assertEqual(grad[0].tolist(), [1, 2, 3])
        self.assertEqual(
            l.dW.tolist(),
            [
                [
                    2,
                ],
                [
                    2,
                ],
                [
                    2,
                ],
            ],
        )
        self.assertEqual(
            l.db.tolist(),
            [
                1,
            ],
        )

    def test_sigmoid(self):
        l = Sigmoid()
        r = l.forward(np.array([-1, 1, 2]))
        self.assertAlmostEqual(r[0], 0.26894142)
        self.assertAlmostEqual(r[1], 0.73105858)
        self.assertAlmostEqual(r[2], 0.88079708)
        l.forward(np.array([-100, 100, 0]))
        dout = l.backward(np.array([1, 1, 1]))
        self.assertAlmostEqual(dout[0], 0.0)
        self.assertAlmostEqual(dout[1], 0.0)
        self.assertAlmostEqual(dout[2], 0.25)

    def test_relu(self):
        l = ReLU()
        r = l.forward(np.array([-1, 1, 2]))
        self.assertEqual(r.tolist(), [0.0, 1.0, 2.0])
        dout = l.backward(np.array([1, 1, 1]))
        self.assertEqual(dout.tolist(), [0.0, 1.0, 1.0])

    def test_softmax(self):
        r = softmax(np.array([[0.3, 2.9, 4.0]]))
        self.assertAlmostEqual(r[0, 0], 0.018211273)
        self.assertAlmostEqual(r[0, 1], 0.2451918129)
        self.assertAlmostEqual(r[0, 2], 0.7365969138)
        r = softmax(np.array([[0.3, 2.9, 4.0], [4.0, 2.9, 0.3]]))
        self.assertAlmostEqual(r[0, 0], 0.018211273)
        self.assertAlmostEqual(r[0, 1], 0.2451918129)
        self.assertAlmostEqual(r[0, 2], 0.7365969138)
        self.assertAlmostEqual(r[1, 0], 0.7365969138)
        self.assertAlmostEqual(r[1, 1], 0.2451918129)
        self.assertAlmostEqual(r[1, 2], 0.018211273)
        r = softmax(np.array([[0, 0, 1]]))
        self.assertAlmostEqual(r[0, 0], 0.21194156)
        self.assertAlmostEqual(r[0, 1], 0.21194156)
        self.assertAlmostEqual(r[0, 2], 0.57611688)

    def test_softmax_with_loss(self):
        l = SoftmaxWithLoss()
        r = l.forward(np.array([[0, 0, 1]]), np.array([[0, 0, 1]]))
        self.assertAlmostEqual(r, 0.551444714)
        dout = l.backward()
        self.assertAlmostEqual(dout[0, 0], 0.21194155)
        self.assertAlmostEqual(dout[0, 1], 0.21194155)
        self.assertAlmostEqual(dout[0, 2], -0.4238831)
        r = l.forward(
            np.array([[-0.21294155, -0.21194155, 1.4238831]]), np.array([[0, 0, 1]])
        )
        self.assertAlmostEqual(r, 0.3288638)

    def test_numerial_gradient(self):
        relu = lambda x: np.maximum(0, x)
        grad = numerical_gradient(relu, np.array([-1.0]))
        self.assertEqual(grad[0], 0)
        grad = numerical_gradient(relu, np.array([1.0]))
        self.assertAlmostEqual(grad[0], 1)

    def test_cross_entropy_error(self):
        Y = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1], [1, 0, 0]])
        Ypred = np.array(
            [[0.7, 0.2, 0.1], [0.1, 0.8, 0.1], [0.1, 0.2, 0.7], [0.9, 0.05, 0.05]]
        )
        E = cross_entropy_error(Ypred, Y)
        self.assertAlmostEqual(E, 0.2604634887)

    def test_dense_backward(self):
        W = np.array([[1, 2, 3], [4, 5, 6]]).T  # 3 x 2
        b = np.array([0, 0])  # 2
        layer = Dense(W, b)
        a = layer.forward(np.array([[1, 2, 3]]))
        self.assertEqual(a.shape, (1, 2))
        self.assertEqual(a[0, 0], 14)
        self.assertEqual(a[0, 1], 32)
        grad = layer.backward(np.array([[1, 1]]))
        self.assertEqual(grad.shape, (1, 3))
        self.assertEqual(layer.dW.shape, (3, 2))
        self.assertEqual(layer.db.shape, (2,))
        self.assertEqual(layer.dW.tolist(), [[1, 1], [2, 2], [3, 3]])
        numerical_gradient(lambda x: layer.forward(x).sum(), np.array([1, 2, 3]))


class TestNN(unittest.TestCase):
    def setUp(self):
        plt.title("Training Loss")
        plt.xlabel("Iteration")
        plt.ylabel("Loss")
        plt.clf()

    def debug_loss(self, i, l, interval=100):
        print("loss: ", l)
        if i % interval == 0:
            plt.plot(i, l, "ro")
            plt.draw()
            plt.pause(0.01)

    def test_train(self):
        X_train = np.array([[1.0, 1.0], [1, 1], [0, 1.0], [1.0, 0], [0, 0]])
        Y_train = np.array([[1.0, 0], [1, 0], [0, 1], [0, 1], [0, 1]])
        nn = TwoLayerNN(2, 2, 2)
        for i in range(10000):
            nn.train(X_train, Y_train, learning_rate=1, numerial_gradient=True)
            l = nn.loss(X_train, Y_train)
            self.debug_loss(i, l)
        O = softmax(nn.predict(np.array([[1, 1], [0, 0], [1, 0], [0, 1]])))
        print(O)
        self.assertGreater(O[0][0], O[0][1])
        self.assertGreater(O[1][1], O[1][0])
        self.assertGreater(O[2][1], O[2][0])
        self.assertGreater(O[3][1], O[3][0])

    def test_train_backward(self):
        X_train = np.array([[1.0, 1.0], [0, 1.0], [1.0, 0], [0, 0]])
        Y_train = np.array([[1.0, 0], [0, 1], [0, 1], [0, 1]])
        nn = TwoLayerNN(2, 2, 2)
        for i in range(20000):
            l = nn.loss(X_train, Y_train).round(13)
            nn.train(X_train, Y_train, learning_rate=0.1)
            self.debug_loss(i, l)
        O = softmax(nn.predict(np.array([[1, 1], [0, 0], [1, 0], [0, 1]])))
        self.assertGreater(O[0][0], O[0][1])
        self.assertGreater(O[1][1], O[1][0])
        self.assertGreater(O[2][1], O[2][0])
        self.assertGreater(O[3][1], O[3][0])

    def test_train2(self):
        X_train = np.array([[1.0, 1.0], [0, 1.0], [1.0, 0], [0, 0]])
        Y_train = np.array([[1.0, 0], [1, 0], [1, 0], [0, 1]])
        nn = TwoLayerNN(2, 16, 2)
        loss = []
        for i in range(20000):
            l = nn.loss(X_train, Y_train).round(14)
            nn.train(X_train, Y_train, learning_rate=0.1)
            self.debug_loss(i, l)
        O = softmax(nn.predict(np.array([[1, 1], [0, 0], [1, 0], [0, 1]])))
        self.assertGreater(O[0][0], O[0][1])
        self.assertGreater(O[1][1], O[1][0])
        self.assertGreater(O[2][0], O[2][1])
        self.assertGreater(O[3][0], O[3][1])

    def test_train_layered_nn(self):
        X_train = np.array([[1.0, 1.0], [0, 1.0], [1.0, 0], [0, 0]])
        Y_train = np.array([[1.0, 0], [1, 0], [1, 0], [0, 1]])
        nn = LayeredNN([2, 16, 2])
        loss = []
        for i in range(50000):
            l = nn.loss(X_train, Y_train).round(14)
            nn.train(X_train, Y_train, learning_rate=0.01, numerical_gradient=False)
            self.debug_loss(i, l)
        O = softmax(nn.predict(np.array([[1, 1], [0, 0], [1, 0], [0, 1]])))
        self.assertGreater(O[0][0], O[0][1])
        self.assertGreater(O[1][1], O[1][0])
        self.assertGreater(O[2][0], O[2][1])
        self.assertGreater(O[3][0], O[3][1])

    def test_train_xor(self):
        X_train = np.array([[1.0, 1.0], [0, 1.0], [1.0, 0], [0, 0]])
        Y_train = np.array([[1.0, 0], [0, 1], [0, 1], [1.0, 0]])
        success = False
        while not success:
            nn = LayeredNN([2, 2, 2])
            for i in range(120000):
                l = nn.loss(X_train, Y_train).round(15)
                nn.train(X_train, Y_train, learning_rate=0.1, numerical_gradient=False)
                self.debug_loss(i, l, interval=1000)
                if l <= 0.32:
                    success = True
                    break
        O = nn.predict(np.array([[1, 1], [0, 0], [1, 0], [0, 1]]))
        print(O)
        self.assertGreater(O[0][0], O[0][1])
        self.assertGreater(O[1][0], O[1][1])
        self.assertGreater(O[2][1], O[2][0])
        self.assertGreater(O[3][1], O[3][0])


class TestEmnistNN(unittest.TestCase):
    def setUp(self):
        self.X_train, self.Y_train, self.X_test, self.Y_test = load_mnist()
        print("X_train: ", self.X_train.shape)
        print("Y_train: ", self.Y_train.shape)
        self.X_train = self.X_train / 255.0
        self.X_test = self.X_test / 255.0

    def load_png(self, path):
        from PIL import Image
        im = Image.open(path, 'r')
        width, height = im.size
        pixel_values = list(im.getdata())
        pixel_values = np.array(pixel_values).reshape((width * height, 4))
        pixel_values = np.sum(pixel_values, axis=1)
        pixel_values = pixel_values.reshape(1, pixel_values.size) / 255.0 / 4
        return pixel_values

    def plot_image(self, pixel_values):
        pixel_values = pixel_values.reshape(28, 28)
        plt.imshow(pixel_values, interpolation='nearest')
        plt.draw()
        plt.pause(1000)

    def pick_mini_batch(self, i, batch_size=10):
        batch_mask = np.random.choice(self.X_train.shape[0], batch_size)
        X_batch = self.X_train[batch_mask]
        Y_batch = self.Y_train[batch_mask]
        return X_batch, Y_batch

    def debug_loss(self, i, l, interval=100):
        if i % interval == 0:
            print("loss: ", l)
            plt.plot(i, l, "ro", color="red")
            plt.draw()
            plt.pause(0.01)

    def debug_accuracy(self, i, nn, interval=100):
        if i % interval == 0:
            a = nn.accuracy(self.X_test, self.Y_test)
            plt.plot(i, a, "ro", color="blue")
            plt.draw()
            plt.pause(0.01)

    def test_train_emnist_train(self):
        nn = LayeredNN([784, 128, 64, 32, 10])
        for i in range(50000000):
            X_batch, Y_batch = self.pick_mini_batch(i, 64)
            l = nn.loss(X_batch, Y_batch)
            nn.train(X_batch, Y_batch, learning_rate=0.003)
            self.debug_loss(i, l, interval=100)
            self.debug_accuracy(i, nn, interval=1000)
            if i > 0 and i % 20000 == 0:
                nn.dump("./emnist_nn%d.pickle" % i)

    def test_my_handwrite(self):
        nn = LayeredNN.load("./emnist_nn60000.pickle")
        got = np.argmax(nn.predict(self.load_png("./samples/2a.png"))) + 1
        self.assertEqual(got, 2)
        got = np.argmax(nn.predict(self.load_png("./samples/5.png"))) + 1
        self.assertEqual(got, 5)
        got = np.argmax(nn.predict(self.load_png("./samples/6a.png"))) + 1
        self.assertEqual(got, 6)
        #got = np.argmax(nn.predict(self.load_png("./samples/7a.png"))) + 1
        # self.assertEqual(got, 7)


if __name__ == "__main__":
    unittest.main()
