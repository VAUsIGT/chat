import os
from flask import Flask, render_template, request, redirect, make_response

app = Flask(__name__)

user_db={}

# Путь к директории, где будут сохраняться файлы данных пользователей
data_dir = os.path.join(os.getcwd(), 'user_data')

# Создание директории, если она не существует
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

# Функция для сохранения данных пользователя в текстовом файле
def save_user_data(username, data):
    file_path = os.path.join(data_dir, f'{username}.txt')
    with open(file_path, 'w') as file:
        file.write(data)


# Функция для загрузки данных пользователя из текстового файла
def load_user_data(username):
    file_path = os.path.join(data_dir, f'{username}.txt')
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        return None

@app.route('/save_data', methods=['POST'])
def save_data():
    username = request.form.get('username')
    data = request.form.get('data')
    save_user_data(username, data)
    return 'Data saved successfully!'

@app.route('/save_user', methods=['POST'])
def save_user():
    username = request.form.get('username')
    password = request.form.get('password')
    user_db[username] = {'username': username, 'password': password}
    save_user_data(username, str(user_db[username]))
    return 'User saved successfully!'

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Проверка наличия данных пользователя в текстовом файле
        if load_user_data(username) and user_db[username]['password'] == password:
            response = make_response(redirect('/profile'))
            response.set_cookie('current_user', username)
            return response
        else:
            return render_template('login.html', message='Неверное имя пользователя или пароль')
    return render_template('login.html')


@app.route('/logout')
def logout():
    response = make_response(redirect('/'))
    response.set_cookie('current_user', '', expires=0)
    return response


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    current_user = request.cookies.get('current_user')
    username = request.args.get('username')

    if username:
        if username in user_db:
            profile = user_db[username]
            return render_template('profile.html', current_user=current_user, profile=profile,
                                   is_current_user=current_user == username)
        else:
            return render_template('profile.html', current_user=current_user, message='Пользователь не найден')

    if current_user:
        profile = user_db[current_user]
        user_profiles = {username: user for username, user in user_db.items() if username != current_user}
        user_data = load_user_data(current_user)  # Загрузка данных пользователя из текстового файла
        return render_template('profile.html', current_user=current_user, profile=profile, user_profiles=user_profiles,
                               user_data=user_data)
    else:
        return redirect('/login')


@app.route('/update_profile', methods=['POST'])
def update_profile():
    current_user = request.cookies.get('current_user')
    if current_user:
        data = request.form['data']
        save_user_data(current_user, data)  # Сохранение данных пользователя в текстовый файл
    return redirect('/profile')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username not in user_db:
            user_db[username] = {'username': username, 'password': password}
            response = make_response(redirect('/login'))
            response.set_cookie('current_user', username)
            return response
        else:
            return render_template('register.html', message='Пользователь уже существует')
    return render_template('register.html')


if __name__ == '__main__':
    app.run()