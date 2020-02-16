import arcade
from copy import deepcopy
from . import utils
from game import originialboard
from game.message import GameMessage

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

INITIAL_BOARD_COORDINATE = (485.6, SCREEN_HEIGHT - 36)

T_WIDTH = 45 # 42.9
T_HEIGHT = 38.9

P2_CAPTAIN_RES = ':resources:images/animated_characters/robot/robot_idle.png'
P2_SOLDIER_RES = ':resources:images/enemies/slimeBlue.png'
P1_CAPTAIN_RES = ':resources:images/animated_characters/zombie/zombie_idle.png'
P1_SOLDIER_RES = ':resources:images/enemies/slimeGreen.png'


class MatchScene:
    def __init__(self, connection, is_initial_player):
        self.connection = connection
        self.is_initial_player = is_initial_player
        self.turn = 0

        self.sprite_list = arcade.SpriteList()
        self.half_width = SCREEN_WIDTH/2
        self.half_height = SCREEN_HEIGHT/2

        self.chat_msg_buffer = ''
        self.chat_messages = [('game', 'Bem Vindo!')]

        self.board = deepcopy(originialboard.board)
        self.board_coordinates = deepcopy(originialboard.board)
        self.board_coordinates_center = deepcopy(originialboard.board)

        self.selected_coordinate = None
        self.accessible_positions = []

        self.setup()

    def setup(self):
        self.load_textures()
        self.setup_chat_sprites()
        self.setup_board_sprites()
        self.setup_board_coordinates()
        self.setup_board_coordinates_center()

    def load_textures(self):
        self.background = arcade.load_texture(":resources:images/backgrounds/abstract_2.jpg")
        self.p1_captain_texture = arcade.load_texture(P1_CAPTAIN_RES)
        self.p1_soldier_texture = arcade.load_texture(P1_SOLDIER_RES)
        self.p2_captain_texture = arcade.load_texture(P2_CAPTAIN_RES)
        self.p2_soldier_texture = arcade.load_texture(P2_SOLDIER_RES)

    def setup_chat_sprites(self):
        chat_bg = arcade.Sprite(':resources:gui_themes/Fantasy/Menu/Menu.png')
        chat_bg.center_x = 130
        chat_bg.center_y = self.half_height
        chat_bg.width = 300
        chat_bg.height = 1000
        chat_text_box = arcade.Sprite(':resources:gui_themes/Fantasy/TextBox/Brown.png')
        chat_text_box.center_x = 130
        chat_text_box.center_y = 20
        chat_text_box.width = 250
        chat_text_box.height = 40
        self.sprite_list.append(chat_bg)
        self.sprite_list.append(chat_text_box)

    def setup_board_sprites(self):
        board_sprite = arcade.Sprite('res/bizingo-board.png')
        board_sprite.center_x = 530
        board_sprite.center_y = self.half_height + 50
        self.sprite_list.append(board_sprite)

    def setup_board_coordinates(self):
        for i in range(len(self.board)):
            y = INITIAL_BOARD_COORDINATE[1] - T_HEIGHT * i
            x_offset = i * T_WIDTH/2
            x_offset = x_offset if i < 9 else x_offset + T_WIDTH * (9-i)
            for j in range(len(self.board[i])):
                x = INITIAL_BOARD_COORDINATE[0] + T_WIDTH * (j if j % 2 == (0 if i < 9 else 1) else j-1) / 2 - x_offset
                x = x if i < 9 else x + T_WIDTH/2
                if i < 9:
                    if j % 2 == 0:
                        self.board_coordinates[i][j] = [(x, y), (x-T_WIDTH/2, y-T_HEIGHT), (x+T_WIDTH/2, y-T_HEIGHT)]
                    else:
                        self.board_coordinates[i][j] = [(x, y), (x+T_WIDTH, y), (x+T_WIDTH/2, y-T_HEIGHT)]
                else:
                    if j % 2 == 0:
                        self.board_coordinates[i][j] = [(x, y), (x+T_WIDTH, y), (x+T_WIDTH/2, y-T_HEIGHT)]
                    else:
                        self.board_coordinates[i][j] = [(x, y), (x-T_WIDTH/2, y-T_HEIGHT), (x+T_WIDTH/2, y-T_HEIGHT)]

    def setup_board_coordinates_center(self):
        for i, row in enumerate(self.board_coordinates):
            for j, point_list in enumerate(row):
                self.board_coordinates_center[i][j] = (
                    (point_list[0][0] + point_list[1][0] + point_list[2][0]) / 3,
                    (point_list[0][1] + point_list[1][1] + point_list[2][1]) / 3 + 8
                )
    
    def get_index_coordinate(self, coordinate):
        row_key = coordinate[0]
        column = coordinate[1:]
        row = ord(row_key) - 65
        return row, int(column) - 1

    def get_board_coordinate(self, row, column):
        x = chr(row + 65)
        return x + str(column+1)

    def get_triangle_coordinate_in_position(self, x, y):
        for i, row in enumerate(self.board_coordinates):
            for j, point_list in enumerate(row):
                if arcade.is_point_in_polygon(x, y, point_list):
                    return self.get_board_coordinate(i, j)
        return None

    def append_chat_message(self, sender, message):
        if sender == 'you':
            self.connection.send(GameMessage().encode({'msg': message}, 'CHAT'))
        self.chat_messages.insert(0, (sender, message))

    def receive_move_action(self, _from, to):
        self.swap_triangles_content(_from, to)

    def receive_capture_action(self, at):
        self.remove_piece_from_board(at)

    def receive_message(self, message):
        self.append_chat_message('player2', message)

    def check_piece_move(self, coordinate):
        if coordinate in map(lambda p: self.get_board_coordinate(p[0], p[1]), self.accessible_positions):
            self.connection.send(
                GameMessage().encode({
                    'action': 'move',
                    'from': self.selected_coordinate,
                    'to': coordinate
                }, 'MATCH')
            )

    def on_draw_chat(self):
        if self.chat_msg_buffer:
            arcade.draw_text(self.chat_msg_buffer, 15, 10, arcade.color.WHITE, 12)
        for i, msg in enumerate(self.chat_messages[:25]):
            arcade.draw_text(msg[1],
                20 if msg[0] in ['you', 'game'] else 230, 50 + 25 * i,
                arcade.color.SMOKY_BLACK if msg[0]=='you' else arcade.color.PURPLE if msg[0]=='game' else arcade.color.BLUE_GREEN,
                12, bold=(msg[0]=='game'),
                anchor_x='left' if msg[0] in ['you', 'game'] else 'right'
            )

    def draw_pieces(self):
        for i, row in enumerate(self.board):
            for j, t_content in enumerate(row):
                if t_content != 0:
                    piece_texture = ''
                    piece_point = self.board_coordinates_center[i][j]
                    if t_content == 1:
                        piece_texture = self.p1_soldier_texture
                    elif t_content == 10:
                        piece_texture = self.p1_captain_texture
                    elif t_content == 2:
                        piece_texture = self.p2_soldier_texture
                    elif t_content == 20:
                        piece_texture = self.p2_captain_texture
                    texture_alpha = 155 if self.get_board_coordinate(i, j) == self.selected_coordinate else 255
                    arcade.draw_lrwh_rectangle_textured(piece_point[0]-15, piece_point[1]-17.5, 30, 35, piece_texture, alpha=texture_alpha)

    def draw_accessible_triangles(self):
        for i, j in self.accessible_positions:
            position = self.board_coordinates_center[i][j]
            arcade.draw_circle_filled(position[0], position[1] - 8, 8, arcade.color.REDWOOD)

    def on_draw_board(self):
        self.draw_pieces()
        if self.turn % 2 == (0 if self.is_initial_player else 1):
            self.draw_accessible_triangles()

    def on_draw_hud(self):
        arcade.draw_text('Turn: ' + str(self.turn+1), 350, 40, arcade.color.COOL_BLACK, 18)

    def on_draw(self):
        arcade.draw_lrwh_rectangle_textured(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, self.background)
        self.sprite_list.draw()
        self.on_draw_chat()
        self.on_draw_board()
        self.on_draw_hud()

    def on_mouse_release(self, x, y, button, key_modifiers):
        piece = 1 if self.is_initial_player else 2

        if (self.turn % 2) + 1 not in [piece, piece*10]:
            return
        
        board_coordinate = self.get_triangle_coordinate_in_position(x, y)
        
        if self.selected_coordinate:
            row, col = self.get_index_coordinate(self.selected_coordinate)
            if self.board[row][col] in [piece, piece*10] and len(self.accessible_positions) > 0:
                self.check_piece_move(board_coordinate)
        self.selected_coordinate = board_coordinate
        if board_coordinate is not None:
            i, j = self.get_index_coordinate(board_coordinate)
            self.accessible_positions = self.get_adjacent_empty_triangles(i, j) if self.board[i][j] in [piece, piece*10] else []
        else:
            self.accessible_positions = []          

    def on_key_release(self, symbol, modifiers):
        if symbol == 65293 and self.chat_msg_buffer:
            self.append_chat_message('you', self.chat_msg_buffer)
            self.chat_msg_buffer = ''
            return
        char = utils.map_key_symbol_to_char(symbol)
        if char == 'del' and len(self.chat_msg_buffer) > 0:
            self.chat_msg_buffer = self.chat_msg_buffer[:-1]
        elif char != 'del' and len(self.chat_msg_buffer) < 32:
            self.chat_msg_buffer += char

    def swap_triangles_content(self, coordinate1, coordinate2):
        row1, col1 = self.get_index_coordinate(coordinate1)
        row2, col2 = self.get_index_coordinate(coordinate2)
        aux = self.board[row1][col1]
        self.board[row1][col1] = self.board[row2][col2]
        self.board[row2][col2] = aux

    def remove_piece_from_board(self, coordinate):
        row, col = self.get_index_coordinate(coordinate)
        self.board[row][col] = 0

    def get_adjacent_empty_triangles(self, row, column):
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
            valid_position = index_path[0] >= 0 and index_path[1] >= 0
            return valid_position and self.board[index_path[0]][index_path[1]] == 0

        return list(filter(validate_inside_board, adjacents))
