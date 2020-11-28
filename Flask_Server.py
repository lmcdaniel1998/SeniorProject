# author: Luke McDaniel
# project: Senior Project
# purpose: Defines context for database models
# description: Allows database to be accessed from the command line


from app import app, db
from app.models import User, Post


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post}
