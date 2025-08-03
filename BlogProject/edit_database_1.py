import sqlite3

# Подключение к базе данных
connection = sqlite3.connect("sqlite.db")
cursor = connection.cursor()

try:
    # Получаем список всех таблиц в базе данных
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    # Для каждой таблицы выбираем данные
    for table_name in tables:
        table_name = table_name[0]
        print(f"Таблица: {table_name}")

        # Выбираем все данные из таблицы
        cursor.execute(f"SELECT * FROM {table_name};")
        rows = cursor.fetchall()

        # Выводим данные в консоль
        for row in rows:
            print(row)
        print("\n")  # Пустая строка для разделения таблиц

except sqlite3.Error as e:
    print(f"Ошибка работы с базой данных: {e}")
finally:
    # Закрываем соединение
    connection.close()