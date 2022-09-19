"""COMP 431 SMTP server"""
import socket
import re
import sys
import threading

#header tells us how many bytes to receive, header is 64 bytes
#consistent header size which communicates the size to come
def main():
    PORT = 9195
    # socket is 192.168.1.71
    HOST_SOCKET = socket.gethostbyname(socket.gethostname()) #socket of host computer
    LOCALHOST = socket.gethostname() #name of host computer
    FORMAT = 'utf-8' #Which format to be used when read

    ADDR = (HOST_SOCKET, PORT) #socket of host and free port

    servSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servSocket.bind(ADDR)

    servSocket.listen()

    servSocket, CLIENT_ADDR = servSocket.accept()

    msg = "220" + LOCALHOST #send generic greeting msg to client
    servSocket.sendall(msg.encode(FORMAT))

    msgRecv = servSocket.recv(256).decode(FORMAT)
    msgRecBool = msg_valid(msgRecv)

    if(msgRecBool):
        # start message processing loop
    else:
        # 500 or 501 error



def msg_valid(msg) -> bool: 
    msg_vaild = "^HELO\s*([a-zA-Z][a-z0-9A-Z-]*(\.[a-zA-Z][a-z0-9A-Z-]*)*)$"

    if re.match(msg_valid, msg): #check if passed parameter matches the email_valid string
            return True
    return False
