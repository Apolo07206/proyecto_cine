# models.py
import os

# --- USUARIO ---

def crear_usuario(mysql, nombre, correo, contrasena_hash, rol='cliente'):
    cur = mysql.connection.cursor()
    cur.execute(
        "INSERT INTO usuario (nombre, correo, contrasena, rol) VALUES (%s, %s, %s, %s)",
        (nombre, correo, contrasena_hash, rol)
    )
    mysql.connection.commit()
    cur.close()

def obtener_usuario_por_correo(mysql, correo):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM usuario WHERE correo = %s", (correo,))
    usuario = cur.fetchone()
    cur.close()
    return usuario

def obtener_usuario_por_id(mysql, id_usuario):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM usuario WHERE id_usuario = %s", (id_usuario,))
    usuario = cur.fetchone()
    cur.close()
    return usuario


# --- PELICULA ---

def crear_pelicula(mysql, titulo, genero, clasificacion, duracion_minutos, sinopsis, poster_url, estado='proxima'):
    cur = mysql.connection.cursor()
    cur.execute(
        """INSERT INTO pelicula (titulo, genero, clasificacion, duracion_minutos, sinopsis, poster_url, estado)
           VALUES (%s, %s, %s, %s, %s, %s, %s)""",
        (titulo, genero, clasificacion, duracion_minutos, sinopsis, poster_url, estado)
    )
    mysql.connection.commit()
    cur.close()

def crear_pelicula_con_poster(mysql, titulo, genero, clasificacion, duracion_minutos, sinopsis, poster_file, estado='proxima', upload_folder='static/img/posters'):
    poster_url = ''
    if poster_file and poster_file.filename:
        poster_url = poster_file.filename
        poster_file.save(os.path.join(upload_folder, poster_url))
    crear_pelicula(mysql, titulo, genero, clasificacion, duracion_minutos, sinopsis, poster_url, estado)
    return poster_url

def obtener_peliculas(mysql):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM pelicula")
    peliculas = cur.fetchall()
    cur.close()
    return peliculas

def obtener_peliculas_por_estado(mysql, estado):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM pelicula WHERE estado = %s", (estado,))
    peliculas = cur.fetchall()
    cur.close()
    return peliculas

def obtener_pelicula_por_id(mysql, id_pelicula):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM pelicula WHERE id_pelicula = %s", (id_pelicula,))
    pelicula = cur.fetchone()
    cur.close()
    return pelicula

def actualizar_pelicula(mysql, id_pelicula, titulo, genero, clasificacion, duracion_minutos, sinopsis, poster_url, estado):
    cur = mysql.connection.cursor()
    cur.execute(
        """UPDATE pelicula SET titulo=%s, genero=%s, clasificacion=%s, duracion_minutos=%s,
           sinopsis=%s, poster_url=%s, estado=%s WHERE id_pelicula=%s""",
        (titulo, genero, clasificacion, duracion_minutos, sinopsis, poster_url, estado, id_pelicula)
    )
    mysql.connection.commit()
    cur.close()

def eliminar_pelicula(mysql, id_pelicula):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM pelicula WHERE id_pelicula = %s", (id_pelicula,))
    mysql.connection.commit()
    cur.close()


# --- SALA ---

def crear_sala(mysql, nombre, filas, columnas, capacidad_total):
    cur = mysql.connection.cursor()
    cur.execute(
        "INSERT INTO sala (nombre, filas, columnas, capacidad_total) VALUES (%s, %s, %s, %s)",
        (nombre, filas, columnas, capacidad_total)
    )
    mysql.connection.commit()
    cur.close()

def obtener_salas(mysql):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM sala")
    salas = cur.fetchall()
    cur.close()
    return salas


# --- SILLA ---

def crear_silla(mysql, id_sala, fila, columna, tipo='general'):
    cur = mysql.connection.cursor()
    cur.execute(
        "INSERT INTO silla (id_sala, fila, columna, tipo) VALUES (%s, %s, %s, %s)",
        (id_sala, fila, columna, tipo)
    )
    mysql.connection.commit()
    cur.close()

def obtener_sillas_por_sala(mysql, id_sala):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM silla WHERE id_sala = %s", (id_sala,))
    sillas = cur.fetchall()
    cur.close()
    return sillas


# --- FUNCION ---

def crear_funcion(mysql, id_pelicula, id_sala, fecha, hora_inicio, precio_base):
    cur = mysql.connection.cursor()
    cur.execute(
        """INSERT INTO funcion (id_pelicula, id_sala, fecha, hora_inicio, precio_base)
           VALUES (%s, %s, %s, %s, %s)""",
        (id_pelicula, id_sala, fecha, hora_inicio, precio_base)
    )
    mysql.connection.commit()
    cur.close()

def obtener_funciones_por_pelicula(mysql, id_pelicula):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM funcion WHERE id_pelicula = %s", (id_pelicula,))
    funciones = cur.fetchall()
    cur.close()
    return funciones

def obtener_funciones(mysql):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT f.*, p.titulo, s.nombre AS nombre_sala
        FROM funcion f
        JOIN pelicula p ON p.id_pelicula = f.id_pelicula
        JOIN sala s ON s.id_sala = f.id_sala
        ORDER BY f.fecha, f.hora_inicio
    """)
    funciones = cur.fetchall()
    cur.close()
    return funciones

def eliminar_funcion(mysql, id_funcion):
    cur = mysql.connection.cursor()
    try:
        cur.execute("DELETE FROM funcion WHERE id_funcion = %s", (id_funcion,))
        mysql.connection.commit()
        exito = True
    except Exception:
        mysql.connection.rollback()
        exito = False
    finally:
        cur.close()
    return exito

def funcion_existe(mysql, id_sala, fecha, hora_inicio):
    cur = mysql.connection.cursor()
    cur.execute(
        """SELECT id_funcion FROM funcion
           WHERE id_sala = %s AND fecha = %s AND hora_inicio = %s""",
        (id_sala, fecha, hora_inicio)
    )
    existe = cur.fetchone() is not None
    cur.close()
    return existe

def obtener_funcion_por_id(mysql, id_funcion):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM funcion WHERE id_funcion = %s", (id_funcion,))
    funcion = cur.fetchone()
    cur.close()
    return funcion


# --- BOLETA ---

def obtener_sillas_ocupadas_por_funcion(mysql, id_funcion):
    """RF-13: sillas ya vendidas para esa función (para pintar el mapa)."""
    cur = mysql.connection.cursor()
    cur.execute(
        """SELECT id_silla FROM boleta
           WHERE id_funcion = %s AND estado != 'cancelada'""",
        (id_funcion,)
    )
    ocupadas = cur.fetchall()
    cur.close()
    return ocupadas

def crear_boleta(mysql, id_funcion, id_usuario, id_silla, tipo_boleta, precio, codigo_qr):
    cur = mysql.connection.cursor()
    cur.execute(
        """INSERT INTO boleta (id_funcion, id_usuario, id_silla, tipo_boleta, precio, codigo_qr)
           VALUES (%s, %s, %s, %s, %s, %s)""",
        (id_funcion, id_usuario, id_silla, tipo_boleta, precio, codigo_qr)
    )
    mysql.connection.commit()
    cur.close()

def obtener_boletas_por_funcion(mysql, id_funcion):
    """Para reportes (RF-10)."""
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM boleta WHERE id_funcion = %s", (id_funcion,))
    boletas = cur.fetchall()
    cur.close()
    return boletas