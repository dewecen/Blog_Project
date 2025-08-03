# 1
from flask import Flask, render_template, request, redirect, url_for

from werkzeug.security import generate_password_hash, check_password_hash

from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

import sqlite3


app = Flask(__name__)
app.config['SECRET_KEY'] = 'key'

login_manager = LoginManager(app)
login_manager.login_view = 'login'
# 1///

# 2
class User(UserMixin): # описывает пользователя. логин, пароль

    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# закрывает соединение с базой
def close_db(connection=None):
    if connection is not None:
        connection.close()

# проверяет если пользователь лайкнул
def user_is_liking(user_id, post_id):
    connection = sqlite3.connect("sqlite.db")
    cursor = connection.cursor()
    like = cursor.execute(
        'SELECT * FROM like WHERE user_id = ? AND post_id = ?',
        (user_id, post_id)).fetchone()
    connection.close()  # Закрываем соединение
    return bool(like)  # возвращаем True или False
# 2///

# 3
@app.route('/like/<int:post_id>')
@login_required
def like_post(post_id):
    connection = sqlite3.connect("sqlite.db")
    cursor = connection.cursor()

    post = cursor.execute('SELECT * FROM post WHERE id = ?',
                          (post_id,)).fetchone()
    if post:
        if user_is_liking(current_user.id, post_id):
            cursor.execute(
                'DELETE FROM like WHERE user_id = ? AND post_id = ?',
                (current_user.id, post_id))
            connection.commit()
            print('You unliked this post.')
        else:
            cursor.execute(
                'INSERT INTO like (user_id, post_id) VALUES (?, ?)',
                (current_user.id, post_id))
            connection.commit()
            print('You liked this post!')
        return redirect(url_for('index'))  # обновление страницы
    connection.close()  # закрываем соединение
    return 'Post not found', 404  # вывод информации о ненайденном посте

@app.teardown_appcontext
def close_connection(exception):
    close_db()
# 3///

# 4
@app.route('/post/<post_id>/')
def post(post_id):
   connection = sqlite3.connect("sqlite.db")
   cursor = connection.cursor()

   # получаем пост
   post_result = cursor.execute(
       'SELECT post.id, post.title, post.content, user.username '
       'FROM post JOIN user ON post.author_id = user.id '
       'WHERE post.id = ?', (post_id,)
   ).fetchone()
   post_dict = {'id': post_result[0], 'title': post_result[1], 'content': post_result[2], 'username': post_result[3]}

   # получаем комментарии
   comments_result = cursor.execute(
       'SELECT comment.content, user.username, comment.created_at '
       'FROM comment JOIN user ON comment.user_id = user.id '
       'WHERE comment.post_id = ? ORDER BY comment.created_at ASC', (post_id,)
   ).fetchall()
   comments = [{'content': comment[0], 'username': comment[1], 'created_at': comment[2]} for comment in comments_result]

   connection.close()

   return render_template('post.html', post=post_dict, comments=comments)

# коментарии
@app.route('/comment/<int:post_id>/', methods=['POST'])
@login_required
def add_comment(post_id):
   content = request.form['content']
   connection = sqlite3.connect("sqlite.db")
   cursor = connection.cursor()


   cursor.execute(
       'INSERT INTO comment (post_id, user_id, content) VALUES (?, ?, ?)',
       (post_id, current_user.id, content) )
   connection.commit()
   connection.close()
   return redirect(url_for('post', post_id=post_id))
# 4///

