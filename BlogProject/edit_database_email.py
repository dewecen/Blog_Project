import sqlite3

connection = sqlite3.connect("sqlite.db", check_same_thread=False)
cursor = connection.cursor()

# Шаг 1: Добавление столбца без ограничения UNIQUE
cursor.execute('ALTER TABLE user ADD COLUMN email TEXT;')

# Шаг 2: Обновление значений в новом столбце
cursor.execute('UPDATE user SET email = "example@example.com" WHERE id = 1;')

# Шаг 3: Создание нового столбца с ограничением UNIQUE
cursor.execute('CREATE UNIQUE INDEX idx_user_email ON user(email);')

connection.commit()
connection.close()