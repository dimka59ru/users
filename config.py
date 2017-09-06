import os

WTF_CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(os.path.dirname(__file__), 'users.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False