from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, IntegerField, TextAreaField, DecimalField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, NumberRange

class LoginForm(FlaskForm):
    username = StringField('Nombre de usuario', validators=[DataRequired(), Length(min=4, max=25)])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=6, max=35)])
    submit = SubmitField('Iniciar sesión')

class UsuarioForm(FlaskForm):
    nombre_usuario = StringField('Nombre de usuario', validators=[DataRequired(), Length(min=4, max=25)])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=6, max=35)])
    rol = SelectField('Rol', choices=[('jefe_taller', 'Jefe Taller'), ('otro_rol', 'Otro Rol')], validators=[DataRequired()])
    submit = SubmitField('Guardar usuario')

class TareaForm(FlaskForm):
    id_trabajador = SelectField('Trabajador', coerce=int, validators=[DataRequired()])
    id_proyecto = SelectField('Proyecto', coerce=int, validators=[DataRequired()])
    tarea = StringField('Tarea', validators=[DataRequired(), Length(max=100)])
    horas = DecimalField('Horas', validators=[DataRequired(), NumberRange(min=0)], places=2)
    submit = SubmitField('Registrar tarea')

class TrabajadorForm(FlaskForm):
    nombre_trabajador = StringField('Nombre', validators=[DataRequired(), Length(min=1, max=50)])
    apellido1_trabajador = StringField('Primer apellido', validators=[DataRequired(), Length(min=1, max=50)])
    apellido2_trabajador = StringField('Segundo apellido', validators=[Optional(), Length(max=50)])
    submit = SubmitField('Guardar trabajador')

class ProyectoForm(FlaskForm):
    numero_proyecto = StringField('Número de proyecto', validators=[DataRequired(), Length(max=50)])
    nombre_proyecto = StringField('Nombre de proyecto', validators=[DataRequired(), Length(max=100)])
    cliente_proyecto = StringField('Cliente', validators=[DataRequired(), Length(max=100)])
    descripcion_proyecto = TextAreaField('Descripción', validators=[Optional()])
    submit = SubmitField('Guardar proyecto')
