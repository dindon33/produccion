# /run.py

import os
from app import create_app, db

# Crear la aplicación con la configuración deseada
app = create_app(os.getenv('FLASK_ENV', 'DevelopmentConfig'))

# Clave secreta cargada desde una variable de entorno o una predeterminada
app.secret_key = os.getenv('SECRET_KEY', 'clave-secreta-predeterminada')

# Crear las tablas en la base de datos si no existen (solo en desarrollo)
with app.app_context():
    if os.getenv('FLASK_ENV') == 'DevelopmentConfig':
        db.create_all()

if __name__ == '__main__':
    # Ejecutar la aplicación en modo de depuración
    app.run(debug=(os.getenv('FLASK_ENV') == 'DevelopmentConfig'), host='192.168.1.138', port=5000)
