import sqlite3


connection = sqlite3.connect("sqlite.db")
cursor = connection.cursor()


cursor.execute('''
   CREATE TABLE comment (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       post_id INTEGER NOT NULL,
       user_id INTEGER NOT NULL,
       content TEXT NOT NULL,
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
       FOREIGN KEY (post_id) REFERENCES post (id),
       FOREIGN KEY (user_id) REFERENCES user (id) );
''')


connection.commit()
connection.close()
