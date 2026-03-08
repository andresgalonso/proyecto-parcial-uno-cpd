from logging import exception
import psycopg2
import threading
from flask import Flask, render_template, request, jsonify, session
from flask_socketio import SocketIO, emit


app = Flask(__name__)
socketio = SocketIO(app)
db_lock = threading.Lock()

def get_conection():
    return psycopg2.connect(
        host="localhost",
        database="wasap",
        user="postgres",
        password="marin1234"
    )

@app.route('/')
def index():
    return render_template('login.html')

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        data = request.get_json() if request.is_json else request.form

        nombre = data.get("nombre")
        apellido = data.get("apellido")
        correo_electronico = data.get("correo")
        nombre_usuario = data.get("usuario")
        contrasena = data.get("contrasena")
        try:
            connection = get_conection()
            cursor = connection.cursor()
            cursor.execute(
          """
                INSERT INTO usuarios (nombre, apellido, correo_electronico, nombre_usuario, contrasena) 
                VALUES (%s, %s, %s, %s, %s)
                """,
                (nombre, apellido, correo_electronico, nombre_usuario, contrasena)
            )
            connection.commit()
            cursor.close()
            connection.close()
            return jsonify({"success": True, "message": "Usuario registrado correctamente."})
        except Exception as e:
            return jsonify({"success": False, "message": f"Error al registrar: {str(e)}"})

    return render_template("register.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/chat-plantilla")
def chat_plantilla():
    return render_template("chat-plantilla.html")

@socketio.on('login')
def handle_login(data):
    username = data.get('username', '').strip()
    password = data.get('password', '')

    try:
        connection = get_conection()
        cursor = connection.cursor()
        cursor.execute(
            "SELECT nombre_usuario FROM usuarios WHERE nombre_usuario = %s AND contrasena = %s",
            (username,password)
        )
        usuario_encontrado = cursor.fetchone()

        cursor.close()
        connection.close()

        if usuario_encontrado:
            nombre_db = usuario_encontrado[0]
            session['username'] = nombre_db
            emit('login_response', {'success': True, 'user': nombre_db})
            emit('message', {'user': 'Sistema', 'msg': f'{nombre_db} se ha unido.'}, broadcast=True)
        else:
            emit('login_response', {'success': False, 'message': 'Usuario o contrasena incorrectos.'})

    except Exception as e:
        emit('login_response', {'success': False, 'message': f'Error de conexion: {str(e)}'})

@socketio.on('conversaciones')
def handle_conversaciones(data):
    username = data.get("username")
    print("Usuario solicitando conversaciones:", username)

    try:
        connection = get_conection()
        cursor = connection.cursor()

        query = """
        SELECT DISTINCT
            c.id,
            CASE 
                WHEN c.tipo = 'grupo' THEN c.nombre
                ELSE (
                    SELECT u_other.nombre_usuario 
                    FROM participantes_conversacion pc_other
                    JOIN usuarios u_other ON pc_other.usuario_id = u_other.id
                    WHERE pc_other.conversacion_id = c.id AND u_other.nombre_usuario != %s
                    LIMIT 1
                )
             END AS nombre_chat
        FROM conversaciones c
        JOIN participantes_conversacion pc ON c.id = pc.conversacion_id
        JOIN usuarios u ON pc.usuario_id = u.id
        WHERE u.nombre_usuario = %s
        ORDER BY c.id DESC;
        """

        cursor.execute(query, (username, username))
        resultados = cursor.fetchall()

        conversaciones = [
            {"id": row[0], "nombre": row[1]}
            for row in resultados
        ]

        cursor.close()
        connection.close()

        emit('lista_conversaciones', {'conversaciones': conversaciones})

    except Exception as e:
        emit('lista_conversaciones', {'error': str(e)})

