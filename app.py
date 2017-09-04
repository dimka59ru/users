# -*- coding: utf-8 -*-
from flask import Flask, render_template, url_for, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from os.path import expanduser
from datetime import datetime
import os
import sys

# Для отображения русских символов (utf-8) на странице
reload(sys)
sys.setdefaultencoding("utf-8")

app = Flask(__name__)
app.secret_key = 'some_secret'


# Для генерации уникальных ссылок на статичные файлы, чтоб не кэшировалось
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


# home = expanduser("~")
# db_uri = 'sqlite:////{}/users.db'.format(home)
# print db_uri

db_path = os.path.join(os.path.dirname(__file__), 'users.db')
db_uri = 'sqlite:///{}'.format(db_path)
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20))
    last_name = db.Column(db.String(50))
    date_of_birth = db.Column(db.DateTime)
    address = db.Column(db.Text)


@app.route('/')
def index():
    users = User.query.all()
    print users
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
            date_of_birth = datetime.strptime(request.form['date_of_birth'] , '%Y-%m-%d')
            address = request.form['address']

            user = User(first_name=first_name, last_name=last_name, date_of_birth=date_of_birth, address=address)
            db.session.add(user)
            db.session.commit()

            flash('Успешно добавлен!')
            return redirect(url_for('index'))

    return render_template('add.html', messages=messages)


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


if __name__ == '__main__':
    app.run(debug=True)
