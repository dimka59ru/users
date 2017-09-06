# -*- coding: utf-8 -*-
from flask import Flask, render_template, url_for, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from forms import AddUserForm
from flask_wtf.csrf import CSRFProtect
import sys
import os

# Для отображения русских символов (utf-8) на странице
reload(sys)
sys.setdefaultencoding("utf-8")

csrf = CSRFProtect()

app = Flask(__name__)
csrf.init_app(app)
app.config.from_object('config')

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20))
    last_name = db.Column(db.String(50))
    date_of_birth = db.Column(db.DateTime)
    address = db.Column(db.Text)


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


@app.route('/', methods=['GET'])
@app.route('/sort/<string:sort>', methods=['GET', 'POST'])
def index(sort=None):
    # главная страница    

    users = db_query(request.args.get('search_last_name'), request.args.get('sort'))

    return render_template('index.html', users=users)


@app.route('/add', methods=['GET', 'POST'])
def add():    
    form = AddUserForm()
    if form.validate_on_submit():
        user = User(first_name=form.first_name.data,
                    last_name=form.last_name.data,
                    date_of_birth=form.date_of_birth.data,
                    address=form.address.data)
        db.session.add(user)
        db.session.commit()
        flash('Успешно добавлен!')
        return redirect(url_for('index'))

    return render_template('add.html', form=form)


#@app.route('/edit/', methods=['GET', 'POST'])
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id=None):
    # редактирование пользователя    
    user = User.query.get(id)
    form = AddUserForm()         

    if form.validate_on_submit():
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.date_of_birth = form.date_of_birth.data
        user.address = form.address.data
        print user.first_name
        db.session.commit()
        flash('Успешно изменен!')
        return redirect(url_for('index'))
    else:        
        if user:
            form.first_name.data = user.first_name
            form.last_name.data = user.last_name
            form.date_of_birth.data = user.date_of_birth
            form.address.data = user.address  

    if user:
        return render_template('edit.html', user=user, form=form)
    else:
        return render_template('edit.html')


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
    # db.create_all()
    app.run(debug=True)
