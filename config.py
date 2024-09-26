# /config.py

import os
from datetime import timedelta

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'clave-secreta-predeterminada')
    WTF_CSRF_ENABLED = True
    SESSION_COOKIE_HTTPONLY = True  # Evita que las cookies de sesión sean accesibles por JS
    SESSION_COOKIE_SAMESITE = 'Lax'  # Evita el envío de cookies en peticiones de terceros
    REMEMBER_COOKIE_DURATION = timedelta(days=7)  # Duración de la cookie 'remember me'
    SESSION_PROTECTION = 'strong'
    SEND_FILE_MAX_AGE_DEFAULT = timedelta(days=30)

class DevelopmentConfig(Config):
    DEBUG = True
    BASEDIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASEDIR, 'clientes/catel.db')}"
    SESSION_COOKIE_SECURE = False  # Solo True en producción
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=600)  # Duración de la sesión

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///production.db')
    SESSION_COOKIE_SECURE = True  # Solo se permite por HTTPS
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=600)  # Duración de la sesión en producción
