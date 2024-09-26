# /run.py

import os
from app import create_app, db
from flask import Response, session

# Crear la aplicación con la configuración deseada
app = create_app(os.getenv('FLASK_ENV', 'DevelopmentConfig'))

# Clave secreta cargada desde una variable de entorno o una predeterminada
app.secret_key = os.getenv('SECRET_KEY', 'clave-secreta-predeterminada')

# Hacer la sesión permanente
@app.before_request
def make_session_permanent():
    session.permanent = True

## No están definidas las templates 404 y 500
#@app.errorhandler(404)
#def not_found_error(error):
#    return render_template('404.html'), 404
#
#@app.errorhandler(500)
#def internal_error(error):
#    return render_template('500.html'), 500

@app.after_request
def add_security_headers(response: Response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response


# Crear las tablas en la base de datos si no existen (solo en desarrollo)
with app.app_context():
    if os.getenv('FLASK_ENV') == 'DevelopmentConfig':
        db.create_all()

if __name__ == '__main__':
    # Ejecutar la aplicación en modo de depuración
    app.run(debug=(os.getenv('FLASK_ENV') == 'DevelopmentConfig'), host='192.168.1.138', port=5000)
