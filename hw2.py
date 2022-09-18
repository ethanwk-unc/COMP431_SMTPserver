"""COMP 431 SMTP server"""
import socket
import threading

PORT = 5050 
SERVER = socket.gethostbyname(socket.gethostname())
print(SERVER)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #create socket with a certain