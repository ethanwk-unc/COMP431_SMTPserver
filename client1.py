import socket
import sys


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_name = sys.argv[1]
port_number = int(sys.argv[2])
host = socket.gethostname()
server_address = (server_name, port_number)
sock.connect(server_address)


    #sock.connect(server_address)

#220 greeting
message = sock.recv(256).decode("utf-8")
print(message)

#you respond back with HELO command
while (message[:3] != "250"):
    sock.sendall((str(input()) + host).encode("utf-8"))

    message = sock.recv(256).decode("utf-8")
    print(message)

message = ""

#you send MAIL FROM
while (message[:3] != "250"):
    message = sock.sendall((input()).encode("utf-8"))

    message = sock.recv(256).decode("utf-8")
    print(message)

message = ""
#you SEND RCPT TO
while (message[:3] != "250"):
    message = sock.sendall((input()).encode("utf-8"))

    message = sock.recv(256).decode("utf-8")
    print(message)

message = ""

#you send DATA
while (message[:3] != "354"):

    sock.sendall((input()).encode("utf-8"))

    message = sock.recv(256).decode("utf-8")
    print(message)
message = ""

#you send one line data 
while (message[:3] != "250"):
    sock.sendall((input()).encode("utf-8"))

    message = sock.recv(256).decode("utf-8")
    print(message)

#sock.sendall(("QUIT").encode("utf-8"))

message = sock.recv(256).decode("utf-8")
print(message)
