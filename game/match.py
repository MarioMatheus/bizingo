
class Match:
    def __init__(self, players):
        self.turn = 1
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
        row_key, column = coordinate
        row = ord(row_key) - 65
        return row, int(column) - 1

    def get_board_coordinate(self, row, column):
        x = chr(row + 65)
        return x + str(column+1)

    def get_piece_in_coodinate(self, coordinate):
        row, col = self.get_index_coordinate(coordinate)
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

    def move_piece(self, player, _from, to):
        player_index = self.players.index(player)
        player_turn = self.turn % 2
        if player_index != player_turn:
            raise Exception('Wait your turn')
        piece = self.get_piece_in_coodinate(_from)
        if piece == 0 or piece % 2 != player_turn:
            raise Exception('You can only move your pieces')
        if self.get_piece_in_coodinate(to) != 0:
            raise Exception('You can only move pieces to empty triangles')

        # if move to adjacent triangle
        # if triangles has same types

        self.swap_triangles_content(_from, to)


    
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

m = Match([])
m.get_adjacent_triangles(8, 20)
