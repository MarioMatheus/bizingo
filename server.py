from game import message, room
from xmlrpc.server import SimpleXMLRPCServer
# import socket
import sys
import threading
import logging, logging.handlers
import select

# def remove_connection(connection, address):
#     if connection in users_queue.keys():
#         users_queue.pop(connection)
#         logging.info('Removed connection! | IP ' + address[0] + ' | PORT ' + str(address[1]))
#     else:
#         logging.debug('Not found connection! | IP ' + address[0] + ' | PORT ' + str(address[1]))


# def handle_join_action(user, payload):
#     def search_room(user_connection):
#         exists = users_queue[user_connection]['room']['name'] == payload['room']
#         return exists and user_connection != user

#     hosts = list(filter(search_room, users_queue.keys()))

#     if len(hosts) == 0:
#         logging.debug('Room not found')
#         user.send(message.GameMessage().encode({'res': 'Not found room to join'}, 'ROOM'))
#     else:
#         host = hosts[0]
#         if users_queue[host]['room']['password'] == payload['password']:
#             logging.info('Creating new room')
#             lock.acquire()
#             host_data = users_queue.pop(host)
#             user_data = users_queue.pop(user)
#             lock.release()
#             logging.debug(str(host_data))
#             host_room = host_data.pop('room')
#             user.send(message.GameMessage().encode({'res': 'Join accepted'}, 'ROOM'))
#             new_room = room.Room({ host: host_data, user: user_data })
#             new_room.setName('Room: ' + host_room['name'])
#             new_room.start()


# def queue_thread():
#     logging.info('Queue initiated!')
#     messenger = message.GameMessage()
#     while True:
#         # logging.debug('Checking new connections data')
#         user_connections, _, _ = select.select(users_queue.keys(), [], [], 1.0)
#         for user in user_connections:
#             try:
#                 data = user.recv(1024)
#                 if data:
#                     module, payload = messenger.decode(data)
#                     logging.debug('Received data | Module: ' + module + ' | payload: ' + str(payload))
#                     if module == 'ROOM' and payload['action'] == 'create':
#                         def search_room(user_connection):
#                             return users_queue[user_connection]['room']['name'] == payload['room']
#                         lock.acquire()
#                         rooms = list(filter(search_room, users_queue.keys()))
#                         if len(rooms) > 0:
#                             user.send(messenger.encode({'res': 'Room already exist'}, 'ROOM'))
#                             logging.info('Creation request rejected | IP ' + users_queue[user]['addr'][0])
#                         else:
#                             users_queue[user]['name'] = payload['name']
#                             users_queue[user]['room'] = { 'name': payload['room'], 'password': payload['password'] }
#                             user.send(messenger.encode({'res': 'Request accepted'}, 'ROOM'))
#                             logging.info('Creation request accepts | IP ' + users_queue[user]['addr'][0])
#                         lock.release()
#                     if module == 'ROOM' and payload['action'] == 'join':
#                         logging.info('Checking request to join a room | IP ' + users_queue[user]['addr'][0])
#                         users_queue[user]['name'] = payload['name']
#                         handle_join_action(user, payload)
#                 else:
#                     logging.debug('To remove connection | IP ' + users_queue[user]['addr'][0] + ' | PORT ' + str(users_queue[user]['addr'][1]))
#                     remove_connection(user, users_queue[user]['addr'])
#             except Exception as exception:
#                 logging.warning(str(exception.with_traceback()))
#             except:
#                 logging.warning('Exception occurred')
#                 continue


# def append_in_queue(connection, address):
#     lock.acquire()
#     users_queue[connection] = { 'addr': address, 'name': '', 'room': { 'name': '', 'password': '' } }
#     lock.release()
#     logging.info('Connection added to queue | IP ' + address[0] + ' | PORT ' + str(address[1]))
#     logging.debug('Queue: ' + str(list(map(lambda conn: users_queue[conn]['addr'][0], users_queue.keys()))))


# def create_socket():
#     try:
#         s = socket.socket()
#         s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
#         return s
#     except socket.error as message:
#         logging.error('Error on create socket: ' + message)


# def bind_socket():
#     try:
#         logging.info('Binding port ' + str(port))
#         s.bind((host, port))
#         s.listen(10)
#         queue.start()
#     except socket.error as message:
#         logging.error('Error on bind socket: ' + message + "\nRetrying...")
#         bind_socket()


# def socket_accept():
#     while True:
#         logging.info('Waiting for new connections')
#         connection, address = s.accept()
#         logging.info('Connection has been stablished! | IP ' + address[0] + ' | PORT ' + str(address[1]))
#         append_in_queue(connection, address)

