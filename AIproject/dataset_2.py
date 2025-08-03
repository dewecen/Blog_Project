#1
import tensorflow as tf
from PIL import Image
import cv2
import os
import matplotlib.pyplot as plt

DATASET_PATH = 'dataset/'
num_classes = len(os.listdir(DATASET_PATH))  # Количество папок-классов
class_mode = "binary" if num_classes == 2 else "categorical"

#2
def predict_image(image_path):

#3
    if not os.path.exists(image_path):
        print(f"Ошибка: Файл не найден по пути: {image_path}")
        return
    try:
        img = Image.open(image_path)
        img.verify()  # Проверка повреждений
        img = Image.open(image_path)  # Повторное открытие
    except (OSError, IOError):
        print(f"Ошибка: Поврежденное изображение - {image_path}")
        return

#4
    model = tf.keras.models.load_model("image_classifier.h5")
    img = cv2.imread(image_path)

    if img is None:
        print(f"Ошибка: Не удалось прочитать изображение - {image_path}")
        return
    img = cv2.resize(img, (128, 128))  #изменение размер под модель
    img = img / 255  # Нормализация
    img = tf.expand_dims(img, axis=0)

#5
    prediction = model.predict(img)
    class_names = os.listdir(DATASET_PATH)  # Берем названия папок-классов
    if class_mode == "binary":
        predicted_class = class_names[int(bool(prediction[0] > 0.5))]
    else:
        predicted_class = class_names[tf.argmax(prediction, axis=-1).numpy()[0]]

#6
    print(f"Модель определила: {predicted_class}")
    # Визуализируем результат
    img = Image.open(image_path)
    plt.imshow(img)
    plt.title(f"Модель определила: {predicted_class}")
    plt.axis('off')
    plt.show()

#7
predict_image('cat.jpg')
predict_image('dog.jpg')
predict_image('pig.png')