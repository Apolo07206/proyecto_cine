import os
import secrets
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


@app.route('/mis-boletas')
@login_required
def mis_boletas():
    boletas = models.obtener_boletas_por_usuario(mysql, session['user_id'])
    return render_template('mis_boletas.html', boletas=boletas)


@app.route('/mis-boletas/cancelar/<int:id_boleta>', methods=['POST'])
@login_required
def cancelar_mi_boleta(id_boleta):
    boleta = models.obtener_boleta_detalle(mysql, id_boleta)
    if not boleta:
        flash('La boleta no existe.', 'error')
        return redirect(url_for('mis_boletas'))
    if boleta['id_usuario'] != session['user_id']:
        flash('No puedes cancelar una boleta ajena.', 'error')
        return redirect(url_for('mis_boletas'))
    if boleta['estado'] != 'pagada':
        flash('Esta boleta ya no está activa.', 'error')
        return redirect(url_for('mis_boletas'))
    models.cancelar_boleta(mysql, id_boleta)
    flash('Boleta cancelada. La silla quedó disponible y tu asiento fue liberado.', 'success')
    return redirect(url_for('mis_boletas'))


@app.route('/cancelar-compra', methods=['POST'])
@login_required
def cancelar_compra():
    id_funcion = request.form.get('id_funcion', type=int)
    asientos_raw = request.form.get('asientos', '')

    if not id_funcion or not asientos_raw:
        flash('No hay información de la compra a cancelar.', 'error')
        return redirect(url_for('mis_boletas'))

    funcion = models.obtener_funcion_por_id(mysql, id_funcion)
    if not funcion:
        flash('La función ya no existe.', 'error')
        return redirect(url_for('mis_boletas'))

    sala = models.obtener_sala_por_id(mysql, funcion['id_sala'])
    sillas = models.obtener_sillas_por_sala(mysql, sala['id_sala'])
    por_codigo = {f"{s['fila']}{s['columna']}": s for s in sillas}

    sillas_ids = []
    for codigo in [c.strip() for c in asientos_raw.split(',') if c.strip()]:
        silla = por_codigo.get(codigo)
        if silla:
            sillas_ids.append(silla['id_silla'])

    if not sillas_ids:
        flash('No se encontraron asientos válidos para cancelar.', 'error')
        return redirect(url_for('mis_boletas'))

    canceladas = models.cancelar_boletas_usuario(
        mysql, id_funcion, sillas_ids, session['user_id'])

    if canceladas:
        flash(f'Compra cancelada: {canceladas} boleto(s) anulado(s). '
              'Las sillas quedaron disponibles.', 'success')
    else:
        flash('No se encontraron boletos tuyos activos para cancelar.', 'error')
    return redirect(url_for('mis_boletas'))


@app.route('/recibo/<int:id_boleta>')
@login_required
def recibo(id_boleta):
    boleta = models.obtener_boleta_detalle(mysql, id_boleta)
    if not boleta:
        flash('La boleta no existe.', 'error')
        return redirect(url_for('mis_boletas'))
    if boleta['id_usuario'] != session['user_id']:
        flash('No tienes permiso para ver este recibo.', 'error')
        return redirect(url_for('mis_boletas'))
    if boleta['estado'] == 'cancelada':
        flash('Este boleto fue cancelado.', 'error')
        return redirect(url_for('mis_boletas'))
    return render_template('recibo.html', boleta=boleta, tipo_visual=tipo_visual)


PRECIOS = {'vip': 25000, 'estandar': 15000, 'preferencial': 12000}

def tipo_visual(tipo):
    return 'estandar' if tipo == 'general' else tipo


@app.route('/boletas')
@login_required
def seleccion_boletas():
    asientos_raw = request.args.get('asientos', '')
    id_funcion = request.args.get('id_funcion', type=int)

    if not asientos_raw or not id_funcion:
        flash('Debes seleccionar una función y sus asientos.', 'error')
        return redirect(url_for('mapa_silla'))

    funcion = models.obtener_funcion_por_id(mysql, id_funcion)
    if not funcion:
        flash('La función seleccionada ya no está disponible.', 'error')
        return redirect(url_for('mapa_silla'))

    sala = models.obtener_sala_por_id(mysql, funcion['id_sala'])
    sillas = models.obtener_sillas_por_sala(mysql, sala['id_sala'])
    por_codigo = {f"{s['fila']}{s['columna']}": s for s in sillas}

    asientos = []
    total = 0
    for codigo in asientos_raw.split(','):
        codigo = codigo.strip()
        if not codigo or codigo not in por_codigo:
            continue
        tipo = tipo_visual(por_codigo[codigo]['tipo'])
        precio = PRECIOS[tipo]
        asientos.append({'codigo': codigo, 'tipo': tipo, 'precio': precio})
        total += precio

    return render_template('seleccion_boletas.html', asientos=asientos,
                           asientos_raw=asientos_raw, total=total,
                           id_funcion=id_funcion, funcion=funcion, sala=sala)