@socketio.on('obtener_mensajes')
def handle_obtener_mensajes(data):

    conversacion_id = data.get('conversacion_id')

    try:
        connection = get_conection()
        cursor = connection.cursor()

        query = """
        SELECT 
            m.contenido,
            m.enviado_en,
            u.nombre_usuario
        FROM mensajes m
        JOIN usuarios u 
            ON m.remitente_id = u.id
        WHERE m.conversacion_id = %s
        ORDER BY m.enviado_en ASC;
        """

        cursor.execute(query, (conversacion_id,))
        resultados = cursor.fetchall()

        mensajes = [
            {
                "usuario": row[2],
                "mensaje": row[0],
                "fecha": str(row[1])
            }
            for row in resultados
        ]

        cursor.close()
        connection.close()

        emit('lista_mensajes', {'mensajes': mensajes})

    except Exception as e:
        emit('lista_mensajes', {'error': str(e)})


def process_message_db(remitente, destinatario, conversacion_id, contenido):
    if not remitente or not contenido:
        return
    conn = None
    try:
        with db_lock:
            conn = get_conection()
            with conn:
                with conn.cursor() as cur:
                    # Remitente
                    cur.execute("SELECT id FROM usuarios WHERE nombre_usuario = %s", (remitente,))
                    rem_row = cur.fetchone()
                    if not rem_row: return
                    rem_id = rem_row[0]

                    #  Conversación
                    if not conversacion_id and destinatario:
                        cur.execute("SELECT id FROM usuarios WHERE nombre_usuario = %s", (destinatario,))
                        dest_row = cur.fetchone()
                        if not dest_row: return
                        dest_id = dest_row[0]

                        cur.execute("""
                            SELECT c.id FROM conversaciones c
                            JOIN participantes_conversacion p1 ON c.id = p1.conversacion_id
                            JOIN participantes_conversacion p2 ON c.id = p2.conversacion_id
                            WHERE c.tipo = 'privado' AND p1.usuario_id = %s AND p2.usuario_id = %s
                        """, (rem_id, dest_id))

                        conv = cur.fetchone()

                        if conv:
                            conversacion_id = conv[0]
                        else:
                            cur.execute("INSERT INTO conversaciones (tipo) VALUES ('privado') RETURNING id")
                            conversacion_id = cur.fetchone()[0]
                            cur.execute("""
                                INSERT INTO participantes_conversacion (conversacion_id, usuario_id)
                                VALUES (%s, %s), (%s, %s)
                            """, (conversacion_id, rem_id, conversacion_id, dest_id))

                    if not conversacion_id: return


                    cur.execute("""
                        INSERT INTO mensajes (conversacion_id, remitente_id, contenido)
                        VALUES (%s, %s, %s) RETURNING enviado_en
                    """, (conversacion_id, rem_id, contenido))
                    fecha = cur.fetchone()[0]

        #  Emitir
        socketio.emit('nuevo_mensaje', {
            'conversacion_id': conversacion_id,
            'usuario': remitente,
            'mensaje': contenido,
            'fecha': str(fecha)
        })
    except Exception as e:
        print(f"Error en hilo BD: {e}")
    finally:
        if conn:
            conn.close()


@socketio.on('obtener_contactos')
def handle_obtener_contactos(data):
    username = data.get('username')
    try:
        with get_conection() as conn:
            with conn.cursor() as cur:
                # Buscamos los usuarios que estén en mi lista de contactos
                cur.execute("""
                    SELECT u.nombre_usuario 
                    FROM contactos c
                    JOIN usuarios u ON c.contacto_id = u.id
                    WHERE c.usuario_id = (SELECT id FROM usuarios WHERE nombre_usuario = %s)
                """, (username,))

                contactos = [{"nombre": row[0]} for row in cur.fetchall()]

        emit('lista_contactos', {'contactos': contactos})
    except Exception as e:
        print(f"Error al obtener contactos: {e}")


