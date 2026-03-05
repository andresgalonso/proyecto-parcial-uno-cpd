import socket
import threading

HOST = '127.0.0.1'
PORT = 5000

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

def receive_messages():
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            print("\n" + message)
        except:
            print("Conexión cerrada.")
            client.close()
            break

def send_messages():
    while True:
        try:
            message = input()
            client.send(message.encode('utf-8'))
        except:
            break

nickname = input("Introduce tu nombre de usuario para ingresar: ")
client.send(nickname.encode('utf-8'))

response = client.recv(1024).decode('utf-8')

if response == "AUTH_OK":
    print("¡Bienvenido al sistema!")
    threading.Thread(target=receive_messages).start()
    threading.Thread(target=send_messages).start()
else:
    print("Error: Usuario no registrado en la lista permitida.")
    client.close()