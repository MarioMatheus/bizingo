import logging
from threading import Thread
from . import message

class Chat:
    def __init__(self, users):
        self.users = users
        self.messages = []

    def broadcast_message(self, message_data, client):
        self.messages.append(message_data)
        for user in self.users:
            if user != client:
                user.send(message)

class Room(Thread):
    def __init__(self, players):
        Thread.__init__(self)
        self.players = players
        self.chat = Chat(players)
        self.message = message.GameMessage()
    
    def receive_data(self, data, from_client):
        module, payload = self.message.decode(data)
        if module == 'CHAT':
            self.receive_chat_msg(payload, from_client)
        elif module == 'MATCH':
            pass

    def receive_chat_msg(self, payload, client):
        try:
            message_data = self.message.encode(payload, 'CHAT')
            self.chat.broadcast_message(message_data, client)
        except:
            client.close()
            self.remove_connection(client)

    def remove_connection(self, connection):
        if connection in self.players:
            self.players.remove(connection)
            logging.info('Removed player!')

    def run(self):
        logging.debug('Room created')
