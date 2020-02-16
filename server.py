from game import message, room
import socket
import sys
import threading
import logging, logging.handlers
import select

def remove_connection(connection, address):
    if connection in users_queue.keys():
        users_queue.pop(connection)
        logging.info('Removed connection! | IP ' + address[0] + ' | PORT ' + str(address[1]))
    else:
        logging.debug('Not found connection! | IP ' + address[0] + ' | PORT ' + str(address[1]))


def handle_join_action(user, payload):
    def search_room(user_connection):
        exists = users_queue[user_connection]['room']['name'] == payload['room']
        return exists and user_connection != user

    hosts = list(filter(search_room, users_queue.keys()))

    if len(hosts) == 0:
        logging.debug('Room not found')
        user.send(message.GameMessage().encode({'res': 'Not found room to join'}, 'ROOM'))
    else:
        host = hosts[0]
        if users_queue[host]['room']['password'] == payload['password']:
            logging.info('Creating new room')
            lock.acquire()
            host_data = users_queue.pop(host)
            user_data = users_queue.pop(user)
            lock.release()
            logging.debug(str(host_data))
            host_room = host_data.pop('room')
            user.send(message.GameMessage().encode({'res': 'Join accepted'}, 'ROOM'))
            new_room = room.Room({ host: host_data, user: user_data })
            new_room.setName('Room: ' + host_room['name'])
            new_room.start()


def queue_thread():
    logging.info('Queue initiated!')
    messenger = message.GameMessage()
    while True:
        # logging.debug('Checking new connections data')
        user_connections, _, _ = select.select(users_queue.keys(), [], [], 1.0)
        for user in user_connections:
            try:
                data = user.recv(1024)
                if data:
                    module, payload = messenger.decode(data)
                    logging.debug('Received data | Module: ' + module + ' | payload: ' + str(payload))
                    if module == 'ROOM' and payload['action'] == 'create':
                        def search_room(user_connection):
                            return users_queue[user_connection]['room']['name'] == payload['room']
                        lock.acquire()
                        rooms = list(filter(search_room, users_queue.keys()))
                        if len(rooms) > 0:
                            user.send(messenger.encode({'res': 'Room already exist'}, 'ROOM'))
                            logging.info('Creation request rejected | IP ' + users_queue[user]['addr'][0])
                        else:
                            users_queue[user]['name'] = payload['name']
                            users_queue[user]['room'] = { 'name': payload['room'], 'password': payload['password'] }
                            user.send(messenger.encode({'res': 'Request accepted'}, 'ROOM'))
                            logging.info('Creation request accepts | IP ' + users_queue[user]['addr'][0])
                        lock.release()
                    if module == 'ROOM' and payload['action'] == 'join':
                        logging.info('Checking request to join a room | IP ' + users_queue[user]['addr'][0])
                        users_queue[user]['name'] = payload['name']
                        handle_join_action(user, payload)
                else:
                    logging.debug('To remove connection | IP ' + users_queue[user]['addr'][0] + ' | PORT ' + str(users_queue[user]['addr'][1]))
                    remove_connection(user, users_queue[user]['addr'])
            except Exception as exception:
                logging.warning(str(exception.with_traceback()))
            except:
                logging.warning('Exception occurred')
                continue


def append_in_queue(connection, address):
    lock.acquire()
    users_queue[connection] = { 'addr': address, 'name': '', 'room': { 'name': '', 'password': '' } }
    lock.release()
    logging.info('Connection added to queue | IP ' + address[0] + ' | PORT ' + str(address[1]))
    logging.debug('Queue: ' + str(list(map(lambda conn: users_queue[conn]['addr'][0], users_queue.keys()))))


def create_socket():
    try:
        s = socket.socket()
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
        return s
    except socket.error as message:
        logging.error('Error on create socket: ' + message)


def bind_socket():
    try:
        logging.info('Binding port ' + str(port))
        s.bind((host, port))
        s.listen(10)
        queue.start()
    except socket.error as message:
        logging.error('Error on bind socket: ' + message + "\nRetrying...")
        bind_socket()


def socket_accept():
    while True:
        logging.info('Waiting for new connections')
        connection, address = s.accept()
        logging.info('Connection has been stablished! | IP ' + address[0] + ' | PORT ' + str(address[1]))
        append_in_queue(connection, address)


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
    users_queue = {}
    queue = threading.Thread(target=queue_thread, args=(), name='Thread-Queue')
    lock = threading.Lock()
    configLogger()
    s = create_socket()
    bind_socket()
    socket_accept()
    s.close()
