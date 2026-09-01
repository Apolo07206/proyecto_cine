from flask import Flask , render_template , request, url_for , flash ,redirect
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


# --- MÓDULO CLIENTE ---

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/registro')
def registro():
    return render_template('registro.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/pelicula')
def detalle_pelicula():
    return render_template('detalle_pelicula.html')

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

@app.route('/admin/peliculas')
def admin_peliculas():
    return render_template('admin/peliculas.html')

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
