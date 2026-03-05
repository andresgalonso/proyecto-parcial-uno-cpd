from flask import Flask, render_template, redirect
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app)

usuarios_registrados = ['gr63', '23aa', '81op', '1ln']
usuarios_conectados = {}

@app.route('/')
def index():
    return render_template('login.html')

@app.route("/register", methods=["GET", "POST"])
def register():
    return render_template("register.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/chat-plantilla")
def login():
    return render_template("chat-plantilla.html")

@socketio.on('login')
def handle_login(data):
    username = data.get('username', '').lower().strip()
    if username in usuarios_registrados:
        usuarios_conectados[username] = True
        emit('login_response', {'success': True, 'user': username})
        emit('message', {'user': 'Sistema', 'msg': f'{username} se ha unido.'}, broadcast=True)
    else:
        emit('login_response', {'success': False, 'message': 'Usuario no registrado.'})

@socketio.on('send_message')
def handle_message(data):
    emit('message', {'user': data['user'], 'msg': data['msg']}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)