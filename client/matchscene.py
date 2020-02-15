import arcade
from . import utils

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

class MatchScene:
    def __init__(self):
        self.sprite_list = arcade.SpriteList()
        self.half_width = SCREEN_WIDTH/2
        self.half_height = SCREEN_HEIGHT/2

        self.chat_msg_buffer = ''
        self.chat_messages = [('game', 'Bem Vindo!')]

        self.setup()

    def setup(self):
        self.setup_chat_sprites()

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
        pass

    def on_draw(self):
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
