"""
#!/usr/bin/env python
"""

from flask import Flask
from flask.ext.restful import Api

import os


from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand
from settings import DB_URI
from flask_sqlalchemy import SQLAlchemy


# Configuration
current_path = os.path.dirname(__file__)
client_path = os.path.abspath(os.path.join(current_path, 'static'))
application = Flask(__name__, static_url_path='', static_folder=client_path)
application.config['SQLALCHEMY_DATABASE_URI'] = DB_URI


     
db = SQLAlchemy(application)
migrate = Migrate(application, db)
manager = Manager(application)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
      manager.run()      