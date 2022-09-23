"""COMP 431 SMTP server"""
import socket
import re
import sys

cur_cmd = 'helo'        #command that is currently being looked for
prev_cmd = 'quit'       #previous command
cmd_rec = ''            #command last received
recipient = ''
lines = []

PORT = 9195
HOST_SOCKET = socket.gethostbyname(socket.gethostname()) #socket of host computer
LOCALHOST = socket.gethostname() #name of host computer
FORMAT = "utf-8" #Which format to be used when read
ADDR = (HOST_SOCKET, PORT) #socket of host and free port

def main():
    firstSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    firstSocket.bind(ADDR)

    while(True):

        global cur_cmd
        global prev_cmd
        global cmd_rec
        global servSocket

        firstSocket.listen() #Begin listening on port 9195
        servSocket, CLIENT_ADDR = firstSocket.accept()


        greeting = "220 " + LOCALHOST #send generic greeting msg to client
        servSocket.sendall(greeting.encode(FORMAT))
        print(greeting)

        heloRecv = servSocket.recv(256).decode(FORMAT)

        while (True):
            print(heloRecv)
            if(cmd_valid(heloRecv) == False):
                heloRecv = servSocket.recv(256).decode(FORMAT)
            elif(cmd_valid(heloRecv) and order_valid(heloRecv)):
                break
            else:
                ERROR503 = '503 Bad sequence of commands'
                servSocket.sendall(ERROR503.encode(FORMAT))
                heloRecv = servSocket.recv(256).decode(FORMAT)

        elements = heloRecv.split() #split into HELO and client name
        client_name = elements[1]

        handshake = "250 Hello " + client_name + " pleased to meet you"
        servSocket.sendall(handshake.encode(FORMAT))
        print(handshake)

        msgRecv = servSocket.recv(256).decode(FORMAT)
        while(disconnect(msgRecv) == False):
            msg_loop(msgRecv)
            msgRecv = servSocket.recv(256).decode(FORMAT)
        
        disconnected = "221 " + LOCALHOST + " closing connection"
        servSocket.sendall(disconnected.encode(FORMAT))
        print(disconnected)
        servSocket.close()

def disconnect(msg) -> bool:
    quit_syntax = "^QUIT\s*$"

    if re.match(quit_syntax, msg):
            return True
    return False

def helo_Domvalid(msg) -> bool: 
    helo_syntax = "^HELO\s+([a-zA-Z][a-z0-9A-Z-]*(\.[a-zA-Z][a-z0-9A-Z-]*)*)$"

    if re.match(helo_syntax, msg):
            return True
    ERROR501 = '501 Syntax error in parameters or arguments'
    servSocket.sendall(ERROR501.encode(FORMAT))
    return False

def msg_loop(line):
    global cur_cmd
    global prev_cmd
    global cmd_rec
    global recipient
    global lines

                         
    if cur_cmd == '.':
        elms = line.split()
        for line in elms:       
            if line == '.':
                lines.append(line)                
                print(line)
                OK = '250 OK'
                servSocket.sendall(OK.encode(FORMAT))
                cur_cmd = 'mfrm'                 
                prev_cmd = '.'                      

                write_file(lines, recipient)               
                lines = []
                recipient = ''   
            else:                                   
                lines.append(line)
                print(line)
                
    else:
        if cmd_valid(line): #Error 500 check         
            if order_valid(line): #Error 503 check              
                if prev_cmd == 'data': #Start '.' check
                    startInput = '354 Start mail input; end with . on a line by itself'
                    print(line)
                    print(startInput)
                    servSocket.sendall(startInput.encode(FORMAT))
                elif prev_cmd == 'mfrm' or prev_cmd == 'rcpt': # 501 Error check
                    if parameter_valid(line): # 501 Error Check
                        if prev_cmd == 'rcpt': # Get recipient name if rcpt to:
                            no_space = line.replace(" ","")        
                            no_space = no_space.replace("\t","")
                            no_space = no_space.replace("\n","")
                            no_space = no_space.replace("$","")
                            no_space = no_space.replace("'","")
                            no_space = no_space.replace(">","")
                            tokens = no_space.split("@", 1)
                            recipient = tokens[1]
                        OK = '250 OK'
                        print(line)
                        print(OK)
                        servSocket.sendall(OK.encode(FORMAT))
                    else: 
                        if prev_cmd == 'mfrm': #ask for another cmd after 501
                            cur_cmd = 'mfrm'
                        else:
                            cur_cmd = 'rcpt'
                        ERROR501 = '501 Syntax error in parameters or arguments'
                        print(line)
                        print(ERROR501)
                        servSocket.sendall(ERROR501.encode(FORMAT))
            else:
                ERROR503 = '503 Bad sequence of commands'
                print(line)
                print(ERROR503)
                servSocket.sendall(ERROR503.encode(FORMAT))
        else:
            ERROR500 = '500 Syntax error: command unrecognized'
            print(line)
            print(ERROR500)
            servSocket.sendall(ERROR500.encode(FORMAT))

