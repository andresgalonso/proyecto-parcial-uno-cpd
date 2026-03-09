# Proyecto paracial uno 
---
## Integrantes

- Emiliano Piñon Marín 367860
- Luisa Fernanda Hernández Hernández 368068
- Andrés Gonzales Alonso 367600
- Mauricio Elías Navarrete Flores 367785

---
## Tabla de contenidos
1. [Descripción General](#descripción-general)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Tecnologías Utilizadas](#tecnologías-utilizadas)
4. [Funcionalidades](#funcionalidades)
5. [Protocolos](#protocolos)
6. [Base de Datos](#base-de-datos)

---
## Descripción General
Se desarrolló una aplicación de mensajería web desarrollada con Flask y SocketIO. Permite a usuarios registrados comunicarse en tiempo real mediante chats privados y grupos. El sistema consta de dos componentes principales:

- **Aplicación Web (`app.py`):** Consta de un servidor Flask con soporte para Socket.IO que gestiona las diferentes funcionalidades.

Cada vez que un cliente se conecta, el servidor le asigna un contexto de ejecución independiente. Esto permite que el servidor atienda múltiples conexiones simultáneamente sin que una bloquee a la otra.

---
## Arquitectura del Sistema
El flujo de mensajes se describe bajo la siguiente secuencia: 
1. El cliente emite el evento `send_message` vía Socket.IO.
2. El servidor lanza un hilo  (`threading.Thread`) para escribir en la base de datos sin bloquear el servidor.
3. Un mutex (`db_lock`) protege el acceso concurrente a la base de datos.
4. Una vez guardado, el servidor emite el evento `nuevo_mensaje` a todos los clientes conectados mediante broadcast.

---
## Tecnologías Utilizadas
| Tecnología | Propósito |
|---|---|
| Python | Lenguaje principal del backend |
| Flask-SocketIO | Comunicación en tiempo real utilizando WebSockets |
| PostgreSQL| Base de datos relacional |
| Bootstrap | Framework CSS para UI |

---
## Funcionalidades
### 1. Registro de Usuario
Los nuevos usuarios pueden crear una cuenta proporcionando:
- Nombre y apellido
- Correo electrónico único
- Nombre de usuario único
- Contraseña
- Confirmación de contraseña

El formulario realiza una petición `POST /register` con los datos en formato JSON. El servidor valida el correo y nombre de usuario antes de insertar en la base de datos.
### 2. Inicio de Sesión
La autenticación se realiza mediante WebSocket (evento `login`). El flujo se explica mediante los siguientes pasos:

1. El usuario ingresa su nombre de usuario y contraseña.
2. El cliente emite el evento `login` vía Socket.IO.
3. El servidor consulta la base de datos y devuelve `login_response`.
4. Si es exitoso, el `nombre_usuario` se guarda en `localStorage`.

### 3. Chat Privado
Permite enviar mensajes directos entre dos usuarios registrados. Se puede iniciar un nuevo chat buscando el usuario en la barra de búsqueda. Enviar el primer mensaje creara automáticamente la conversación en la base de datos. En caso de continuar conversaciones previas, los mensajes históricos se cargan desde la base de datos.

### 4. Chat Grupal
Los usuarios pueden crear grupos de conversación con múltiples participantes. El flujo para crear un grupo se detalla con los siguientes pasos: 

1. Acceder al menú  más opciones en la barra.
2. Seleccionar "Crear grupo".
3. Ingresar el nombre del grupo.
4. Ingresar los nombres de usuario de los miembros separados por coma.

Un chat grupal tiene el mismo comportamiento que aquellos chats de dos participantes.
## Protocolos
En este trabajo se utilizo HTTP, utilizando POST y GET
### Rutas HTTP
| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/` | Redirige a la pantalla de login |
| `GET` | `/login` | Renderiza la página de login |
| `GET` | `/register` | Renderiza la página de registro |
| `POST` | `/register` | Registra un nuevo usuario (JSON) |
| `GET` | `/chat-plantilla` | Renderiza la interfaz principal del chat |

Se utilizó WebSockets, que es un protocolo de capa de aplicación que mantiene una conexión persistente y bidireccional sobre TCP. Esto garantiza que los mensajes lleguen en orden y sin errores. 

### Eventos de Socket.IO — Emitidos por el Cliente

| Evento | Contenido | Descripción |
|---|---|---|
| `login` | `{ username, password }` | Autenticar al usuario |
| `conversaciones` | `{ username }` | Solicitar lista de conversaciones |
| `obtener_mensajes` | `{ conversacion_id }` | Cargar historial de mensajes |
| `send_message` | `{ remitente, destinatario, conversacion_id, mensaje }` | Enviar un mensaje |
| `obtener_contactos` | `{ username }` | Solicitar lista de contactos |
| `agregar_contacto` | `{ mi_usuario, nuevo_contacto }` | Agregar un nuevo contacto |
| `crear_grupo` | `{ creador, nombre_grupo, miembros }` | Crear un grupo de chat |

### Eventos de Socket.IO — Emitidos por el Servidor

| Evento | Contenido | Descripción |
|---|---|---|
| `login_response` | `{ success, user? , message? }` | Resultado de la autenticación |
| `lista_conversaciones` | `{ conversaciones: [{id, nombre}] }` | Lista de conversaciones del usuario |
| `lista_mensajes` | `{ mensajes: [{usuario, mensaje, fecha}] }` | Historial de mensajes de una conversación |
| `nuevo_mensaje` | `{ conversacion_id, usuario, mensaje, fecha }` | Nuevo mensaje en tiempo real (broadcast) |
| `lista_contactos` | `{ contactos: [{nombre}] }` | Lista de contactos del usuario |
| `respuesta_contacto` | `{ success, message }` | Resultado de agregar un contacto |
| `respuesta_grupo` | `{ success, message }` | Resultado de crear un grupo |


## Concurrencia

El servidor utiliza dos mecanismos para manejar concurrencia de forma segura:
- **`threading.Thread`:** El procesamiento de mensajes hacia la base de datos se delega a un hilo secundario para no bloquear el event loop de Socket.IO.
- **`threading.Lock` (`db_lock`):** Un mutex asegura que solo un hilo acceda a la base de datos a la vez durante la escritura de mensajes y creación de grupos, evitando condiciones de carrera.

## Gestión de Conexiones a la BD
Cada operación abre y cierra su propia conexión a PostgreSQL mediante `psycopg2`

---
## Base de Datos
El sistema utiliza una base de datos PostgreSQL llamada `wasap`. El script `base_datos.sql` contiene todas las sentencias DDL necesarias para crear las tablas.
### Esquema
#### Tabla `usuarios`
Almacena la información de todos los usuarios registrados en el sistema.

| Columna | Tipo | Restricción | Descripción |
|---|---|---|---|
| `id` | SERIAL | PRIMARY KEY | Identificador único autoincremental |
| `nombre` | VARCHAR(100) | NOT NULL | Nombre del usuario |
| `apellido` | VARCHAR(100) | NOT NULL | Apellido del usuario |
| `correo_electronico` | VARCHAR(100) | UNIQUE, NOT NULL | Correo electrónico único |
| `nombre_usuario` | VARCHAR(50) | UNIQUE, NOT NULL | Nombre de usuario para login |
| `contrasena` | VARCHAR(50) | NOT NULL | Contraseña del usuario |
| `fecha_creacion` | TIMESTAMP | DEFAULT NOW() | Fecha de registro |

#### Tabla `conversaciones`
Representa tanto chats privados (entre dos usuarios) como grupos.

| Columna | Tipo | Restricción | Descripción |
|---|---|---|---|
| `id` | BIGSERIAL | PRIMARY KEY | Identificador único |
| `tipo` | VARCHAR(10) | CHECK ('privado','grupo') | Tipo de conversación |
| `nombre` | TEXT | — | Nombre del grupo (NULL para privados) |
| `creado_por` | BIGINT | FK → usuarios(id) | Usuario creador (grupos) |
| `creado_en` | TIMESTAMP | DEFAULT NOW() | Fecha de creación |

#### Tabla `participantes_conversacion`
Tabla de relación muchos-a-muchos entre usuarios y conversaciones, con soporte de roles.

| Columna | Tipo | Restricción | Descripción |
|---|---|---|---|
| `conversacion_id` | BIGINT | FK → conversaciones(id), CASCADE | ID de la conversación |
| `usuario_id` | BIGINT | FK → usuarios(id), CASCADE | ID del usuario |
| `rol` | VARCHAR(10) | CHECK ('admin','miembro') | Rol dentro del grupo |
| `unido_en` | TIMESTAMP | DEFAULT NOW() | Fecha de incorporación |

> **Clave primaria compuesta:** `(conversacion_id, usuario_id)`

#### Tabla `mensajes`
Almacena todos los mensajes enviados en todas las conversaciones.

| Columna | Tipo | Restricción | Descripción |
|---|---|---|---|
| `id` | BIGSERIAL | PRIMARY KEY | Identificador único |
| `conversacion_id` | BIGINT | FK → conversaciones(id), CASCADE | Conversación a la que pertenece |
| `remitente_id` | BIGINT | FK → usuarios(id), SET NULL | Usuario que envió el mensaje |
| `contenido` | TEXT | NOT NULL | Contenido del mensaje |
| `enviado_en` | TIMESTAMP | DEFAULT NOW() | Fecha y hora de envío |

#### Tabla `contactos`
Lista de contactos por usuario (relación unidireccional).

| Columna | Tipo | Restricción | Descripción |
|---|---|---|---|
| `usuario_id` | INT | FK → usuarios(id), CASCADE | Usuario propietario de la lista |
| `contacto_id` | INT | FK → usuarios(id), CASCADE | Usuario agregado como contacto |
| `agregado_en` | TIMESTAMP | DEFAULT NOW() | Fecha en que fue agregado |

> **Clave primaria compuesta:** `(usuario_id, contacto_id)`
