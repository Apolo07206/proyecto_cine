import os
from flask import Flask, render_template, request, url_for, flash, redirect
from flask_mysqldb import MySQL
from config import Config
import models




app=Flask(__name__)
app.config.from_object(Config)
mysql=MySQL(app)


app.secret_key='eicwiemcumaehfppiwgqkvr'


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] =''
app.config['MYSQL_DB'] ='cine_premier'
app.config['MYSQL_UNIX_SOCKET'] = '/opt/lampp/var/mysql/mysql.sock'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'







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


@app.route('/registro' ,methods=['GET','POST'])
def registro():
    if request.method=='POST':
        nombre=request.form['nombre']
        correo=request.form['correo']
        contraseña=request.form['contrasena']
        rol = request.form.get('rol', 'cliente')

        print(nombre , correo ,contraseña,rol)

        flash('¡Registro exitoso! Ya puedes iniciar sesión.')
        return redirect(url_for('login'))
           
    return render_template('registro.html')
    

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/boletas')
def seleccion_boletas():
    return render_template('seleccion_boletas.html')

@app.route('/mapa')
def mapa_silla():
    return render_template('mapa_silla.html')

@app.route('/pago')
def resumen_pago():
    return render_template('resumen_pago.html')

@app.route('/confirmacion')
def confirmacion():
    return render_template('confirmacion.html')


# --- MÓDULO ADMIN ---

@app.route('/admin')
def admin_dashboard():
    return render_template('admin/dashboard.html')




@app.route('/admin/peliculas', methods=['GET', 'POST'])
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
        flash('Pelicula guardada correctamente')
        return redirect(url_for('admin_peliculas'))

    peliculas = models.obtener_peliculas(mysql)
    return render_template('admin/peliculas.html', peliculas=peliculas)




@app.route('/admin/peliculas/eliminar/<string:id_pelicula>', methods=['POST'])
def eliminar(id_pelicula):
    models.eliminar_pelicula(mysql, id_pelicula)
    return redirect(url_for('admin_peliculas'))


@app.route('/admin/peliculas/editar/<string:id_pelicula>', methods=['GET'])
def editar_pelicula_form(id_pelicula):
    pelicula = models.obtener_pelicula_por_id(mysql, id_pelicula)
    return render_template('admin/editar_pelicula.html', pelicula=pelicula)


@app.route('/admin/peliculas/editar/<string:id_pelicula>', methods=['POST'])
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
    flash('Pelicula actualizada correctamente')
    return redirect(url_for('admin_peliculas'))





@app.route('/admin/salas')
def admin_salas():
    return render_template('admin/salas.html')

@app.route('/admin/funciones')
def admin_funciones():
    return render_template('admin/funciones.html')

@app.route('/admin/reportes')
def admin_reportes():
    return render_template('admin/reportes.html')


if __name__ == '__main__':
    app.run(debug=True)