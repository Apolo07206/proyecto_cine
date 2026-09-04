import os
from flask import Flask, render_template, request, url_for, flash, redirect, session
from flask_mysqldb import MySQL
from config import Config
import models
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps

app = Flask(__name__)
app.config.from_object(Config)
mysql = MySQL(app)

app.secret_key = 'eicwiemcumaehfppiwgqkvr'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'cine_premier'
app.config['MYSQL_UNIX_SOCKET'] = '/opt/lampp/var/mysql/mysql.sock'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# Deshabilitar la caché en el navegador para evitar volver atrás tras cerrar sesión
@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

# Decorador de autenticación
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Debes iniciar sesión para acceder a esta página.')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Debes iniciar sesión para acceder a esta página.')
                return redirect(url_for('login'))
            if session.get('rol') != role:
                flash('No tienes permiso para acceder a esta página.')
                return redirect(url_for('home'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# --- MÓDULO CLIENTE ---

@app.route('/')
def home():
    proximas = models.obtener_peliculas_por_estado(mysql, 'proxima')
    cartelera = models.obtener_peliculas_por_estado(mysql, 'cartelera')
    finalizadas = models.obtener_peliculas_por_estado(mysql, 'finalizada')
    return render_template('home.html', proximas=proximas, cartelera=cartelera, finalizadas=finalizadas)


@app.route('/detalle_pelicula/<int:id>')
def detalle_pelicula(id):
    pelicula = models.obtener_pelicula_por_id(mysql, id)
    return render_template('detalle_pelicula.html', pelicula=pelicula)


@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form['nombre']
        correo = request.form['correo']
        contrasena = request.form['contrasena']
        rol = request.form.get('rol', 'cliente')
        usuario_existente = models.obtener_usuario_por_correo(mysql, correo)
        
        if usuario_existente:
            flash('El correo ya está registrado. Inicia sesión.')
            return redirect(url_for('login'))
        else:
            contrasena_hash = generate_password_hash(contrasena)
            models.crear_usuario(mysql, nombre, correo, contrasena_hash, rol)
            flash('¡Registro exitoso! Ya puedes iniciar sesión.')
            return redirect(url_for('login'))
           
    return render_template('registro.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        correo = request.form['correo']
        contrasena = request.form['contrasena']

        usuario = models.obtener_usuario_por_correo(mysql, correo)

        if usuario and check_password_hash(usuario['contrasena'], contrasena):
            session['user_id'] = usuario['id_usuario']
            session['nombre'] = usuario['nombre']
            session['rol'] = usuario.get('rol', 'cliente')
            if session['rol'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('usuario_panel'))
        else:
            flash('Correo o contraseña incorrectos.')
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Has cerrado sesión correctamente.')
    return redirect(url_for('login'))


@app.route('/usuario')
@login_required
def usuario_panel():
    usuario = models.obtener_usuario_por_id(mysql, session['user_id'])
    return render_template('usuario.html', usuario=usuario)


@app.route('/boletas')
@login_required
def seleccion_boletas():
    return render_template('seleccion_boletas.html')


@app.route('/mapa')
@login_required
def mapa_silla():
    return render_template('mapa_silla.html')


@app.route('/pago')
@login_required
def resumen_pago():
    return render_template('resumen_pago.html')


@app.route('/confirmacion')
@login_required
def confirmacion():
    return render_template('confirmacion.html')


# --- MÓDULO ADMIN ---

@app.route('/admin')
@role_required('admin')
def admin_dashboard():
    return render_template('admin/dashboard.html')


@app.route('/admin/peliculas', methods=['GET', 'POST'])
@role_required('admin')
def admin_peliculas():
    if request.method == 'POST':
        titulo = request.form['titulo']
        genero = request.form['genero']
        clasificacion = request.form['clasificacion']
        duracion_minutos = request.form['duracion_minutos']
        sinopsis = request.form.get('sinopsis', '')
        estado = request.form.get('estado', 'proxima')

        poster = request.files.get('poster_url')
        poster_url = ''
        if poster and poster.filename:
            poster_url = poster.filename
            poster.save(os.path.join('static/img/posters', poster_url))

        models.crear_pelicula(mysql, titulo, genero, clasificacion,
                              duracion_minutos, sinopsis, poster_url, estado)
        flash('Película guardada correctamente')
        return redirect(url_for('admin_peliculas'))

    peliculas = models.obtener_peliculas(mysql)
    return render_template('admin/peliculas.html', peliculas=peliculas)


@app.route('/admin/peliculas/eliminar/<string:id_pelicula>', methods=['POST'])
@role_required('admin')
def eliminar(id_pelicula):
    models.eliminar_pelicula(mysql, id_pelicula)
    return redirect(url_for('admin_peliculas'))


@app.route('/admin/peliculas/editar/<string:id_pelicula>', methods=['GET'])
@role_required('admin')
def editar_pelicula_form(id_pelicula):
    pelicula = models.obtener_pelicula_por_id(mysql, id_pelicula)
    return render_template('admin/editar_pelicula.html', pelicula=pelicula)


@app.route('/admin/peliculas/editar/<string:id_pelicula>', methods=['POST'])
@role_required('admin')
def guardar_pelicula(id_pelicula):
    titulo = request.form['titulo']
    genero = request.form['genero']
    clasificacion = request.form['clasificacion']
    duracion_minutos = request.form['duracion_minutos']
    sinopsis = request.form.get('sinopsis', '')
    estado = request.form.get('estado', 'proxima')

    poster_url = models.obtener_pelicula_por_id(mysql, id_pelicula)['poster_url']
    poster = request.files.get('poster_url')
    if poster and poster.filename:
        poster_url = poster.filename
        poster.save(os.path.join('static/img/posters', poster_url))

    models.actualizar_pelicula(mysql, id_pelicula, titulo, genero, clasificacion,
                               duracion_minutos, sinopsis, poster_url, estado)
    flash('Película actualizada correctamente')
    return redirect(url_for('admin_peliculas'))


@app.route('/admin/salas')
@role_required('admin')
def admin_salas():
    return render_template('admin/salas.html')


@app.route('/admin/funciones')
@role_required('admin')
def admin_funciones():
    return render_template('admin/funciones.html')


@app.route('/admin/reportes')
@role_required('admin')
def admin_reportes():
    return render_template('admin/reportes.html')


if __name__ == '__main__':
    app.run(debug=True)