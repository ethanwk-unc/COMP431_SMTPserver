"""COMP 431 SMTP server"""
import socket
import re
import sys

cur_cmd = 'helo'        #command that is currently being looked for
prev_cmd = 'quit'       #previous command
cmd_rec = ''            #command last received

PORT = 9195
HOST_SOCKET = socket.gethostbyname(socket.gethostname()) #socket of host computer
LOCALHOST = socket.gethostname() #name of host computer
FORMAT = "utf-8" #Which format to be used when read
ADDR = (HOST_SOCKET, PORT) #socket of host and free port

def main():

    print("test helo err")

    global servSocket;
    servSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #create a socket for streaming data
    print("[SERVER SOCKET CREATED]")
    servSocket.bind(ADDR) #bind the socket to the address of the current computer
    print("[BIND]")

    servSocket.listen() #Begin listening on port 9195
    print("[LISTEN]")
    servSocket, CLIENT_ADDR = servSocket.accept()
    print("[ACCEPT]")

    greeting = "220 " + LOCALHOST #send generic greeting msg to client
    print("[GREETING MAKE]")
    servSocket.sendall(greeting.encode(FORMAT))
    print("[SEND GREETING]")
    print(greeting)

    heloRecv = servSocket.recv(256).decode(FORMAT)
    print("[DECODE HELLO]")
    print(heloRecv)

    if (cmd_valid(heloRecv)): #HELO command was valid
        test = "[HELO CMD VALID]"
        print(test)

        if(helo_Domvalid(heloRecv)):
            test = "[HELO DOM VALID]"
            print(test)
            servSocket.close()
            """
            elements = heloRecv.split() #split into HELO and client name
            client_name = elements[1]
            print("[READ CLIENT NAME]")

            handshake = "250 Hello " + client_name + " pleased to meet you"
            servSocket.sendall(handshake.encode(FORMAT))
            print("[PRINT HANDSHAKE]")
            print(handshake)

            msgRecv = servSocket.recv(256).decode(FORMAT)

            while(not disconnect(msgRecv)):
                print("[MSG LOOP]")
                msg_loop(msgRecv)
                msgRecv = servSocket.recv(256).decode(FORMAT)
            
            disconnected = "221 " + LOCALHOST + " closing connection"
            servSocket.sendall(disconnected.encode(FORMAT))
            servSocket.close()
            """
        else:
            ERROR501 = '501 Syntax error in parameters or arguments'
            test = "[HELO DOM INVALID]"
            print(test)
            servSocket.sendall(ERROR501.encode(FORMAT))
            servSocket.close()


    else:
        ERROR500 = '500 Syntax error: command unrecognized'
        test = "[HELO CMD INVALID]"
        print(test)
        servSocket.sendall(ERROR500.encode(FORMAT))
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
    return False

def msg_loop(line):
    global cur_cmd
    global prev_cmd
    global cmd_rec

    lines = []                                      #array to store all lines that are valid
    if cur_cmd == '.':                          #when the current command is looking for the "."
        detect_dot = line.split()               #split line into parts
        if detect_dot[0] == '.':                #if the first part of the line is "." end
            print(".")
            OK = '250 OK'
            servSocket.sendall(OK.encode(FORMAT))
            lines.append(line)
            cur_cmd = 'mfrm'                    #reset to default command
            prev_cmd = '.'                      #reset previous command to "."

            write_file(lines)                   #pass lines array to write to function file
            lines = []                          #reset the array
        else:                                   #if line != "." keep taking in message bodies
            lines.append(line)
            print(line, end='')                 #else print line
    else:
        if cmd_valid(line):                     #if cmd not valid 500 err
            if order_valid(line) or (not helo_Cmdvalid(line)):               #if order not valid 503 err
                if prev_cmd == 'data':
                    startInput = '354 Start mail input; end with . on a line by itself'
                    lines.append(line)
                    print(line, end='')
                    print(startInput)
                    servSocket.sendall(startInput.encode(FORMAT))
                elif prev_cmd == 'mfrm' or prev_cmd == 'rcpt': #if email not valid 501 err
                    if parameter_valid(line):
                        OK = '250 OK'
                        print(line, end='')
                        print(OK)
                        servSocket.sendall(OK.encode(FORMAT))
                        if prev_cmd == 'mfrm':
                            lines.append(line)
                        elif prev_cmd == 'rcpt':
                            lines.append(line)
                    else: 
                        if prev_cmd == 'mfrm':
                            cur_cmd = 'mfrm'
                        else:
                            cur_cmd = 'rcpt'
                        ERROR501 = '501 Syntax error in parameters or arguments'
                        print(line, end='')
                        print(ERROR501)
                        servSocket.sendall(ERROR501.encode(FORMAT))
            else:
                ERROR503 = '503 Bad sequence of commands'
                print(line, end='')
                print('503 Bad sequence of commands')
                servSocket.sendall(ERROR503.encode(FORMAT))
        else:
            ERROR500 = '500 Syntax error: command unrecognized'
            print(line, end='')
            print('500 Syntax error: command unrecognized')
            servSocket.sendall(ERROR500.encode(FORMAT))

def cmd_valid(line) -> bool:
    global prev_cmd
    global cur_cmd
    global cmd_rec

    if line[0] == 'H':
        cmd_form = "^HELO\s+.*"
        if re.match(cmd_form,line): #check if passed parameter matches the cmd_form string
            cmd_rec = 'helo'        #if yes then valid received command is mfrm
            return True
        else:
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
        cmd_form = '^DATA\s*$'
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
    
    if cur_cmd == 'mfrm' and cmd_rec == 'mfrm': #confirm command looking for is mail from and the cmd rec is mfrm
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

def write_file(lines):
    first = lines[1]                                            #take the second line of the array the rcpt from
    no_space = first.replace(" ","")                            #remove all spaces
    no_space = no_space.replace("\t","")
    no_space = no_space.replace("\n","")
    no_space = no_space.replace("$","")
    no_space = no_space.replace("'","")
    tokens = no_space.split(":")                            #split for just the email param after from:
    recipient = tokens[1]                                   #store the email string (or parameter) as recipient
    recipient = recipient.replace("'","")
    #recipient[1:(len(recipient)-2)]                        #replace with recipient before submit, test file
    #print("recipient: " + recipient)
    with open("forward/"+ recipient, "a") as file:          #open file or create file with recipient address
        for line in lines:                                  #write the lines of lines into the new file
            file.write(line)
    return

if __name__ == "__main__":
    main()