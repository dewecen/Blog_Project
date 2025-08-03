import sqlite3

from werkzeug.security import generate_password_hash

connection = sqlite3.connect('sqlite.db', check_same_thread=False)
cursor = connection.cursor()

# cursor.execute('''
#     CREATE TABLE user (
#     id   integer primary key autoincrement,
#     username TEXT UNIQUE NOT NULL,
#     pasword_hash TEXT NOT NULL
#     );
#                ''')

cursor.execute('ALTER TABLE post ADD author_id INTEGER;')

cursor.execute('INSERT INTO user VALUES (?, ?, ?)',
    (1, 'defolpwin', generate_password_hash('querty123')))

connection.commit()
connection.close()