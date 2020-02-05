import logging
import select
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
                user.send(message_data)

class Room(Thread):
    def __init__(self, players):
        Thread.__init__(self)
        self.players = players
        self.chat = Chat(players.keys())
        self.message = message.GameMessage()
    
    def receive_data(self, data, from_player):
        module, payload = self.message.decode(data)
        if module == 'CHAT':
            self.receive_chat_msg(payload, from_player)
        elif module == 'MATCH':
            pass

    def receive_chat_msg(self, payload, player):
        try:
            message_data = self.message.encode(payload, 'CHAT')
            self.chat.broadcast_message(message_data, player)
            logging.info('Chat msg sent from player ' + self.players[player]['name'] + ' | IP ' + self.players[player]['addr'][0])
        except:
            logging.warning('Error to send message from player ' + self.players[player]['name'])

    def remove_player (self, player):
        if player in self.players:
            removed_player = self.players.pop(player)
            logging.info('Removed player ' + removed_player['name'] + ' | IP ' + removed_player['addr'][0])

    def broadcast(self, message):
        for player in self.players.keys():
            player.send(self.message.encode(message, 'MATCH'))

    def run(self):
        logging.debug(self.getName() + ' started')
        self.broadcast('Bem Vindo a Bizingo!')
        while True:
            read_connections, _, _ = select.select(list(self.players.keys()), [], [])
            for player in read_connections:
                try:
                    message = player.recv(1024)
                    if message:
                        self.receive_data(message, from_player=player)
                    else:
                        return self.remove_player(player)
                except:
                    logging.warn('Some Exception occurred')
                    continue
