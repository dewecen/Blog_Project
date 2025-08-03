import tensorflow as tf
from tensorflow.keras.datasets import fashion_mnist
import matplotlib.pyplot as plt
import random

model = tf.keras.models.load_model('fashion_mnist_model.h5')

(_, _), (x_test, y_test), = fashion_mnist.load_data()
x_test = x_test / 255.0
# x_test = x_test.reshape(-1, 28, * 28)

class_names = ['T-shirt/top', 'Trouser', 'Pullover', 'Dress', 'Coat',
               'Sandal', 'Shirt', 'Sneaker', 'Bag', 'Ankle boot']

# Функция предсказания и отображения изображения
def predict_image(index):
    img = x_test[index] # изображение по индексу
    img_exanded = img.reshape(1, 28, 28) # размерность
    predictions = model.predict(img_exanded) # предсказание
    predicted_class = predictions[0].argmax() # индекс класса
    confidence = predictions[0][predicted_class] * 100 # уверенность в %
    plt.imshow(img, cmap="gray")
    plt.title(f'предсказано: {class_names[predicted_class]}({confidence: 2f}%)\n'
              f'Истинный класс: {class_names[y_test[index]]}')
    plt.axis('off')
    plt.show()

random_index = random.randint(0, len(x_test) - 1)
predict_image(random_index)