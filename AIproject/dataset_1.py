#1
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Input
import os

#2
DATASET_PATH = 'dataset/'
num_classes = len(os.listdir(DATASET_PATH))  # Количество папок-классов
class_mode = "binary" if num_classes == 2 else "categorical"

#3
train_datagen = ImageDataGenerator(rescale=1 / 255, validation_split=0.2)

#4
train_data = train_datagen.flow_from_directory(
    DATASET_PATH, target_size=(128, 128), batch_size=32, class_mode=class_mode, subset="training"
)
val_data = train_datagen.flow_from_directory(
    DATASET_PATH, target_size=(128, 128), batch_size=32, class_mode=class_mode, subset="validation"
)

#5
model = Sequential([
    Input(shape=(128, 128, 3)),
    Conv2D(32, (3, 3), activation="relu"),
    MaxPooling2D(2, 2),

    Conv2D(64, (3, 3), activation="relu"),
    MaxPooling2D(2, 2),

    Conv2D(128, (3, 3), activation="relu"),
    MaxPooling2D(2, 2),

    Flatten(),
    Dense(256, activation="relu"),
    Dense(1, activation="sigmoid") if class_mode == "binary" else Dense(num_classes, activation="softmax")
])

#6
loss_function = "binary_crossentropy" if class_mode == "binary" else "categorical_crossentropy"
model.compile(optimizer="adam", loss=loss_function, metrics=["accuracy"])
model.fit(train_data, validation_data=val_data, epochs=10)
test_loss, test_accuracy = model.evaluate(val_data)

print(f"Точность модели на валидационных данных: {test_accuracy:.2f}")
model.save("image_classifier.h5")