def create_match(host_id, user_id):
    host_data = users_queue.pop(host_id)
    user_data = users_queue.pop(user_id)
    new_room = room.Room({
        host_id: { **host_data, 'addr': connected_players[host_id] },
        user_id: { **user_data, 'addr': connected_players[user_id] }
    })
    new_room.setName('ROOM: ' + host_data['room']['name'])
    match_rooms.append(new_room)
    new_room.start()

def create_room(user_id, username, room_name, room_password):
    def search_room(user_id):
        return users_queue[user_id]['room']['name'] == room_name
    rooms = list(filter(search_room, users_queue.keys())) if user_id in users_queue.keys() else []
    if len(rooms) > 0:
        logging.info('Creation request rejected | ID ' + user_id)
        return (False, 'Room already exist')
    else:
        users_queue[user_id] = {
            'name': username,
            'room': { 'name': room_name, 'password': room_password }
        }
        logging.info('Creation request accepts | IP ' + user_id)
        return (True, 'Request accepted')


def join_room(user_id, username, room_name, room_password):
    logging.info('Checking request to join a room | IP ' + user_id)

    users_queue[user_id] = {
        'name': username,
        'room': { 'name': room_name, 'password': room_password }
    }

    def search_room(_user_id):
        exists = users_queue[_user_id]['room']['name'] == room_name
        return exists and _user_id != user_id

    hosts = list(filter(search_room, users_queue.keys()))

    if len(hosts) == 0:
        logging.debug('Room not found')
        return (False, 'Not found room to join')
    else:
        host_id = hosts[0]
        if users_queue[host_id]['room']['password'] == room_password:
            logging.info('Creating new room')
            create_match(host_id, user_id)
            return (True, 'Join accepted')


def get_room_where_user_is(user_id):
    room = list(filter(lambda room: user_id in room.players.keys(), match_rooms))
    if room:
        return room[0]


def send_message(user_id, message):
    room = get_room_where_user_is(user_id)
    if room:
        room.receive_chat_msg(message, user_id)
        return message
    return ''

def giveup_the_match(user_id):
    room = get_room_where_user_is(user_id)
    if room:
        return room.receive_match_msg({ 'action': 'giveup' }, user_id)
    return ('',)

def request_rematch(user_id):
    room = get_room_where_user_is(user_id)
    if room:
        return room.receive_match_msg({ 'action': 'rematch', 'op': 'request' }, user_id)
    return False

def reply_rematch(user_id, reply):
    room = get_room_where_user_is(user_id)
    if room:
        return room.receive_match_msg({ 'action': 'rematch', 'op': reply }, user_id)
    return ()

def move_piece(user_id, _from, to):
    room = get_room_where_user_is(user_id)
    if room:
        return room.receive_match_msg({ 'action': 'move', 'from': _from, 'to': to }, user_id)
    return ()

def generate_id():
    from uuid import uuid4
    return str(uuid4())

def close(user_id):
    logging.info('Player disconnected with id: ' + user_id)
    connected_players.pop(user_id)
    if user_id in users_queue:
        users_queue.pop(user_id)

def create_rpc_server():
    with SimpleXMLRPCServer((host, port)) as rpc_server:
        rpc_server.register_introspection_functions()

        def request_identifier(address):
            identifier = generate_id()
            while identifier in connected_players.keys():
                identifier = generate_id()
            connected_players[identifier] = address
            logging.info('Player connected with identifier: ' + identifier)
            return identifier

        rpc_server.register_function(request_identifier)
        rpc_server.register_function(close)
        rpc_server.register_function(create_room)
        rpc_server.register_function(join_room)
        rpc_server.register_function(send_message)
        rpc_server.register_function(giveup_the_match)
        rpc_server.register_function(request_rematch)
        rpc_server.register_function(reply_rematch)
        rpc_server.register_function(move_piece)

        try:
            logging.info('RPC Server on')
            rpc_server.serve_forever()
        except Exception as exc:
            logging.error('Exception at start RPC Server: ' + str(exc))


def configLogger():
    logFormatter = logging.Formatter('%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s')
    consoleHandler = logging.StreamHandler(sys.stdout)
    consoleHandler.setFormatter(logFormatter)
    fileHandler = logging.handlers.TimedRotatingFileHandler('logs/bizingo', when='midnight', interval=1)
    fileHandler.suffix = '%Y%m%d.log'
    fileHandler.setFormatter(logFormatter)
    logging.basicConfig(level=logging.DEBUG, handlers=[fileHandler, consoleHandler])


if __name__ == "__main__":
    host = ''
    port = 9999
    connected_players = {}
    users_queue = {}
    match_rooms = []
    configLogger()
    create_rpc_server()
    # queue = threading.Thread(target=queue_thread, args=(), name='Thread-Queue')
    # lock = threading.Lock()
    # s = create_socket()
    # bind_socket()
    # socket_accept()
    # s.close()