@socketio.on('agregar_contacto')
def handle_agregar_contacto(data):
    mi_usuario = data.get('mi_usuario')
    nuevo_contacto = data.get('nuevo_contacto')
    try:
        with get_conection() as conn:
            with conn.cursor() as cur:
                # Obtener mi ID
                cur.execute("SELECT id FROM usuarios WHERE nombre_usuario = %s", (mi_usuario,))
                mi_id = cur.fetchone()[0]

                # Obtener el ID del  a agregar
                cur.execute("SELECT id FROM usuarios WHERE nombre_usuario = %s", (nuevo_contacto,))
                amigo_row = cur.fetchone()

                if not amigo_row:
                    emit('respuesta_contacto', {'success': False, 'message': 'El usuario no existe.'})
                    return
                amigo_id = amigo_row[0]

                if mi_id == amigo_id:
                    emit('respuesta_contacto', {'success': False, 'message': 'No puedes agregarte a ti mismo.'})
                    return

                # Validar si ya lo tengo agregado
                cur.execute("SELECT 1 FROM contactos WHERE usuario_id = %s AND contacto_id = %s", (mi_id, amigo_id))
                if cur.fetchone():
                    emit('respuesta_contacto',
                         {'success': False, 'message': 'Ya tienes a este usuario en tus contactos.'})
                    return

                cur.execute("INSERT INTO contactos (usuario_id, contacto_id) VALUES (%s, %s)", (mi_id, amigo_id))

        emit('respuesta_contacto', {'success': True, 'message': f'{nuevo_contacto} ha sido agregado.'})
    except Exception as e:
        emit('respuesta_contacto', {'success': False, 'message': f'Error: {str(e)}'})


@socketio.on('crear_grupo')
def handle_crear_grupo(data):
    creador = data.get('creador')
    nombre_grupo = data.get('nombre_grupo')
    miembros_str = data.get('miembros', '')


    nombres_miembros = [n.strip() for n in miembros_str.split(',') if n.strip()]
    nombres_miembros.append(creador)
    nombres_miembros = list(set(nombres_miembros))

    try:

        with db_lock:
            conn = get_conection()
            with conn:
                with conn.cursor() as cur:
                    # 1. Creamos la conversación de tipo 'grupo'
                    cur.execute("""
                        INSERT INTO conversaciones (tipo, nombre, creado_por)
                        VALUES ('grupo', %s, (SELECT id FROM usuarios WHERE nombre_usuario = %s)) 
                        RETURNING id
                    """, (nombre_grupo, creador))
                    grupo_id = cur.fetchone()[0]

                    # 2. Agregamos a todos los participantes
                    for miembro in nombres_miembros:
                        cur.execute("SELECT id FROM usuarios WHERE nombre_usuario = %s", (miembro,))
                        usuario_row = cur.fetchone()

                        # Si el usuario existe, lo metemos al grupo
                        if usuario_row:
                            u_id = usuario_row[0]
                            # Le damos rol de admin al creador, y miembro a los demás
                            rol = 'admin' if miembro == creador else 'miembro'
                            cur.execute("""
                                INSERT INTO participantes_conversacion (conversacion_id, usuario_id, rol)
                                VALUES (%s, %s, %s)
                            """, (grupo_id, u_id, rol))
        emit('respuesta_grupo', {'success': True, 'message': f'El grupo "{nombre_grupo}" ha sido creado.'})

    except Exception as e:
        print(f"Error al crear grupo: {e}")
        emit('respuesta_grupo', {'success': False, 'message': f'Error al crear grupo: {str(e)}'})



@socketio.on('send_message')
def handle_message(data):
    remitente = data.get('remitente')
    destinatario = data.get('destinatario')
    conversacion_id = data.get('conversacion_id')
    mensaje = data.get('mensaje')

    hilo_db = threading.Thread(
        target=process_message_db,
        args = (remitente, destinatario, conversacion_id, mensaje)
    )
    hilo_db.start()

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)