# 5
@app.route('/edit/<int:post_id>/', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
   connection = sqlite3.connect("sqlite.db")
   cursor = connection.cursor()


   # проверка, что пост существует и принадлежит текущему пользователю
   post = cursor.execute(
       'SELECT * FROM post WHERE id = ? AND author_id = ?', (post_id, current_user.id)
   ).fetchone()
   if post is None:
       connection.close()
       return "Post not found or you don't have permission to edit it", 404


   if request.method == 'POST':
       # получаем новые данные из формы
       title = request.form['title']
       content = request.form['content']


       # Обновляем пост в базе данных
       cursor.execute(
           'UPDATE post SET title = ?, content = ? WHERE id = ?',
           (title, content, post_id)
       )
       connection.commit()
       connection.close()
       return redirect(url_for('index'))


   connection.close()
   return render_template('edit_post.html', post={'id': post[0], 'title': post[1], 'content': post[2]})
# 5///

# 6
@app.route("/")
def index():
    connection = sqlite3.connect("sqlite.db")
    cursor = connection.cursor()

    cursor.execute(''' 
        SELECT post.id, post.title, post.content, post.author_id, 
               user.username, COUNT(like.id) AS likes  
        FROM post  
        JOIN user ON post.author_id = user.id  
        LEFT JOIN like ON post.id = like.post_id 
        GROUP BY post.id, post.title, post.content, post.author_id, user.username 
    ''')
    result = cursor.fetchall()

    posts = []
    for post in reversed(result):
        posts.append({
            'id': post[0],
            'title': post[1],
            'content': post[2],
            'author_id': post[3],
            'username': post[4],
            'likes': post[5]
        })

        # если игрок авторизован, получаем список постов, которые он лайкнул
    liked_posts = []
    if current_user.is_authenticated:
        cursor.execute(
            'SELECT post_id FROM like WHERE user_id = ?', (current_user.id,)
        )
        likes_result = cursor.fetchall()
        liked_posts = [like[0] for like in likes_result]

    for post in posts:
        post['is_liked'] = post['id'] in liked_posts

    connection.close()
    context = {'posts': posts}
    return render_template('index.html', **context)
# 6///

# 7
@app.route('/add/' , methods = ['GET' , 'POST'])
@login_required
def add_post():
    connection = sqlite3.connect('sqlite.db')
    cursor = connection.cursor()

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        cursor.execute(
            'INSERT INTO post(title , content, author_id) VALUES (?,?,?)',
            (title, content, current_user.id)
        )
        connection.commit()
        return redirect(url_for('index'))
    return render_template('add_post.html')
# 7///

# 8
# register
@app.route('/register/', methods=['GET', 'POST'])
def register():
    connection = sqlite3.connect("sqlite.db")
    cursor = connection.cursor()
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email'] #дз
        password = request.form['password']
        try:
            cursor.execute('INSERT INTO user (username, password_hash,email) VALUES (?, ?, ?)',  #дз email
                           (username, generate_password_hash(password),email)              #дз email
                          )
            connection.commit()
            print('Регистрация пользователя прошла успешно')
            return render_template('register.html',message='Username registration successful')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            print('Username already exists!')
            return render_template('register.html',message='Username already exists!')
    return render_template('register.html')

@login_manager.user_loader
def load_user(user_id):
    connection = sqlite3.connect("sqlite.db")
    cursor = connection.cursor()
    user = cursor.execute(
        'SELECT * FROM user WHERE id = ?', (user_id,)).fetchone()
    if user is not None:
        return User(user[0], user[1], user[2])
    return None


@app.route('/login/', methods=['GET', 'POST'])
def login():
    connection = sqlite3.connect("sqlite.db")
    cursor = connection.cursor()

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = cursor.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user and User(user[0], user[1], user[2]).check_password(password):
            login_user(User(user[0], user[1], user[2]))
            return redirect(url_for('index'))
        else:
            return render_template('login.html', message='Invalid username or password')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
# 8///

# 9
@app.route('/delete/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    connection = sqlite3.connect("sqlite.db")
    cursor = connection.cursor()
    try:
        post = cursor.execute('SELECT * FROM post WHERE id = ?', (post_id,)).fetchone()
        if post and post[3] == current_user.id:
            cursor.execute('DELETE FROM post WHERE id = ?', (post_id,))
            connection.commit()  # зафиксировать изменения
        return redirect(url_for('index'))
    finally:
        connection.close()  # Закрываем соединение
# 9///

if __name__ == '__main__':
    app.run()