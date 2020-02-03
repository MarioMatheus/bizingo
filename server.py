from game import message, room
import socket
import sys
import threading
import logging
import select

def remove_connection(connection, address):
    if connection in users_queue.keys():
        users_queue.pop(connection)
        logging.info('Removed connection! | IP ' + address[0] + ' | PORT ' + str(address[1]))
    else:
        logging.debug('Not found connection! | IP ' + address[0] + ' | PORT ' + str(address[1]))

def handle_join_action(user, payload):
    hosts = list(filter(lambda user: users_queue[user]['room']['name'] == payload['name']))
    if len(hosts) == 0:
        logging.debug('Room not found')
        user.send('Room not found')
    else:
        host = hosts[0]
        if host['room']['password'] == payload['password']:
            logging.info('Creating new room')
            lock.acquire()
            users_queue.pop(host)
            users_queue.pop(user)
            lock.release()
            new_room = room.Room([ host['conn'], user ])
            new_room.setName('Room: ' + host['room']['name'])
            new_room.start()


def queue_thread():
    logging.info('Queue initiated!')
    messenger = message.GameMessage()
    while True:
        logging.debug('Checking new connections data')
        user_connections, _, _ = select.select(users_queue.keys(), [], [], 1.0)
        for user in user_connections:
            try:
                data = user.recv(1024)
                if data:
                    module, payload = messenger.decode(data)
                    logging.info('Received data | Module: ' + module + ' | payload: ' + payload)
                    if module == 'ROOM' and payload['action'] == 'create':
                        queue.acquire()
                        users_queue[user]['room'] = { 'name': payload['name'], 'password': payload['password'] }
                        queue.release()
                        logging.info('Creation request accepts | IP ' + users_queue[user]['addr'][0])
                    if module == 'ROOM' and payload['action'] == 'join':
                        logging.info('Checking request to join a room | IP ' + users_queue[user]['addr'][0])
                        handle_join_action(user, payload)
                else:
                    logging.debug('To remove connection | IP ' + users_queue[user]['addr'][0] + ' | PORT ' + str(users_queue[user]['addr'][1]))
                    remove_connection(user, users_queue[user]['addr'])
            except Exception as exception:
                logging.warning(str(exception.with_traceback()))
            except:
                logging.warning('Exception occured')
                continue


def append_in_queue(connection, address):
    lock.acquire()
    users_queue[connection] = { 'addr': address, 'room': { 'name': '', 'password': '' } }
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
    fileHandler = logging.FileHandler('socketpy.log')
    consoleHandler = logging.StreamHandler(sys.stdout)
    fileHandler.setFormatter(logFormatter)
    consoleHandler.setFormatter(logFormatter)
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
