import socket
import threading

HOST = '127.0.0.1'
PORT = 5000

usuarios_registrados = ['gr63', 'aa23', 'op81', 'ln1']

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

clients = []
usernames = {}

def broadcast(message, _client):
    for client in clients:
        if client != _client:
            try:
                client.send(message)
            except:
                client.close()
                if client in clients: clients.remove(client)

def handle_client(client):
    try:
        
        nickname = client.recv(1024).decode('utf-8')
        
        if nickname.lower() in usuarios_registrados:
            print(f"Acceso concedido a: {nickname}")
            client.send("AUTH_OK".encode('utf-8')) 
            usernames[client] = nickname
            clients.append(client)
            broadcast(f"{nickname} se ha unido al chat".encode('utf-8'), client)
        else:
            print(f"Intento de acceso denegado: {nickname}")
            client.send("AUTH_FAILED".encode('utf-8'))
            client.close()
            return

        while True:
            message = client.recv(1024)
            if not message: break
            broadcast(f"{usernames[client]}: ".encode('utf-8') + message, client)
            
    except:
        if client in clients: clients.remove(client)
        client.close()

def receive_connections():
    print(f"Servidor iniciado. Esperando usuarios de la lista: {usuarios_registrados}")
    while True:
        client, address = server.accept()
        thread = threading.Thread(target=handle_client, args=(client,))
        thread.start()

if __name__ == "__main__":
    receive_connections()