# app/routes.py
import pandas as pd
from flask import render_template, request, redirect, url_for, send_file, Response, flash, session
from . import db
from .models import RegistroTareas, RegistroTrabajadores, RegistroProyectos, Usuario
from datetime import datetime, timedelta
from io import BytesIO
import random
from functools import wraps
import bcrypt
from werkzeug.security import generate_password_hash, check_password_hash  # Importación correcta




# Decorador para verificar que el usuario está logueado
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Debes iniciar sesión para acceder a esta página.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# Decorador para verificar que el usuario tiene el rol de jefe_taller
def jefe_taller_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'rol' not in session or session['rol'] != 'jefe_taller':
            flash('No tienes permisos para acceder a esta página.', 'error')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function


def register_routes(app):
    
    @app.route('/')
    def home():
        return render_template('base.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']

            # Buscar usuario en la base de datos
            usuario = Usuario.query.filter_by(nombre_usuario=username).first()

            if usuario and check_password_hash(usuario.password, password):  # Uso de check_password_hash
                # Almacenar información del usuario en la sesión
                session['usuario_id'] = usuario.ID_usuario
                session['rol'] = usuario.rol  # Guardar el rol en la sesión

                flash('Inicio de sesión exitoso', 'success')

                # Redirigir según el rol
                if usuario.rol == 'jefe_taller':
                    return redirect(url_for('home'))
                else:
                    return redirect(url_for('registro_tarea'))
            else:
                flash('Credenciales incorrectas', 'error')

        return render_template('login.html')

    @app.route('/logout')
    def logout():
        session.clear()  # Limpia toda la información de la sesión
        flash('Has cerrado sesión exitosamente.', 'success')
        return redirect(url_for('login'))

    @app.route('/gestionar_usuarios', methods=['GET', 'POST'])
    @login_required
    @jefe_taller_required  # Solo el Jefe de Taller puede acceder
    def gestionar_usuarios():
        if request.method == 'POST':
            nombre_usuario = request.form['nombre_usuario']
            password = request.form['password']
            rol = request.form['rol']

            # Encriptar la contraseña antes de guardarla
            hashed_password = generate_password_hash(password)  # Uso de generate_password_hash

            nuevo_usuario = Usuario(
                nombre_usuario=nombre_usuario,
                password=hashed_password,  # Guardar la contraseña encriptada
                rol=rol
            )
            db.session.add(nuevo_usuario)
            db.session.commit()
            flash('Usuario agregado con éxito', 'success')
            return redirect(url_for('gestionar_usuarios'))

        usuarios = Usuario.query.all()
        return render_template('gestionar_usuarios.html', usuarios=usuarios)
        

    @app.route('/editar_usuario/<int:id>', methods=['GET', 'POST'])
    @login_required
    @jefe_taller_required  # Solo el Jefe de Taller puede acceder
    def editar_usuario(id):
        usuario = Usuario.query.get_or_404(id)

        if request.method == 'POST':
            usuario.nombre_usuario = request.form['nombre_usuario']
            rol = request.form['rol']
            usuario.rol = rol

            # Si se proporciona una nueva contraseña, actualizarla
            if request.form['password']:
                usuario.password = generate_password_hash(request.form['password'])  # Uso de generate_password_hash

            db.session.commit()
            flash('Usuario actualizado con éxito', 'success')
            return redirect(url_for('gestionar_usuarios'))

        return render_template('editar_usuario.html', usuario=usuario)

    @app.route('/eliminar_usuario/<int:id>', methods=['POST'])
    @login_required
    @jefe_taller_required  # Solo el Jefe de Taller puede acceder
    def eliminar_usuario(id):
        usuario = Usuario.query.get(id)
        if usuario:
            db.session.delete(usuario)
            db.session.commit()
            flash('Usuario eliminado con éxito', 'success')
        else:
            flash('Usuario no encontrado', 'error')
        return redirect(url_for('gestionar_usuarios'))
    


    @app.route('/registro_tarea', methods=['GET', 'POST'])
    def registro_tarea():
        if request.method == 'POST':
            fecha_hora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            id_trabajador = request.form['id_trabajador']
            id_proyecto = request.form['id_proyecto']
            tarea = request.form['tarea']
            horas = request.form['horas']

            nueva_tarea = RegistroTareas(
                fecha_hora=fecha_hora,
                ID_trabajador=id_trabajador,
                ID_proyecto=id_proyecto,
                tarea=tarea,
                horas=horas
            )
            db.session.add(nueva_tarea)
            db.session.commit()

            # Obtener detalles del trabajador y del proyecto
            #trabajador = RegistroTrabajadores.query.get(id_trabajador)
            #proyecto = RegistroProyectos.query.get(id_proyecto)

            # Crear un mensaje flash con la información del registro
            mensaje_flash = (
                f'Registro guardado con éxito.\n'
                f'Trabajador: {id_trabajador} - \n'
                f'Proyecto: {id_proyecto} - \n'
                f'Tarea: {tarea} - \n'
                f'Horas: {horas}'
            )
            flash(mensaje_flash, 'success')
            return redirect(url_for('registro_tarea'))

        trabajadores = RegistroTrabajadores.query.filter_by(eliminado=False).all()
        proyectos = RegistroProyectos.query.filter_by(eliminado=False).all()
        return render_template('registro_tarea.html', trabajadores=trabajadores, proyectos=proyectos)

    @app.route('/visor_registros', methods=['GET'])
    @login_required
    @jefe_taller_required  # Solo el Jefe de Taller puede acceder
    def visor_registros():
        if request.args.get('reset'):
            return redirect(url_for('visor_registros'))

        trabajador_id = request.args.get('trabajador')
        proyecto_id = request.args.get('proyecto')
        tarea_filter = request.args.get('tarea', '').strip().lower()
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        horas = request.args.get('horas')
        horas_comparacion = request.args.get('horas_comparacion')

        query = RegistroTareas.query.filter_by(eliminado=False)

        if trabajador_id:
            query = query.filter_by(ID_trabajador=trabajador_id)
        if proyecto_id:
            query = query.filter_by(ID_proyecto=proyecto_id)
        if tarea_filter:
            query = query.filter(RegistroTareas.tarea.ilike(f'%{tarea_filter}%'))
        if fecha_inicio:
            query = query.filter(RegistroTareas.fecha_hora >= fecha_inicio)
        if fecha_fin:
            fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d') + timedelta(days=1)
            query = query.filter(RegistroTareas.fecha_hora < fecha_fin_dt)

        if horas:
            if horas_comparacion == 'igual':
                query = query.filter(RegistroTareas.horas == float(horas))
            elif horas_comparacion == 'mayor_igual':
                query = query.filter(RegistroTareas.horas >= float(horas))
            elif horas_comparacion == 'menor_igual':
                query = query.filter(RegistroTareas.horas <= float(horas))

        registros = query.all()
        num_registros = len(registros)
        total_horas = sum(registro.horas for registro in registros)

        trabajadores = RegistroTrabajadores.query.filter_by(eliminado=False).all()
        proyectos = RegistroProyectos.query.filter_by(eliminado=False).all()
        trabajador_completo = RegistroTrabajadores.query.get(trabajador_id) if trabajador_id else None
        proyecto_completo = RegistroProyectos.query.get(proyecto_id) if proyecto_id else None

        filtros_aplicados = {
            'trabajador': trabajador_completo,
            'proyecto': proyecto_completo,
            'tarea': tarea_filter,
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'horas': horas,
            'horas_comparacion': horas_comparacion
        }

        if request.args.get('exportar_excel'):
            registros = query.all()
            df = pd.DataFrame([{
                'ID Tarea': r.ID_tarea,
                'Fecha y Hora': r.fecha_hora,
                'Trabajador': f"{r.trabajador.nombre_trabajador} {r.trabajador.apellido1_trabajador}",
                'Proyecto': f"{r.proyecto.numero_proyecto} - {r.proyecto.cliente_proyecto} - {r.proyecto.nombre_proyecto}",
                'Tarea': r.tarea,
                'Horas': r.horas
            } for r in registros])
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Registros')
            output.seek(0)

            response = Response(output.getvalue(), 
                                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response.headers['Content-Disposition'] = 'attachment; filename=registros.xlsx'
            return response

        return render_template('visor_registros.html', 
                               registros=registros, 
                               trabajadores=trabajadores, 
                               proyectos=proyectos, 
                               filtros_aplicados=filtros_aplicados,
                               num_registros=num_registros, 
                               total_horas=total_horas)

    @app.route('/editar_registro/<int:id>', methods=['GET', 'POST'])
    @login_required
    @jefe_taller_required  # Solo el Jefe de Taller puede acceder
    def editar_registro(id):
        registro = RegistroTareas.query.get_or_404(id)

        if request.method == 'POST':
            registro.ID_trabajador = request.form['id_trabajador']
            registro.ID_proyecto = request.form['id_proyecto']
            registro.tarea = request.form['tarea']
            registro.horas = request.form['horas']

            db.session.commit()
            flash('Registro actualizado con éxito', 'success')
            return redirect(url_for('visor_registros'))

        trabajadores = RegistroTrabajadores.query.all()
        proyectos = RegistroProyectos.query.all()
        return render_template('editar_registro.html', registro=registro, trabajadores=trabajadores, proyectos=proyectos)

    @app.route('/eliminar_registro/<int:id>', methods=['POST'])
    @login_required
    @jefe_taller_required  # Solo el Jefe de Taller puede acceder
    def eliminar_registro(id):
        registro = RegistroTareas.query.get(id)
        if registro:
            registro.eliminado = True
            db.session.commit()
            flash('Registro eliminado con éxito', 'success')
        else:
            flash('Registro no encontrado', 'error')
        return redirect(url_for('visor_registros'))

    @app.route('/historial_registros')
    @login_required
    @jefe_taller_required  # Solo el Jefe de Taller puede acceder
    def historial_registros():
        registros_eliminados = RegistroTareas.query.filter_by(eliminado=True).all()
        return render_template('historial_registros.html', registros=registros_eliminados)

    @app.route('/recuperar_registro/<int:id>', methods=['POST'])
    @login_required
    @jefe_taller_required  # Solo el Jefe de Taller puede acceder
    def recuperar_registro(id):
        registro = RegistroTareas.query.get(id)
        if registro:
            registro.eliminado = False
            db.session.commit()
            flash('Registro recuperado con éxito', 'success')
        else:
            flash('Registro no encontrado', 'error')
        return redirect(url_for('visor_registros'))

    # Rutas para gestionar trabajadores
    @app.route('/gestionar_trabajadores', methods=['GET', 'POST'])
    @login_required
    @jefe_taller_required  # Solo el Jefe de Taller puede acceder
    def gestionar_trabajadores():
        if request.method == 'POST':
            nombre = request.form['nombre_trabajador']
            apellido1 = request.form['apellido1_trabajador']
            apellido2 = request.form['apellido2_trabajador'] or None

            # Generación automática del PIN
            pin = random.randint(1000, 9999)  # Genera un PIN de 4 a 6 dígitos

            nuevo_trabajador = RegistroTrabajadores(
                PIN_trabajador=pin,  # Asignamos el PIN generado
                nombre_trabajador=nombre,
                apellido1_trabajador=apellido1,
                apellido2_trabajador=apellido2,
                eliminado=False
            )
            db.session.add(nuevo_trabajador)
            db.session.commit()
            flash('Trabajador agregado con éxito', 'success')
            return redirect(url_for('gestionar_trabajadores'))

        trabajadores = RegistroTrabajadores.query.filter_by(eliminado=False).all()
        return render_template('gestionar_trabajadores.html', trabajadores=trabajadores)

    @app.route('/editar_trabajador/<int:id>', methods=['GET', 'POST'])
    @login_required
    @jefe_taller_required  # Solo el Jefe de Taller puede acceder
    def editar_trabajador(id):
        trabajador = RegistroTrabajadores.query.get_or_404(id)

        if request.method == 'POST':
            trabajador.nombre_trabajador = request.form['nombre_trabajador']
            trabajador.apellido1_trabajador = request.form['apellido1_trabajador']
            trabajador.apellido2_trabajador = request.form['apellido2_trabajador']
            db.session.commit()
            flash('Trabajador actualizado con éxito', 'success')
            return redirect(url_for('gestionar_trabajadores'))

        return render_template('editar_trabajador.html', trabajador=trabajador)

    @app.route('/eliminar_trabajador/<int:id>', methods=['POST'])
    @login_required
    @jefe_taller_required  # Solo el Jefe de Taller puede acceder
    def eliminar_trabajador(id):
        trabajador = RegistroTrabajadores.query.get(id)
        if trabajador:
            trabajador.eliminado = True
            db.session.commit()
            flash('Trabajador eliminado con éxito', 'success')
        else:
            flash('Trabajador no encontrado', 'error')
        return redirect(url_for('gestionar_trabajadores'))

    @app.route('/historial_trabajadores')
    @login_required
    @jefe_taller_required  # Solo el Jefe de Taller puede acceder
    def historial_trabajadores():
        trabajadores_eliminados = RegistroTrabajadores.query.filter_by(eliminado=True).all()
        return render_template('historial_trabajadores.html', trabajadores=trabajadores_eliminados)

    @app.route('/recuperar_trabajador/<int:id>', methods=['POST'])
    @login_required
    @jefe_taller_required  # Solo el Jefe de Taller puede acceder
    def recuperar_trabajador(id):
        trabajador = RegistroTrabajadores.query.get(id)
        if trabajador:
            trabajador.eliminado = False
            db.session.commit()
            flash('Trabajador recuperado con éxito', 'success')
        else:
            flash('Trabajador no encontrado', 'error')
        return redirect(url_for('gestionar_trabajadores'))

    # Rutas para gestionar proyectos
    @app.route('/gestionar_proyectos', methods=['GET', 'POST'])
    @login_required
    @jefe_taller_required  # Solo el Jefe de Taller puede acceder
    def gestionar_proyectos():
        if request.method == 'POST':
            numero_proyecto = request.form['numero_proyecto']
            nombre_proyecto = request.form['nombre_proyecto']
            cliente_proyecto = request.form['cliente_proyecto']
            descripcion_proyecto = request.form['descripcion_proyecto']

            nuevo_proyecto = RegistroProyectos(
                numero_proyecto=numero_proyecto,
                nombre_proyecto=nombre_proyecto,
                cliente_proyecto=cliente_proyecto,
                descripcion_proyecto=descripcion_proyecto,
                eliminado=False
            )
            db.session.add(nuevo_proyecto)
            db.session.commit()
            flash('Proyecto agregado con éxito', 'success')
            return redirect(url_for('gestionar_proyectos'))

        proyectos = RegistroProyectos.query.filter_by(eliminado=False).all()
        return render_template('gestionar_proyectos.html', proyectos=proyectos)

    @app.route('/editar_proyecto/<int:id>', methods=['GET', 'POST'])
    @login_required
    @jefe_taller_required  # Solo el Jefe de Taller puede acceder
    def editar_proyecto(id):
        proyecto = RegistroProyectos.query.get_or_404(id)

        if request.method == 'POST':
            proyecto.nombre_proyecto = request.form['nombre_proyecto']
            proyecto.cliente_proyecto = request.form['cliente_proyecto']
            proyecto.numero_proyecto = request.form['numero_proyecto']
            proyecto.descripcion_proyecto = request.form['descripcion_proyecto']

            db.session.commit()
            flash('Proyecto actualizado con éxito', 'success')
            return redirect(url_for('gestionar_proyectos'))

        return render_template('editar_proyecto.html', proyecto=proyecto)

    @app.route('/eliminar_proyecto/<int:id>', methods=['POST'])
    @login_required
    @jefe_taller_required  # Solo el Jefe de Taller puede acceder
    def eliminar_proyecto(id):
        proyecto = RegistroProyectos.query.get(id)
        if proyecto:
            proyecto.eliminado = True
            db.session.commit()
            flash('Proyecto eliminado con éxito', 'success')
        else:
            flash('Proyecto no encontrado', 'error')
        return redirect(url_for('gestionar_proyectos'))

    @app.route('/historial_proyectos')
    @login_required
    @jefe_taller_required  # Solo el Jefe de Taller puede acceder
    def historial_proyectos():
        proyectos_eliminados = RegistroProyectos.query.filter_by(eliminado=True).all()
        return render_template('historial_proyectos.html', proyectos=proyectos_eliminados)

    @app.route('/recuperar_proyecto/<int:id>', methods=['POST'])
    @login_required
    @jefe_taller_required  # Solo el Jefe de Taller puede acceder
    def recuperar_proyecto(id):
        proyecto = RegistroProyectos.query.get(id)
        if proyecto:
            proyecto.eliminado = False
            db.session.commit()
            flash('Proyecto recuperado con éxito', 'success')
        else:
            flash('Proyecto no encontrado', 'error')
        return redirect(url_for('gestionar_proyectos'))
