# app/__init__.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
import os

db = SQLAlchemy()
csrf = CSRFProtect()

def create_app(config_name='DevelopmentConfig'):
    app = Flask(__name__)

    # Configuraciones según el entorno
    app.config.from_object(f'config.{config_name}')

    db.init_app(app)
    csrf.init_app(app)  # Iniciamos la protección CSRF

    # Importar y registrar las rutas
    from .routes import register_routes
    register_routes(app)

    return app
