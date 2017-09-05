# -*- coding: utf-8 -*-
from flask import Flask, render_template, url_for, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import sys

# Для отображения русских символов (utf-8) на странице
reload(sys)
sys.setdefaultencoding("utf-8")

DB_URI = 'sqlite:///' + os.path.join(os.path.dirname(__file__), 'users.db')

app = Flask(__name__)
app.secret_key = 'some_secret'
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI 
db = SQLAlchemy(app)


# Для генерации уникальных ссылок на статичные файлы, чтоб не кэшировались
@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)


def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                     endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)



class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20))
    last_name = db.Column(db.String(50))
    date_of_birth = db.Column(db.DateTime)
    address = db.Column(db.Text)


@app.route('/', methods=['GET'])
@app.route('/sort/<string:sort>', methods=['GET', 'POST'])
def index(sort=None):
    # главная страница
        
    users = db_query(request.args.get('search_last_name'), request.args.get('sort'))

    return render_template('index.html', users=users)


@app.route('/add', methods=['GET', 'POST'])
def add():
    messages = None
    # Если форма отправлена
    if request.method == "POST":
        messages = form_validated(request)

        # Если ошибок нет, то записываем данные в базу и делаем редирект на главную страницу
        if not messages:
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            date_of_birth = datetime.strptime(request.form['date_of_birth'], '%Y-%m-%d')
            address = request.form['address']

            user = User(first_name=first_name, last_name=last_name, date_of_birth=date_of_birth, address=address)
            db.session.add(user)
            db.session.commit()

            flash('Успешно добавлен!')
            return redirect(url_for('index'))

    return render_template('add.html', messages=messages)


# @app.route('/edit/')
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id=None):
    # редактирование пользователя
    user = User.query.get(id)
    return render_template('edit.html', user=user )


def form_validated(request):
    # Проверка формы. # Возврашает список ошибок
    messages = []
    if not request.form['first_name']:
        messages.append('Не указано имя.')
    if not request.form['last_name']:
        messages.append('Не указана фамилия.')
    if not request.form['date_of_birth']:
        messages.append('Не указана дата рождения.')
    if not request.form['address']:
        messages.append('Не указан адрес.')

    return messages


def db_query(last_name=None, sort=None):
    # выбор данных из базы с сортировкой и фильтрами
    # last_name принимает строку - фамилию, которую ищем в базе
    # sort принимает строку. В зависимости от значения строки,
    # сортировка происходит по разным полям

    users = []

    if last_name and not sort:

        # выборка с поиском по фамилии. сортировка по id                              
        users = User.query.order_by(User.id).filter(User.last_name.contains(last_name))

    elif last_name and sort:

        if sort == "lastname":
            # выборка с поиском по фамилии. сортировка по фамилии            
            users = User.query.filter(User.last_name.contains(last_name)).order_by(User.last_name)

        elif sort == "firstname":
            # выборка с поиском по фамилии. сортировка по имени           
            users = User.query.filter(User.last_name.contains(last_name)).order_by(User.first_name)

        elif sort == "id":
            # выборка с поиском по фамилии. сортировка по id          
            users = User.query.filter(User.last_name.contains(last_name)).order_by(User.id)
    
    elif not last_name and sort:

        if sort == "lastname":
            # выборка. сортировка по фамилии            
            users = User.query.order_by(User.last_name)

        elif sort == "firstname":
            # выборка. сортировка по имени           
            users = User.query.order_by(User.first_name)
        else:
            users = User.query.order_by(User.id)
    else:
        users = User.query.order_by(User.id)

    return users

if __name__ == '__main__':
    app.run(debug=True)
