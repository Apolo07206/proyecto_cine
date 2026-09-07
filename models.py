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

def obtener_sala_por_id(mysql, id_sala):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM sala WHERE id_sala = %s", (id_sala,))
    sala = cur.fetchone()
    cur.close()
    return sala

def sala_existe(mysql, nombre):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id_sala FROM sala WHERE nombre = %s", (nombre,))
    existe = cur.fetchone() is not None
    cur.close()
    return existe

def _letra_fila(indice, total_filas):
    return chr(ord('A') + total_filas - 1 - indice)

def _tipo_fila(indice, total_filas):
    if indice < 2:
        return 'vip'
    if indice >= total_filas - 2:
        return 'preferencial'
    return 'general'

def crear_sala_completa(mysql, nombre, filas, columnas):
    capacidad = filas * columnas
    cur = mysql.connection.cursor()
    try:
        cur.execute(
            "INSERT INTO sala (nombre, filas, columnas, capacidad_total) VALUES (%s, %s, %s, %s)",
            (nombre, filas, columnas, capacidad)
        )
        id_sala = cur.lastrowid
        for fila in range(filas):
            letra = _letra_fila(fila, filas)
            tipo = _tipo_fila(fila, filas)
            for columna in range(1, columnas + 1):
                cur.execute(
                    "INSERT INTO silla (id_sala, fila, columna, tipo) VALUES (%s, %s, %s, %s)",
                    (id_sala, letra, columna, tipo)
                )
        mysql.connection.commit()
    except Exception:
        mysql.connection.rollback()
        raise
    finally:
        cur.close()
    return id_sala

def obtener_salas_con_total_sillas(mysql):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT s.id_sala, s.nombre, s.filas, s.columnas, s.capacidad_total,
               COUNT(si.id_silla) AS total_sillas
        FROM sala s
        LEFT JOIN silla si ON si.id_sala = s.id_sala
        GROUP BY s.id_sala, s.nombre, s.filas, s.columnas, s.capacidad_total
        ORDER BY s.id_sala
    """)
    salas = cur.fetchall()
    cur.close()
    return salas

def sala_tiene_funciones(mysql, id_sala):
    """Bloquea el borrado de la sala solo si tiene funciones con boletas pagadas."""
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT f.id_funcion FROM funcion f
        JOIN boleta b ON b.id_funcion = f.id_funcion
        WHERE f.id_sala = %s AND b.estado = 'pagada'
    """, (id_sala,))
    tiene = cur.fetchone() is not None
    cur.close()
    return tiene

def eliminar_sala_con_sillas(mysql, id_sala):
    cur = mysql.connection.cursor()
    try:
        cur.execute("DELETE FROM silla WHERE id_sala = %s", (id_sala,))
        cur.execute("DELETE FROM sala WHERE id_sala = %s", (id_sala,))
        mysql.connection.commit()
    except Exception:
        mysql.connection.rollback()
        raise
    finally:
        cur.close()

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
    """Solo elimina la función si NO tiene boletas pagadas asociadas."""
    cur = mysql.connection.cursor()
    try:
        cur.execute("""
            DELETE FROM funcion
            WHERE id_funcion = %s
              AND NOT EXISTS (
                  SELECT 1 FROM boleta
                  WHERE boleta.id_funcion = funcion.id_funcion
                    AND boleta.estado = 'pagada'
              )
        """, (id_funcion,))
        mysql.connection.commit()
        exito = cur.rowcount > 0
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

def obtener_funciones_para_reportes(mysql):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT f.id_funcion, p.titulo AS pelicula, s.nombre AS sala,
               f.fecha, f.hora_inicio AS hora
        FROM funcion f
        JOIN pelicula p ON p.id_pelicula = f.id_pelicula
        JOIN sala s ON s.id_sala = f.id_sala
        ORDER BY f.fecha DESC, f.hora_inicio
    """)
    funciones = cur.fetchall()
    cur.close()
    return funciones


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

def obtener_boleta_por_silla_funcion(mysql, id_funcion, id_silla):
    cur = mysql.connection.cursor()
    cur.execute(
        """SELECT * FROM boleta
           WHERE id_funcion = %s AND id_silla = %s AND estado = 'pagada'
           ORDER BY id_boleta DESC LIMIT 1""",
        (id_funcion, id_silla)
    )
    boleta = cur.fetchone()
    cur.close()
    return boleta

def obtener_boletas_por_usuario(mysql, id_usuario):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT b.id_boleta, b.tipo_boleta, b.precio, b.fecha_compra, b.estado, b.codigo_qr,
               p.titulo AS pelicula, s.nombre AS sala,
               f.fecha, f.hora_inicio,
               CONCAT(si.fila, si.columna) AS silla,
               si.tipo AS tipo_silla
        FROM boleta b
        JOIN funcion f ON f.id_funcion = b.id_funcion
        JOIN pelicula p ON p.id_pelicula = f.id_pelicula
        JOIN sala s ON s.id_sala = f.id_sala
        JOIN silla si ON si.id_silla = b.id_silla
        WHERE b.id_usuario = %s
        ORDER BY b.fecha_compra DESC
    """, (id_usuario,))
    boletas = cur.fetchall()
    cur.close()
    return boletas