@app.route('/mapa')
@login_required
def mapa_silla():
    funciones = models.obtener_funciones(mysql)
    id_funcion = request.args.get('id_funcion', type=int)

    filas = []
    funcion = None
    sala = None
    if id_funcion:
        funcion = models.obtener_funcion_por_id(mysql, id_funcion)
        if not funcion:
            flash('La función seleccionada no existe.', 'error')
            return render_template('mapa_silla.html', funciones=funciones,
                                   mapa_activo=False)
        sala = models.obtener_sala_por_id(mysql, funcion['id_sala'])
        sillas = models.obtener_sillas_por_sala(mysql, funcion['id_sala'])
        ocupadas = {r['id_silla'] for r in
                    models.obtener_sillas_ocupadas_por_funcion(mysql, id_funcion)}

        fila_actual = None
        for s in sillas:
            if fila_actual is None or fila_actual['letra'] != s['fila']:
                fila_actual = {'letra': s['fila'], 'sillas': []}
                filas.append(fila_actual)
            fila_actual['sillas'].append({
                'codigo': f"{s['fila']}{s['columna']}",
                'tipo': tipo_visual(s['tipo']),
                'ocupado': s['id_silla'] in ocupadas,
            })

    return render_template('mapa_silla.html', funciones=funciones, funcion=funcion,
                           sala=sala, filas=filas, mapa_activo=bool(id_funcion and funcion))


@app.route('/pago')
@login_required
def resumen_pago():
    asientos = request.args.get('asientos', '')
    total = request.args.get('total', '0')
    id_funcion = request.args.get('id_funcion', type=int)

    if not asientos or not id_funcion:
        flash('Compra incompleta. Vuelve a elegir tus asientos.', 'error')
        return redirect(url_for('mapa_silla'))

    return render_template('resumen_pago.html', asientos=asientos,
                           total=total, id_funcion=id_funcion)


@app.route('/procesar_pago', methods=['POST'])
@login_required
def procesar_pago():
    asientos_raw = request.form.get('asientos', '')
    id_funcion = request.form.get('id_funcion', type=int)

    if not asientos_raw or not id_funcion:
        flash('No hay asientos para comprar.', 'error')
        return redirect(url_for('mapa_silla'))

    funcion = models.obtener_funcion_por_id(mysql, id_funcion)
    if not funcion:
        flash('La función ya no está disponible.', 'error')
        return redirect(url_for('mapa_silla'))

    sala = models.obtener_sala_por_id(mysql, funcion['id_sala'])
    sillas = models.obtener_sillas_por_sala(mysql, sala['id_sala'])
    por_codigo = {f"{s['fila']}{s['columna']}": s for s in sillas}
    ocupadas = {r['id_silla'] for r in
                models.obtener_sillas_ocupadas_por_funcion(mysql, id_funcion)}

    codigos = [c.strip() for c in asientos_raw.split(',') if c.strip()]
    compradas = []
    total = 0
    for codigo in codigos:
        silla = por_codigo.get(codigo)
        if not silla:
            continue
        if silla['id_silla'] in ocupadas:
            flash(f'El asiento {codigo} ya fue ocupado por otra persona.', 'error')
            continue
        precio = PRECIOS[tipo_visual(silla['tipo'])]
        codigo_qr = f"CP-{id_funcion}-{silla['id_silla']}-{secrets.token_hex(4)}"
        models.crear_boleta(mysql, id_funcion, session['user_id'],
                            silla['id_silla'], 'general', precio, codigo_qr)
        compradas.append(codigo)
        total += precio

    if not compradas:
        flash('No se pudo confirmar la compra de ningún asiento.', 'error')
        return redirect(url_for('mapa_silla', id_funcion=id_funcion))

    return redirect(url_for('confirmacion', id_funcion=id_funcion,
                            asientos=','.join(compradas)))


