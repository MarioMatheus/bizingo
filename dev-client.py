# import socket
from xmlrpc.client import ServerProxy
from xmlrpc.server import SimpleXMLRPCServer
import sys
import select

# s = socket.socket()
host = 'localhost'
# host = '192.168.15.4'
# host = '10.112.2.7'
port = 9999

def callback(message):
    print(message)

server_proxy = ServerProxy('http://' + host + ':' + str(port))
# response = server_proxy.request_identifier()
# print(response)

with SimpleXMLRPCServer((host, 0)) as rpc_server:
    rpc_server.register_introspection_functions()

    def test_connection():
        print('Server say ping')
        return 'RPC Client say pong'

    rpc_server.register_function(test_connection, 'ping')

    try:
        server_proxy.set_client_server(rpc_server.socket.getsockname())
        rpc_server.serve_forever()
    except Exception as exc:
        print('Error: ' + str(exc))

teste = server_proxy.set_callback(callback)
print(teste)

# s.connect((host, port))

# input_list = [sys.stdin, s]

# while True:
#     inputs, _, _ = select.select(input_list, [], [])
#     for ipt in inputs:
#         if ipt == s:
#             message = ipt.recv(1024)
#             if message:
#                 print(message.decode('utf-8'))
#             else:
#                 s.close()
#                 sys.exit()
#         else:
#             message = input()
#             if message == 'quit':
#                 s.close()
#                 sys.exit()
#             s.send(message.encode())
#             sys.stdout.write('Message sent: ' + message + '\n')
#             sys.stdout.flush()

# s.close()