def obtener_boleta_detalle(mysql, id_boleta):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT b.id_boleta, b.tipo_boleta, b.precio, b.fecha_compra, b.estado, b.codigo_qr,
               b.id_usuario,
               COALESCE(u.nombre, 'Invitado') AS nombre_usuario,
               COALESCE(u.correo, 'No registrado') AS correo_usuario,
               p.titulo AS pelicula, p.clasificacion,
               s.nombre AS sala,
               f.fecha, f.hora_inicio,
               CONCAT(si.fila, si.columna) AS silla,
               si.tipo AS tipo_silla
        FROM boleta b
        JOIN funcion f ON f.id_funcion = b.id_funcion
        JOIN pelicula p ON p.id_pelicula = f.id_pelicula
        JOIN sala s ON s.id_sala = f.id_sala
        JOIN silla si ON si.id_silla = b.id_silla
        LEFT JOIN usuario u ON u.id_usuario = b.id_usuario
        WHERE b.id_boleta = %s
    """, (id_boleta,))
    boleta = cur.fetchone()
    cur.close()
    return boleta

def cancelar_boleta(mysql, id_boleta):
    cur = mysql.connection.cursor()
    cur.execute(
        "UPDATE boleta SET estado = 'cancelada' WHERE id_boleta = %s",
        (id_boleta,)
    )
    mysql.connection.commit()
    exito = cur.rowcount > 0
    cur.close()
    return exito

def cancelar_boletas_usuario(mysql, id_funcion, sillas_ids, id_usuario):
    cur = mysql.connection.cursor()
    if not sillas_ids:
        return 0
    formato = ','.join(['%s'] * len(sillas_ids))
    cur.execute(
        f"""UPDATE boleta SET estado = 'cancelada'
            WHERE id_funcion = %s AND id_usuario = %s AND estado = 'pagada'
              AND id_silla IN ({formato})""",
        (id_funcion, id_usuario, *sillas_ids)
    )
    mysql.connection.commit()
    cantidad = cur.rowcount
    cur.close()
    return cantidad

def obtener_resumen_ventas(mysql):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT COALESCE(SUM(CASE WHEN estado = 'pagada' THEN precio ELSE 0 END), 0) AS total_ingresos,
               SUM(CASE WHEN estado = 'pagada' THEN 1 ELSE 0 END) AS total_pagadas,
               SUM(CASE WHEN estado = 'cancelada' THEN 1 ELSE 0 END) AS total_canceladas
        FROM boleta
    """)
    resumen = cur.fetchone()
    cur.close()
    return resumen

def obtener_totales_por_funcion(mysql, id_funcion):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT COUNT(*) AS cantidad, COALESCE(SUM(precio), 0) AS ingreso
        FROM boleta
        WHERE id_funcion = %s AND estado = 'pagada'
    """, (id_funcion,))
    totales = cur.fetchone()
    cur.close()
    return totales

def obtener_boletas_con_detalles(mysql, id_funcion, filtro=None):
    cur = mysql.connection.cursor()
    if filtro:
        cur.execute("""
            SELECT b.id_boleta, b.tipo_boleta, b.precio, b.fecha_compra, b.estado, b.codigo_qr,
                   COALESCE(u.nombre, 'Invitado') AS usuario,
                   COALESCE(u.correo, 'No registrado') AS correo,
                   CONCAT(s.fila, s.columna) AS silla
            FROM boleta b
            JOIN silla s ON s.id_silla = b.id_silla
            LEFT JOIN usuario u ON u.id_usuario = b.id_usuario
            WHERE b.id_funcion = %s
              AND (COALESCE(u.correo, '') LIKE %s OR COALESCE(u.nombre, '') LIKE %s)
            ORDER BY b.fecha_compra DESC
        """, (id_funcion, f"%{filtro}%", f"%{filtro}%"))
    else:
        cur.execute("""
            SELECT b.id_boleta, b.tipo_boleta, b.precio, b.fecha_compra, b.estado, b.codigo_qr,
                   COALESCE(u.nombre, 'Invitado') AS usuario,
                   COALESCE(u.correo, 'No registrado') AS correo,
                   CONCAT(s.fila, s.columna) AS silla
            FROM boleta b
            JOIN silla s ON s.id_silla = b.id_silla
            LEFT JOIN usuario u ON u.id_usuario = b.id_usuario
            WHERE b.id_funcion = %s
            ORDER BY b.fecha_compra DESC
        """, (id_funcion,))
    boletas = cur.fetchall()
    cur.close()
    return boletas