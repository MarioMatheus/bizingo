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
            player.close()
            self.remove_player(player)

    def remove_player (self, player):
        if player in self.players:
            removed_player = self.players.pop(player)
            logging.info('Removed player ' + removed_player['name'] + ' | IP ' + removed_player['addr'][0])

    def run(self):
        logging.debug(self.getName() + ' started')
        while len(self.players) != 0:
            player = list(self.players.keys())[0]
            player.close()
            self.remove_player(player)
