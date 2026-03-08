CREATE IF NOT EXISTS DATABASE wasap;

CREATE TABLE IF NOT EXISTS usuarios (
	id SERIAL PRIMARY KEY,
	nombre VARCHAR(100) NOT NULL,
	apellido VARCHAR(100) NOT NULL,
	correo_electronico VARCHAR(100) UNIQUE NOT NULL,
	nombre_usuario VARCHAR(50) UNIQUE NOT NULL,
	contrasena VARCHAR(50) NOT NULL,
	fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS conversaciones (
    id BIGSERIAL PRIMARY KEY,
    tipo VARCHAR(10) NOT NULL CHECK (tipo IN ('privado', 'grupo')),
    nombre TEXT,
    creado_por BIGINT REFERENCES usuarios(id) ON DELETE SET NULL,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS participantes_conversacion (
    conversacion_id BIGINT REFERENCES conversaciones(id) ON DELETE CASCADE,
    usuario_id BIGINT REFERENCES usuarios(id) ON DELETE CASCADE,
    rol VARCHAR(10) DEFAULT 'miembro' CHECK (rol IN ('admin', 'miembro')),
    unido_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (conversacion_id, usuario_id)
);

CREATE TABLE IF NOT EXISTS mensajes (
    id BIGSERIAL PRIMARY KEY,
    conversacion_id BIGINT REFERENCES conversaciones(id) ON DELETE CASCADE,
    remitente_id BIGINT REFERENCES usuarios(id) ON DELETE SET NULL,
    contenido TEXT NOT NULL,
    enviado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS contactos (
    usuario_id INT REFERENCES usuarios(id) ON DELETE CASCADE,
    contacto_id INT REFERENCES usuarios(id) ON DELETE CASCADE,
    agregado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (usuario_id, contacto_id)
);