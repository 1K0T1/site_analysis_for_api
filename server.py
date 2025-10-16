import os
import asyncio
from time import time, ctime
from pathlib import Path
import logging

from flask import ( 
    Flask,                # основной класс приложения
    render_template,      # для рендеринга HTML-шаблонов
    request,              # доступ к данным запроса GET/POST
    redirect,             # перенаправление на другие маршруты
    url_for,              # генерация URL по имени функции
    jsonify,              # для возврата JSON-ответов
    make_response,        # для создания объектов ответа вручную
    session,              # хранение данных между запросами
    flash,                # временные сообщения для пользователя
    get_flashed_messages, # получение flash-сообщений
    g,                    # специальный объект для хранения данных в течение одного запроса
    send_file             # для скачивания файла клиенту
)
from flask_socketio import SocketIO, emit
from argon2 import PasswordHasher, exceptions
from dotenv import load_dotenv #для токенов

#отдельные функции
from gmail_restore import Restore_account
from data_sql import Data_base
from create_instructions_and_API import Instructions_API
from fileopen import Open_List, Open_File, Download_File
    
env_key = Path(__file__).parent / "key" / ".env"

load_dotenv(dotenv_path=env_key)

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
socketio = SocketIO(app, manage_session=False, async_mode='threading')
ph = PasswordHasher()

# убераем логирование socketio и engineio
logging.getLogger('engineio').setLevel(logging.ERROR)
logging.getLogger('socketio').setLevel(logging.ERROR)

# рендер 1 страницы
@app.route("/")
def index():
    return render_template("index.html")

#страница регистрации
@app.route("/register", methods=['POST', 'GET'])
def register():
    data_time = ctime() #дада регистрации
    answer = "" #что бы код не ломался
    login = None
    password = None
    email = None
    hash_password = None
    if request.method == "POST":
        login  = request.form.get("username")
        password = request.form.get("password")
        hash_password = ph.hash(password) #хешируем пароль
        email = request.form.get("email")
    print(f"Регистр{login, hash_password , email}")
    
    # если введен логин пароль и эмайл
    if login and password and email:
        regis = Data_base().registr(login, email)

        #проверка на такой же логин и почту в бд
        if regis is not None:
            if login == regis[0] or email == regis[2]:
                print("Такой пользователь уже есть")
                answer = "Такой пользователь уже есть"
        else:
            Data_base().add_users(login, hash_password, email, data_time)
            print("Зарегистрирован")
            answer = "Вы зарегистрированы"
    return render_template("register.html", name=login, password=password, email=email, message=answer)

# страница входа
@app.route("/login", methods=['POST', 'GET'])
def login():
    answer = "" #что бы код не ломался
    name = None
    password = None
    if request.method == "POST":
        name = request.form.get("username")
        password = request.form.get("password")
    print(f"Вход{name, password}")
    # если пароль и логин введены
    if name and password:
        pas = Data_base().login(name)
        print(pas)
        # проверка если пароль и логин введены правильно
        try:
            if pas is not None:
                passwords = pas[0]
                if ph.verify(passwords, password):
                    print(f'Авторизация')
                    answer = "Вы авторизированы"
                    session["name"] = name
                    return redirect(url_for("view_analysis_api", username=name))
            else:
                print("Не авторизация")
                answer = "Вы не авторизированы"
        except exceptions.VerificationError:
            answer = "Не верный пароль"
    return render_template("login.html", name=name, password=password, message=answer)

#отправка письма на почту
@app.route("/restore", methods=['POST', 'GET'])
def restore_gmail():
    email = None
    if request.method == "POST":
        email = request.form.get("email")
        if not email:
            print("Почта не введена")
        else:
            token = Data_base().restore_gmail(email)
            reset_link = url_for("restore_password", token=token, _external=True)
            #отправка на почту
            send_to_gmail = Restore_account(email, reset_link)
            send_to_gmail.restore_password()
    return render_template("restore_gmail.html", email=email)

#для тех кто забыл пароль :<
@app.route("/restore/password/<token>", methods=['POST', 'GET'])
def restore_password(token):
    password1 = None
    password2 = None
    hash_password = None
    if request.method == "POST":
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        print(f"Пароль 1: {password1} \nПароль 2: {password2}")
        if password1 == password2:
            hash_password = ph.hash(password1)
            tok = Data_base().restore_password(token, hash_password)
            print(tok)
    return render_template("restore_password.html", password1=password1, password2=password2, token=token)

#страница создания инструкций и api
@app.route("/view_analysis_api", methods=["GET", "POST", "DELETE"])
def view_analysis_api():
    name = session.get("name") 
    namein = f'Вы вошли как: {name}'
    link = None
    if request.method == "POST":
        link = request.form.get("buttonurl")
        session["link"] = link
        Instructions_API().open_resource(link, name)
    if request.method == "GET":
        links = None
    return render_template("view_analysis_api.html", message=namein)

# показывем список у клиента
@socketio.on('request_files')
def get_files():
    name = session.get("name") 
    files = Open_List().list_file(name)
    emit("update_files", files)

# показываем содержимое файла
@socketio.on('file_selected')
def view_file(filename):
    name = session.get("name") 
    open_file = Open_File().view_file(name, filename)
    emit('file_chosen', {'fileMessage': open_file})

#пользователь скачивает html файлы
@app.route("/view_analysis_api/html", methods=["GET", "POST"])
def download_html():
    name = session.get("name")
    path = Download_File().html_download(name)
    return send_file(path, as_attachment=True)

#пользователь скачивает js файлы 
@app.route("/view_analysis_api/js", methods=["GET", "POST"])
def download_js():
    name = session.get("name")
    path = Download_File().js_download(name)
    return send_file(path, as_attachment=True)

@app.route("/view_analysis_api/link", methods=["GET", "POST"])
def download_links():
    link = None
    name = session.get("name")
    link = session.get("link")
    path = Download_File().link_download(link, name)
    return send_file(path, as_attachment=True)

if __name__ == "__main__":
    cert_path = Path(__file__).parent / "pem" / r"localhost+2.pem" 
    key_path = Path(__file__).parent / "pem" / r"localhost+2-key.pem"
    socketio.run(app, debug=True, ssl_context=(cert_path, key_path)) #лог и самоподписанный сертификат 