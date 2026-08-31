CREATE TABLE usuario (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(150) NOT NULL UNIQUE,
    contrasena VARCHAR(255) NOT NULL,
    rol ENUM('admin', 'taquillero', 'cliente') NOT NULL DEFAULT 'cliente',
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE pelicula (
    id_pelicula INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(150) NOT NULL,
    genero VARCHAR(50),
    clasificacion VARCHAR(10),
    duracion_minutos INT NOT NULL,
    sinopsis TEXT,
    poster_url VARCHAR(255),
    estado ENUM('cartelera', 'proxima', 'finalizada') NOT NULL DEFAULT 'proxima'
);

CREATE TABLE sala (
    id_sala INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    filas INT NOT NULL,
    columnas INT NOT NULL,
    capacidad_total INT NOT NULL
);

CREATE TABLE silla (
    id_silla INT AUTO_INCREMENT PRIMARY KEY,
    id_sala INT NOT NULL,
    fila VARCHAR(5) NOT NULL,
    columna INT NOT NULL,
    tipo ENUM('general', 'vip', 'preferencial') NOT NULL DEFAULT 'general',
    FOREIGN KEY (id_sala) REFERENCES sala(id_sala),
    UNIQUE (id_sala, fila, columna)
);

CREATE TABLE funcion (
    id_funcion INT AUTO_INCREMENT PRIMARY KEY,
    id_pelicula INT NOT NULL,
    id_sala INT NOT NULL,
    fecha DATE NOT NULL,
    hora_inicio TIME NOT NULL,
    precio_base DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (id_pelicula) REFERENCES pelicula(id_pelicula),
    FOREIGN KEY (id_sala) REFERENCES sala(id_sala)
);

CREATE TABLE boleta (
    id_boleta INT AUTO_INCREMENT PRIMARY KEY,
    id_funcion INT NOT NULL,
    id_usuario INT NULL,
    id_silla INT NOT NULL,
    tipo_boleta ENUM('general', 'nino', 'adulto_mayor') NOT NULL DEFAULT 'general',
    precio DECIMAL(10,2) NOT NULL,
    fecha_compra DATETIME DEFAULT CURRENT_TIMESTAMP,
    estado ENUM('pagada', 'cancelada', 'usada') NOT NULL DEFAULT 'pagada',
    codigo_qr VARCHAR(255) UNIQUE,
    FOREIGN KEY (id_funcion) REFERENCES funcion(id_funcion),
    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario) ON DELETE SET NULL,
    FOREIGN KEY (id_silla) REFERENCES silla(id_silla)
);
