import arcade
from . import utils
from game import originialboard

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

INITIAL_BOARD_COORDINATE = (485.6, SCREEN_HEIGHT - 36)

T_WIDTH = 45 # 42.9
T_HEIGHT = 38.9


class MatchScene:
    def __init__(self):
        self.sprite_list = arcade.SpriteList()
        self.half_width = SCREEN_WIDTH/2
        self.half_height = SCREEN_HEIGHT/2

        self.chat_msg_buffer = ''
        self.chat_messages = [('game', 'Bem Vindo!')]

        self.board = originialboard.board.copy()
        self.board_coordinates = originialboard.board.copy()

        self.setup()

    def setup(self):
        self.background = arcade.load_texture(":resources:images/backgrounds/abstract_2.jpg")
        self.setup_chat_sprites()
        self.setup_board_sprites()
        self.setup_board_coordinates()

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


    def on_draw_chat(self):
        if self.chat_msg_buffer:
            arcade.draw_text(self.chat_msg_buffer, 15, 10, arcade.color.WHITE, 12)
        for i, msg in enumerate(self.chat_messages[:25]):
            arcade.draw_text(msg[1],
                15 if msg[0] in ['you', 'game'] else 200, 50 + 25 * i,
                arcade.color.BLACK_OLIVE, 12, bold=(msg[0]=='game'),
                align='left' if msg[0] in ['you', 'game'] else 'right'
            )

    def on_draw_board(self):
        # arcade.draw_point(INITIAL_BOARD_COORDINATE[0], INITIAL_BOARD_COORDINATE[1], arcade.color.BLACK, 1)
        # arcade.draw_point(INITIAL_BOARD_COORDINATE[0] - T_WIDTH/2, INITIAL_BOARD_COORDINATE[1] - T_HEIGHT, arcade.color.BLACK, 1)
        # arcade.draw_point(INITIAL_BOARD_COORDINATE[0] + T_WIDTH/2, INITIAL_BOARD_COORDINATE[1] - T_HEIGHT, arcade.color.BLACK, 1)
        for row in self.board_coordinates:
            for col in row:
                for point in col:
                    arcade.draw_point(point[0], point[1], arcade.color.BLACK, 4)

    def on_draw(self):
        arcade.draw_lrwh_rectangle_textured(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, self.background)

        self.sprite_list.draw()
        self.on_draw_chat()
        self.on_draw_board()

    def on_key_release(self, symbol, modifiers):
        if symbol == 65293 and self.chat_msg_buffer:
            self.chat_messages.insert(0, ('you', self.chat_msg_buffer))
            self.chat_msg_buffer = ''
            return
        char = utils.map_key_symbol_to_char(symbol)
        if char == 'del' and len(self.chat_msg_buffer) > 0:
            self.chat_msg_buffer = self.chat_msg_buffer[:-1]
        elif char != 'del' and len(self.chat_msg_buffer) < 32:
            self.chat_msg_buffer += char