@app.route('/confirmacion')
@login_required
def confirmacion():
    id_funcion = request.args.get('id_funcion', type=int)
    asientos_raw = request.args.get('asientos', '')

    if not id_funcion or not asientos_raw:
        flash('No hay información de la compra.', 'error')
        return redirect(url_for('usuario_panel'))

    funcion = models.obtener_funcion_por_id(mysql, id_funcion)
    sala = models.obtener_sala_por_id(mysql, funcion['id_sala'])
    sillas = models.obtener_sillas_por_sala(mysql, sala['id_sala'])
    por_codigo = {f"{s['fila']}{s['columna']}": s for s in sillas}

    detalles = []
    total = 0
    for codigo in [c.strip() for c in asientos_raw.split(',') if c.strip()]:
        silla = por_codigo.get(codigo)
        if not silla:
            continue
        tipo = tipo_visual(silla['tipo'])
        precio = PRECIOS[tipo]
        boleta = models.obtener_boleta_por_silla_funcion(mysql, id_funcion, silla['id_silla'])
        detalles.append({
            'codigo': codigo,
            'tipo': tipo,
            'precio': precio,
            'codigo_qr': boleta['codigo_qr'] if boleta else '',
        })
        total += precio

    return render_template('confirmacion.html', funcion=funcion, sala=sala,
                           detalles=detalles, total=total)


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


@app.route('/admin/salas', methods=['GET', 'POST'])
@role_required('admin')
def admin_salas():
    if request.method == 'POST':
        nombre = request.form['nombre']
        filas = int(request.form['filas'])
        columnas = int(request.form['columnas'])
        if models.sala_existe(mysql, nombre):
            flash('Ya existe una sala con ese nombre.', 'error')
        else:
            models.crear_sala_completa(mysql, nombre, filas, columnas)
            flash('Sala creada y sillas generadas correctamente.', 'success')
        return redirect(url_for('admin_salas'))
    salas = models.obtener_salas_con_total_sillas(mysql)
    return render_template('admin/salas.html', salas=salas)


@app.route('/admin/salas/eliminar/<int:id_sala>', methods=['POST'])
@role_required('admin')
def admin_eliminar_sala(id_sala):
    if models.sala_tiene_funciones(mysql, id_sala):
        flash('No se puede eliminar la sala: tiene funciones programadas.', 'error')
    else:
        models.eliminar_sala_con_sillas(mysql, id_sala)
        flash('Sala eliminada correctamente.', 'success')
    return redirect(url_for('admin_salas'))


@app.route('/admin/funciones', methods=['GET', 'POST'])
@role_required('admin')
def admin_funciones():
    if request.method == 'POST':
        if models.funcion_existe(mysql, request.form['sala'],
                                 request.form['fecha'], request.form['hora']):
            flash('Ya existe una función en esa sala a esa hora.', 'error')
        else:
            models.crear_funcion(mysql,
                request.form['pelicula'], request.form['sala'],
                request.form['fecha'], request.form['hora'], request.form['precio'])
            flash('Función guardada correctamente')
        return redirect(url_for('admin_funciones'))
    peliculas = models.obtener_peliculas_por_estado(mysql, 'cartelera')
    salas = models.obtener_salas(mysql)
    funciones = models.obtener_funciones(mysql)
    return render_template('admin/funciones.html', peliculas=peliculas,
                           salas=salas, funciones=funciones)


@app.route('/admin/funciones/eliminar/<int:id_funcion>', methods=['POST'])
@role_required('admin')
def eliminar_funcion(id_funcion):
    if models.eliminar_funcion(mysql, id_funcion):
        flash('Función eliminada')
    else:
        flash('No se puede eliminar: la función ya tiene boletas vendidas.', 'error')
    return redirect(url_for('admin_funciones'))


@app.route('/admin/reportes')
@role_required('admin')
def admin_reportes():
    resumen = models.obtener_resumen_ventas(mysql)
    funciones = models.obtener_funciones_para_reportes(mysql)
    id_funcion = request.args.get('id_funcion', type=int)
    filtro = request.args.get('correo', '').strip()

    boletas = []
    totales_funcion = None
    if id_funcion:
        boletas = models.obtener_boletas_con_detalles(mysql, id_funcion,
                                                      filtro or None)
        totales_funcion = models.obtener_totales_por_funcion(mysql, id_funcion)

    return render_template('admin/reportes.html', resumen=resumen, funciones=funciones,
                           id_funcion_seleccionada=id_funcion, boletas=boletas,
                           totales_funcion=totales_funcion, filtro=filtro)


if __name__ == '__main__':
    app.run(debug=True)