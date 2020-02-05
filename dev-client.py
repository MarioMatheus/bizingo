import socket
import sys
import select

s = socket.socket()
host = '192.168.15.4'
# host = '10.112.2.7'
port = 9999

s.connect((host, port))

input_list = [sys.stdin, s]

while True:
    inputs, _, _ = select.select(input_list, [], [])
    for ipt in inputs:
        if ipt == s:
            message = ipt.recv(1024)
            if message:
                print(message.decode('utf-8'))
            else:
                s.close()
                sys.exit()
        else:
            message = input()
            if message == 'quit':
                s.close()
                sys.exit()
            s.send(message.encode())
            sys.stdout.write('Message sent: ' + message + '\n')
            sys.stdout.flush()

s.close()
