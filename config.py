# author: Luke McDaniel
# project: Senior Project
# purpose: Sets up server file structure
# description: creates the config class. This class contains the
# secret key which is used to encrypt user passwords.
# server database is defined here as well.


import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
