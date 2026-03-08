import psycopg2
from flask import Flask, render_template, redirect, request, jsonify, session
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app)


def get_conection():
    return psycopg2.connect(
        host="localhost",
        database="wasap",
        user="postgres",
        password="1234"
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
        SELECT 
            c.id,
            CASE 
                WHEN c.tipo = 'grupo' THEN c.nombre
                ELSE u.nombre_usuario
            END AS nombre_chat
        FROM conversaciones c
        JOIN participantes_conversacion pc 
            ON c.id = pc.conversacion_id
        JOIN usuarios u 
            ON pc.usuario_id = u.id
        WHERE c.id IN (
            SELECT conversacion_id
            FROM participantes_conversacion pc2
            JOIN usuarios u2 ON pc2.usuario_id = u2.id
            WHERE u2.nombre_usuario = %s
        )
        AND u.nombre_usuario != %s;
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

@socketio.on('send_message')
def handle_message(data):
    emit('message', {'user': data['user'], 'msg': data['msg']}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)