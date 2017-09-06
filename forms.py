# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, TextAreaField
from wtforms.validators import InputRequired
from wtforms.fields.html5 import DateField


class AddUserForm(FlaskForm):
	first_name = StringField("Имя:", validators=[InputRequired(message="Имя обязательно для заполнения")], render_kw={"placeholder": "Имя"})
	last_name = StringField("Фамилия:", validators=[InputRequired(message="Фамилия обязательна для заполнения")], render_kw={"placeholder": "Фамилия"})
	date_of_birth = DateField("Дата рождения:", format='%Y-%m-%d',
								validators=[InputRequired(message="Дата обязательна для заполнения")],
							 render_kw={"placeholder": "ГГГГ-ММ-ДД",
							 			"pattern": "[0-9]{4}-(0[1-9]|1[012])-(0[1-9]|1[0-9]|2[0-9]|3[01])",
							 			"data-valid-example": "1988-04-23"
							 			})
	address = TextAreaField("Адрес:", validators=[InputRequired(message="Адрес обязателен для заполнения")], render_kw={"placeholder": "Адрес"})
	