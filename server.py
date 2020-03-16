from game import message, room
from xmlrpc.server import SimpleXMLRPCServer
# import socket
import sys
import threading
import logging, logging.handlers
import select

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
