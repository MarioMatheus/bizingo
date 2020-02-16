import logging
from copy import deepcopy
from . import originialboard

class Match:
    def __init__(self, players):
        self.turn = 0
        self.game_over = False
        self.winner = None
        self.players = players
        self.board = deepcopy(originialboard.board)

    def broadcast(self, message_data):
        from . import message
        for player in self.players:
            player.send(message.GameMessage().encode(message_data, 'MATCH'))

    def get_player_pieces_count(self, player):
        player_piece = self.players.index(player) + 1
        count = 0
        for row in self.board:
            count += row.count(player_piece) + row.count(player_piece * 10)
        return count

    def get_index_coordinate(self, coordinate):
        row_key = coordinate[0]
        column = coordinate[1:]
        row = ord(row_key) - 65
        return row, int(column) - 1

    def get_board_coordinate(self, row, column):
        x = chr(row + 65)
        return x + str(column+1)

    def get_piece_in_coordinate(self, coordinate):
        row, col = self.get_index_coordinate(coordinate)
        if row < 0 or col < 0:
            raise Exception('Invalid Coordinate')
        try:
            return self.board[row][col]
        except:
            raise Exception('Invalid Coordinate')

    def get_adjacent_triangles(self, row, column):
        up_lenght = len(self.board[row])-2 if row - 1 < 0 else len(self.board[row-1])
        col_offset_up = len(self.board[row]) - up_lenght
        col_offset_bottom = len(self.board[row]) - up_lenght
        col_offset_up -= 0 if row < 9 else -1 if row == 9 else -2
        col_offset_bottom -= 0 if row < 8 else -1 if row == 8 else -4 if row == 9 else 0
        adjacents = [
            (row-1, column-col_offset_up), (row-1, column+2-col_offset_up),
            (row, column-2), (row, column+2),
            (row+1, column+2-col_offset_bottom), (row+1, column+4-col_offset_bottom)
        ]
        def validate_inside_board(index_path):
            if index_path[0] >= len(self.board) or index_path[1] >= len(self.board[index_path[0]]):
                return False
            return index_path[0] >= 0 and index_path[1] >= 0

        return list(filter(validate_inside_board, adjacents))

    def swap_triangles_content(self, coordinate1, coordinate2):
        row1, col1 = self.get_index_coordinate(coordinate1)
        row2, col2 = self.get_index_coordinate(coordinate2)
        aux = self.board[row1][col1]
        self.board[row1][col1] = self.board[row2][col2]
        self.board[row2][col2] = aux

    def is_player_piece(self, player, piece):
        player_index = self.players.index(player)
        if player_index == 0 and (piece == 1 or piece == 10):
            return True
        if player_index == 1 and (piece == 2 or piece == 20):
            return True
        return False

    def remove_piece_from_board(self, coordinate, by):
        row, col = self.get_index_coordinate(coordinate)
        self.board[row][col] = 0
        return coordinate
        # self.broadcast({ 'event': 'capture', 'coordinate': coordinate })

    def enemy_bottom_triangle_coordinate(self, coordinate):
        row, column = self.get_index_coordinate(coordinate)
        row += 1
        column += 1 if row < 9 else 0 if row == 9 else -1
        return self.get_board_coordinate(row, column)
    
    def enemy_up_triangle_coordinate(self, coordinate):
        row, column = self.get_index_coordinate(coordinate)
        row -= 1
        column -= 1 if row < 8 else 0 if row == 8 else -1
        return self.get_board_coordinate(row, column)

    def get_enemies_triangles_coordinates_to_surround(self, coordinate):
        piece = self.get_piece_in_coordinate(coordinate)
        row_index = ord(coordinate[0]) - 65
        row_lenght = len(self.board[row_index])
        left_col_index = int(coordinate[1:]) - 1
        right_col_index = int(coordinate[1:]) + 1
        peak_row_index = row_index + (1 if piece in [1,10] else -1)
        coordinates = []
        if peak_row_index != -1 or peak_row_index != len(self.board):
            triangle = 1
            if (row_index < 9 and int(coordinate[1:]) % 2 == 0) or (row_index > 8 and int(coordinate[1:]) % 2 == 1):
                triangle = 2
            coordinates.append(self.enemy_bottom_triangle_coordinate(coordinate) if triangle == 1 else self.enemy_up_triangle_coordinate(coordinate))
        if left_col_index >= 1:
            coordinates.append(coordinate[0] + str(left_col_index))
        if right_col_index <= row_lenght:
            coordinates.append(coordinate[0] + str(right_col_index))

        coordinates.sort()
        coordinates.sort(key=lambda c: int(c[1:]))
        return coordinates

    def piece_is_surrounded(self, coordinate):
        piece = self.get_piece_in_coordinate(coordinate)
        if piece == 0:
            return False
        row_index = ord(coordinate[0]) - 65
        row_lenght = len(self.board[row_index])
        left_col_index = int(coordinate[1:]) - 1
        right_col_index = int(coordinate[1:]) + 1
        peak_row_index = row_index + (1 if piece in [1,10] else -1)
        if left_col_index < 1 or right_col_index > row_lenght or peak_row_index == -1 or peak_row_index == len(self.board):
            if piece in [10, 20]:
                return False
            piece *= 10
        left_piece = self.get_piece_in_coordinate(coordinate[0] + str(left_col_index)) if left_col_index > 0 else 1 if piece in [2, 20] else 2
        right_piece = self.get_piece_in_coordinate(coordinate[0] + str(right_col_index)) if right_col_index <= row_lenght else 1 if piece in [2, 20] else 2
        if not (left_piece in ([1, 10] if piece in [2, 20] else [2, 20]) and right_piece in ([1, 10] if piece in [2, 20] else [2, 20])):
            return False
        peak_piece = 1 if piece in [2, 20] else 2
        if not (peak_row_index == -1 or peak_row_index == len(self.board)):
            peak_piece_coordinate = self.enemy_bottom_triangle_coordinate(coordinate) if piece in [1, 10] else self.enemy_up_triangle_coordinate(coordinate)
            peak_piece = self.get_piece_in_coordinate(peak_piece_coordinate)
        if peak_piece not in ([1, 10] if piece in [2, 20] else [2, 20]):
            return False
        if piece == 1:
            return left_piece in [2, 20] and right_piece in [2, 20] and peak_piece in [2, 20]
        if piece == 10:
            return left_piece in [2, 20] and right_piece in [2, 20] and peak_piece in [2, 20] and 20 in [left_piece, right_piece, peak_piece]
        if piece == 2:
            return left_piece in [1, 10] and right_piece in [1, 10] and peak_piece in [1, 10]
        if piece == 20:
            return left_piece in [1, 10] and right_piece in [1, 10] and peak_piece in [1, 10] and 10 in [left_piece, right_piece, peak_piece]

    def check_custody_capture(self, player, coordinate):
        player_index = self.players.index(player)
        to_capture_coordinates = self.get_enemies_triangles_coordinates_to_surround(coordinate)
        for capture_coordinate in to_capture_coordinates:
            if self.piece_is_surrounded(capture_coordinate):
                return self.remove_piece_from_board(capture_coordinate, by=player)
        if self.piece_is_surrounded(coordinate):
            return self.remove_piece_from_board(coordinate, by=self.players[0 if player_index == 1 else 1])
        return ''

    def set_game_over(self, to):
        winner_index = 0 if self.players.index(to) == 1 else 1
        self.winner = self.players[winner_index]
        self.game_over = True
        logging.info('Game Over! Winner: Player ' + str(winner_index+1))
        self.broadcast({ 'event': 'gameover', 'winner': str(winner_index) })

    def move_piece(self, player, _from, to):
        player_index = self.players.index(player)
        player_turn = self.turn % 2
        
        if player_index != player_turn:
            raise Exception('Wait your turn')
        if _from == to:
            raise Exception('You cannot move to same position')

        ori_row, ori_col = self.get_index_coordinate(_from)
        if self.get_index_coordinate(to) not in self.get_adjacent_triangles(ori_row, ori_col):
            raise Exception('You can only move to adjacent triangles')

        piece = self.get_piece_in_coordinate(_from)
        if piece == 0 or not self.is_player_piece(player, piece):
            raise Exception('You can only move your pieces')
        if self.get_piece_in_coordinate(to) != 0:
            raise Exception('You can only move pieces to empty triangles')

        self.swap_triangles_content(_from, to)

        captured_piece = self.check_custody_capture(player, to)   

        for p in self.players:
            if self.get_player_pieces_count(p) == 2:
                return self.set_game_over(to=p)

        self.turn += 1
        self.broadcast({
            'event': 'movement',
            'from': _from,
            'to': to,
            'captured': captured_piece,
            'turn': str(self.turn)
        })
        logging.info('BC::Move piece from ' + _from + ' to ' + to + ' | Captured '+ captured_piece + ' | Turn ' + str(self.turn))

    def __str__(self):
        description = 'Match\nBoard:\n'
        offset = 8
        i = 0
        while i < len(self.board):
            for _ in range(offset):
                description += '   '
            description += str(self.board[i]) + '\n'
            offset = offset + 2 if i > 8 else offset - 1
            i += 1

        return description
