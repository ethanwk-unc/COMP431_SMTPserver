"""COMP 431 SMTP server"""
import socket
import threading

HEADER = 64 
#header tells us how many bytes to receive, header is 64 bytes
#consistent header size which communicates the size to come

PORT = 9195
# socket is 192.168.1.71
SERVER = socket.gethostbyname(socket.gethostname()) #socket of host computer
HOST = socket.gethostname() #name of host computer

ADDR = (SERVER, PORT) #socket of host and free port

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind(ADDR)
 
print(SERVER)
print("220 " + HOST)


"""
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"


def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")

    connected = True
    while connected:
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)
            if msg == DISCONNECT_MESSAGE:
                connected = False

            print(f"[{addr}] {msg}")
            conn.send("Msg received".encode(FORMAT))

    conn.close()
        

def start():
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")


print("[STARTING] server is starting...")
start()
"""
