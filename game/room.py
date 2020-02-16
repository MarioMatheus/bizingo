import logging
import select
from threading import Thread
import random
from . import message, match

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
        players_keys = list(players.keys())
        random.shuffle(players_keys)
        self.bizingo_match = match.Match(players_keys)
        self.chat = Chat(players_keys)
        self.message = message.GameMessage()
    
    def receive_data(self, data, from_player):
        module, payload = self.message.decode(data)
        if module == 'CHAT':
            self.receive_chat_msg(payload, from_player)
        elif module == 'MATCH':
            self.receive_match_msg(payload, from_player)

    def receive_chat_msg(self, payload, player):
        try:
            message_data = self.message.encode(payload, 'CHAT')
            self.chat.broadcast_message(message_data, player)
            logging.info('Chat msg sent from player ' + self.players[player]['name'] + ' | IP ' + self.players[player]['addr'][0])
        except:
            logging.warning('Error to send message from player ' + self.players[player]['name'])

    def receive_match_msg(self, payload, player):
        try:
            if payload['action'] == 'move':
                self.bizingo_match.move_piece(player, _from=payload['from'], to=payload['to'])
            if self.bizingo_match.game_over and self.bizingo_match.winner is not None:
                self.broadcast({ 'event': 'Game Over!', 'winner': self.players[self.bizingo_match.winner]['name'] })
                logging.info('Game Over!')
        except Exception as identifier:
            self.broadcast({ 'exception': str(identifier) }, to_player=player)
            logging.warning('Exception occurred ' + str(identifier))

    def remove_player (self, player):
        if player in self.players:
            removed_player = self.players.pop(player)
            logging.info('Removed player ' + removed_player['name'] + ' | IP ' + removed_player['addr'][0])

    def broadcast(self, message, to_player=None):
        if to_player is not None:
            return to_player.send(self.message.encode(message, 'MATCH'))
        for player in self.players.keys():
            player.send(self.message.encode(message, 'MATCH'))

    def run(self):
        logging.debug(self.getName() + ' started')
        for player in self.bizingo_match.players:
            player.send(
                self.message.encode({
                    'info': 'Bem Vindo a Bizingo!',
                    'is_initial_player': self.bizingo_match.players.index(player) == 0
                }, 'MATCH')
            )
        while True:
            read_connections, _, _ = select.select(list(self.players.keys()), [], [])
            for player in read_connections:
                try:
                    message = player.recv(1024)
                    if message:
                        self.receive_data(message, from_player=player)
                    else:
                        return self.remove_player(player)
                except Exception as m:
                    logging.error(str(m))
                except:
                    logging.warn('Some Exception occurred')
                    continue
