# app/models.py

from . import db


class Usuario(db.Model):
    __tablename__ = 'usuarios'

    ID_usuario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre_usuario = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    rol = db.Column(db.String, nullable=False)  # 'jefe_taller' o 'trabajador'


class RegistroProyectos(db.Model):
    __tablename__ = 'registro_proyectos'

    ID_proyecto = db.Column(db.Integer, primary_key=True, autoincrement=True)
    numero_proyecto = db.Column(db.String, unique=True, nullable=False)
    cliente_proyecto = db.Column(db.String, nullable=False)
    nombre_proyecto = db.Column(db.String, nullable=False)
    descripcion_proyecto = db.Column(db.String)
    eliminado = db.Column(db.Boolean, default=False, nullable=False)  # Nueva columna


class RegistroTrabajadores(db.Model):
    __tablename__ = 'registro_trabajadores'

    ID_trabajador = db.Column(db.Integer, primary_key=True, autoincrement=True)
    PIN_trabajador = db.Column(db.Integer, unique=True)
    nombre_trabajador = db.Column(db.String, nullable=False)
    apellido1_trabajador = db.Column(db.String, nullable=False)
    apellido2_trabajador = db.Column(db.String)
    eliminado = db.Column(db.Boolean, default=False, nullable=False)  # Nueva columna


class RegistroTareas(db.Model):
    __tablename__ = 'registro_tareas'

    ID_tarea = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fecha_hora = db.Column(db.String, nullable=False)
    ID_trabajador = db.Column(db.Integer, db.ForeignKey('registro_trabajadores.ID_trabajador'), nullable=False)
    ID_proyecto = db.Column(db.Integer, db.ForeignKey('registro_proyectos.ID_proyecto'), nullable=False)
    tarea = db.Column(db.String, nullable=False)
    horas = db.Column(db.Float, nullable=False)
    eliminado = db.Column(db.Boolean, default=False, nullable=False)  # Nueva columna


    trabajador = db.relationship('RegistroTrabajadores', backref='tareas')
    proyecto = db.relationship('RegistroProyectos', backref='tareas')   