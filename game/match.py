
class Match:
    def __init__(self, players):
        self.turn = 0
        self.players = players
        self.board = [
                                    [0, 0, 0, 0, 0],
                                 [0, 0, 0, 0, 0, 0, 0],
                              [0, 0, 1, 0, 1, 0, 1, 0, 0],
                           [0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0],
                        [0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0],
                     [0, 0, 1, 0,10, 0, 1, 0, 1, 0,10, 0, 1, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
               [0, 0, 0, 2, 0,20, 0, 2, 0, 2, 0, 2, 0,20, 0, 2, 0, 0, 0],
            [0, 0, 0, 0, 0, 2, 0, 2, 0, 2, 0, 2, 0, 2, 0, 2, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 2, 0, 2, 0, 2, 0, 2, 0, 2, 0, 0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        ]

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
        print('peca capturada pelo player ' + str(by) + ' em ' + coordinate)
        row, col = self.get_index_coordinate(coordinate)
        self.board[row][col] = 0

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
        row, column = self.get_index_coordinate(coordinate)
        adjacent_triangles = self.get_adjacent_triangles(row, column)
        adjacent_pieces = list(map(lambda c: self.get_board_coordinate(c[0], c[1]), adjacent_triangles))
        coordinates = list(filter(lambda c: self.get_piece_in_coordinate(c) in [1, 10] if player_index == 0 else [2, 20], adjacent_pieces)) + [coordinate]
        if len(coordinates) > 2:
            for c in coordinates:
                same_triangles_row = list(filter(lambda coord: c[0] == coord[0], coordinates))
                same_triangles_row.sort(key=lambda c: int(c[1:]))
                if (len(same_triangles_row) == 2 and
                    True in list(map(lambda c: c[0] == chr(ord(same_triangles_row[0][0]) + (- 1 if player_index == 0 else 1)) and int(c[1]) in range(int(same_triangles_row[0][1]), int(same_triangles_row[1][1])+1), coordinates)) and
                    self.get_piece_in_coordinate(same_triangles_row[0][0] + str(int(same_triangles_row[0][1]) + 1)) in [2, 20]
                ):
                    up_triangle_map = list(map(lambda c: c[0] == chr(ord(same_triangles_row[0][0]) + (- 1 if player_index == 0 else 1)) and int(c[1]) in range(int(same_triangles_row[0][1]), int(same_triangles_row[1][1])+1), coordinates))
                    up_triangle = coordinates[up_triangle_map.index(True)]
                    captured_piece_coordinate = same_triangles_row[0][0] + str(int(same_triangles_row[0][1]) + 1)
                    captured_piece = self.get_piece_in_coordinate(captured_piece_coordinate)
                    if captured_piece == 2 if player_index == 0 else 1:
                        return self.remove_piece_from_board(captured_piece_coordinate, by=player)
                    elif 10 if player_index == 0 else 20 in list(map(lambda c: self.get_piece_in_coordinate(c), same_triangles_row + [up_triangle])):
                        return self.remove_piece_from_board(captured_piece_coordinate, by=player)
                            
        # check if player captured a piece
        # check if player was captured
        pass

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
        self.check_custody_capture(player, to)

        self.turn += 1


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

# m = Match(['P1', 'P2'])
# m.board[10][1] = 1
# m.board[10][0] = 20
# m.board[10][2] = 2
# m.piece_is_surrounded('K2')
# m.check_custody_capture('P2', 'H8')