def cmd_valid(line) -> bool:
    global prev_cmd
    global cur_cmd
    global cmd_rec

    if cur_cmd == 'helo':
        cmd_form = "^HELO\s+.*"
        if re.match(cmd_form,line):
            if(helo_Domvalid(line)):
                cmd_rec = 'helo'
                return True
            else:
                return False
        else:
            ERROR500 = '500 Syntax error: command unrecognized'
            servSocket.sendall(ERROR500.encode(FORMAT))
            return False
    elif line[0] == 'M':
        cmd_form = "^MAIL\s+FROM:.+"
        if re.match(cmd_form,line): #check if passed parameter matches the cmd_form string
            cmd_rec = 'mfrm'        #if yes then valid received command is mfrm
            return True
        else:
            return False
    elif line[0] == 'R':
        cmd_form = '^RCPT\s+TO:.+' #same for rcpt
        if re.match(cmd_form,line):
            cmd_rec = 'rcpt' 
            return True
        else:
            return False
    elif line[0] == 'D':
        cmd_form = 'DATA\s*'
        if re.match(cmd_form,line): #same for data
            cmd_rec = 'data'
            return True
        else:
            return False
    else: 
        return False

def order_valid(line) -> bool:
    global prev_cmd
    global cur_cmd
    global cmd_rec
    
    if cur_cmd == 'helo' and cmd_rec == 'helo': #confirm command looking for is mail from and the cmd rec is mfrm
        prev_cmd = cur_cmd                      #make prev cmd last cmd
        cur_cmd = 'mfrm'                        #look for rcpt cmd
        cmd_rec = ''                            #set no received cmd
        return True
    elif cur_cmd == 'mfrm' and cmd_rec == 'mfrm': #confirm command looking for is mail from and the cmd rec is mfrm
        prev_cmd = cur_cmd                      #make prev cmd last cmd
        cur_cmd = 'rcpt'                        #look for rcpt cmd
        cmd_rec = ''                            #set no received cmd
        return True
    elif cur_cmd == 'rcpt' and cmd_rec == 'rcpt': #check cur cmd needed is cmd received
        prev_cmd = cur_cmd
        cur_cmd = 'data'
        cmd_rec = '' 
        return True
    elif cur_cmd == 'data' and cmd_rec == 'data': #same thing
        prev_cmd = cur_cmd
        cur_cmd = '.'
        cmd_rec = '' 
        return True
    elif cur_cmd == '.' and prev_cmd == 'data': #if the last cmd was data and we hit . start message body
        return True
    return False

def parameter_valid(line) -> bool: 
                                        #email_valid is the string structure for valid emails
    tokens = line.split(":")            #split for email end at :
    param = tokens[1]                   #isolate token

    #create a string with regex values for space ahead, behind, starting with < and ending with>
    #inside only allow a-z0-9A-Z-|^\&\*] almost all ascii one or more times then @ then only a-z0-9A-Z- letters+numbs
    #then one or more domains with only upper and lower case multiple

    email_valid = "\s*<([a-z0-9A-Z-_|^\&\*]+)@([a-zA-Z][a-z0-9A-Z-]*(\.[a-zA-Z][a-z0-9A-Z-]*)*)>\s*"
    if re.match(email_valid,param): #check if passed parameter matches the email_valid string
        return True
    return False

def write_file(lines, recipient):                           

    with open("forward/"+ recipient, "a") as file:        
        for line in lines:                               
            file.write(line)
    return

if __name__ == "__main__":
    main()