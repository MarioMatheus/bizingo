import arcade
import random
import os
import socket

from . import utils, components

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Bizingo"

class BizingoGame(arcade.Window):

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        self.conn_socket = socket.socket()

        self.log = ''

        self.server_address = 'server:80'
        self.connected = False

        self.room_mode = 'Create'
        self.active_room_field = 'name'
        self.in_room_standby = False

        self.room_name = 'sala1'
        self.room_password = 'pass'

        self.button_list = None

        self.half_width = self.width/2
        self.half_height = self.height/2
        self.theme = None

        self.name_field_rect = (self.half_width, self.half_height, 340, 35)
        self.password_field_rect = (self.half_width, self.half_height-50, 340, 35)
        self.name_field_color = arcade.color.WHITE_SMOKE
        self.password_field_color = arcade.color.BLACK_BEAN

    def setup(self):
        self.button_list = []
        self.sprite_list = arcade.SpriteList()

        arcade.set_background_color(arcade.color.ALICE_BLUE)
        self.background = arcade.load_texture(":resources:images/backgrounds/abstract_1.jpg")

        self.add_menu_sprites()
        self.set_theme()
        self.add_conn_dialogue_box()
        self.add_room_dialogue_box()
        self.add_button()

    def add_menu_sprites(self):
        title = arcade.Sprite('res/bizingo_logo.png')
        title.center_x = self.half_width
        title.center_y = self.half_height + 100
        flag = arcade.Sprite(':resources:images/items/flagRed1.png')
        flag.center_x = self.width - 266
        flag.center_y = self.half_height * 1.8  
        flag.scale = 0.3
        self.sprite_list.append(title)
        self.sprite_list.append(flag)

    def set_theme(self):
        self.theme = arcade.gui.Theme()
        self.set_dialogue_box_texture()
        self.set_button_texture()
        self.theme.set_font(20, arcade.color.WINE)

    def set_dialogue_box_texture(self):
        self.theme.add_dialogue_box_texture(':resources:gui_themes/Fantasy/DialogueBox/DialogueBox.png')

    def set_button_texture(self):
        normal = ":resources:gui_themes/Fantasy/Buttons/Normal.png"
        hover = ":resources:gui_themes/Fantasy/Buttons/Hover.png"
        clicked = ":resources:gui_themes/Fantasy/Buttons/Clicked.png"
        locked = ":resources:gui_themes/Fantasy/Buttons/Locked.png"
        self.theme.add_button_textures(normal, hover, clicked, locked)

    def add_conn_dialogue_box(self):
        color = (220, 228, 255)
        dialoguebox = arcade.gui.DialogueBox(self.half_width, self.half_height, self.half_width*1.1,
                                             self.half_height*1.5, color, self.theme)
        dialoguebox.color = arcade.color.BLACK_LEATHER_JACKET
        conn_button = components.CloseDialogButton(dialoguebox, self.half_width, self.half_height-(self.half_height/2) + 80, width=160, text="Connect", on_will_close=self.create_connection, theme=self.theme)
        close_button = components.CloseDialogButton(dialoguebox, self.half_width, self.half_height-(self.half_height/2) + 20, on_will_close=self.conn_will_close, theme=self.theme)
        dialoguebox.button_list.append(conn_button)
        dialoguebox.button_list.append(close_button)
        message = "Type Server Address"
        
        dialoguebox.text_list.append(arcade.gui.TextLabel(message, self.half_width, self.half_height + 60, self.theme.font_color))
        self.dialogue_box_list.append(dialoguebox)

    def add_room_dialogue_box(self):
        color = (220, 228, 255)
        dialoguebox = arcade.gui.DialogueBox(self.half_width, self.half_height, self.half_width*1.1,
                                             self.half_height*1.5, color, self.theme)
        conn_button = components.CloseDialogButton(dialoguebox, self.half_width, self.half_height-(self.half_height/2) + 45, width=160, text=self.room_mode, on_will_close=self.handle_room_action,theme=self.theme)
        close_button = components.CloseDialogButton(dialoguebox, self.half_width, self.half_height-(self.half_height/2) - 10, theme=self.theme)
        dialoguebox.button_list.append(conn_button)
        dialoguebox.button_list.append(close_button)
        message = "Room Info"
        
        dialoguebox.text_list.append(arcade.gui.TextLabel(message, self.half_width, self.half_height + 60, self.theme.font_color))
        self.dialogue_box_list.append(dialoguebox)

    def add_button(self):
        show_conn_button = components.ShowDialogButton(self.dialogue_box_list[0], self.width-150, self.half_height * 1.8, theme=self.theme)
        create_room_button = components.ShowDialogButton(self.dialogue_box_list[1], self.half_width, self.half_height - 140, text='Create', on_will_active=self.set_room_to_create_mode,theme=self.theme)
        join_room_button = components.ShowDialogButton(self.dialogue_box_list[1], self.half_width, self.half_height - 80, text='Join', on_will_active=self.set_room_to_join_mode, theme=self.theme)
        
        self.button_list.append(show_conn_button)
        self.button_list.append(create_room_button)
        self.button_list.append(join_room_button)

    def on_draw(self):
        arcade.start_render()
        super().on_draw()

        if self.dialogue_box_list[0].active:
            arcade.draw_text('Options', self.half_width-50, self.half_height+170, arcade.color.BLACK, 22)
            arcade.draw_rectangle_outline(
                self.half_width, self.half_height, 340, 35,
                arcade.color.WHITE_SMOKE
            )
            if self.server_address:
                arcade.draw_text(self.server_address, self.half_width-160, self.half_height-12, arcade.color.BLACK, 18)
        
        if self.dialogue_box_list[1].active:
            arcade.draw_text('Options', self.half_width-50, self.half_height+170, arcade.color.BLACK, 22)
            arcade.draw_rectangle_outline(
                self.name_field_rect[0], self.name_field_rect[1], self.name_field_rect[2], self.name_field_rect[3],
                self.name_field_color
            )
            arcade.draw_rectangle_outline(
                self.password_field_rect[0], self.password_field_rect[1], self.password_field_rect[2], self.password_field_rect[3],
                self.password_field_color
            )
            if self.room_name:
                arcade.draw_text(self.room_name, self.half_width-160, self.half_height-12, arcade.color.BLACK, 18)
            if self.room_password:
                arcade.draw_text(self.room_password, self.half_width-160, self.half_height-62, arcade.color.BLACK, 18)

        if True not in map(lambda dialog: dialog.active, self.dialogue_box_list):
            arcade.draw_lrwh_rectangle_textured(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, self.background)
            self.sprite_list.draw()
            for button in self.button_list:
                button.draw()
        
        if self.log:
            arcade.draw_text(self.log, 10, 10, arcade.color.WHITE, 14)

    def on_update(self, delta_time):
        self.name_field_color = arcade.color.WHITE_SMOKE if self.active_room_field == 'name' else arcade.color.BLACK_BEAN
        self.password_field_color = arcade.color.WHITE_SMOKE if self.active_room_field == 'password' else arcade.color.BLACK_BEAN
        if True in map(lambda dialog: dialog.active, self.dialogue_box_list):
            return

    def on_key_release(self, symbol, modifiers):
        if True not in map(lambda dialog: dialog.active, self.dialogue_box_list):
            return
        char = utils.map_key_symbol_to_char(symbol)
        if char == 'del':
            if self.dialogue_box_list[0].active and len(self.server_address) > 0:
                self.server_address = self.server_address[:-1]
            elif self.dialogue_box_list[1].active and len(self.room_name if self.active_room_field == 'name' else self.room_password) > 0:
                if self.active_room_field == 'name':
                    self.room_name = self.room_name[:-1]
                else:
                    self.room_password = self.room_password[:-1]
        elif self.dialogue_box_list[0].active:
            self.server_address += char
        elif self.active_room_field == 'name':
            self.room_name += char
        else:
            self.room_password += char

    def on_mouse_press(self, x, y, button, key_modifiers):
        utils.check_mouse_press_for_buttons(
            x, y,
            self.button_list +
            self.dialogue_box_list[0].button_list +
            self.dialogue_box_list[1].button_list
        )

    def on_mouse_release(self, x, y, button, key_modifiers):
        if self.dialogue_box_list[1].active and utils.check_click_at_rect(x, y, self.name_field_rect):
            self.active_room_field = 'name'
        if self.dialogue_box_list[1].active and utils.check_click_at_rect(x, y, self.password_field_rect):
            self.active_room_field = 'password'
        utils.check_mouse_release_for_buttons(
            x, y,
            self.button_list +
            self.dialogue_box_list[0].button_list +
            self.dialogue_box_list[1].button_list
        )

    def set_connection(self, is_connected):
        self.connected = is_connected
        texture = 'flagGreen1.png' if is_connected else 'flagRed1.png'
        self.sprite_list[1].texture = arcade.load_texture(':resources:images/items/' + texture)

    def set_room_to_create_mode(self):
        self.room_mode = 'Create'
        self.dialogue_box_list[1].button_list[0].text = 'Create'
    
    def set_room_to_join_mode(self):
        self.room_mode = 'Join'
        self.dialogue_box_list[1].button_list[0].text = 'Join'

    def create_connection(self):
        self.log = ''
        self.dialogue_box_list[1].active = False
        host, port = self.server_address.split(':') if self.server_address and ':' in self.server_address else (self.server_address, 80)
        try:
            self.conn_socket.connect((host, int(port)))
            self.set_connection(True)
        except Exception as m:
            self.set_connection(False)
            self.log = str(m)

    def handle_room_action(self):
        if not self.room_name or not self.room_password:
            return
        import getpass
        from game import message
        try:
            username = getpass.getuser()
            data = message.GameMessage().encode({
                "action": self.room_mode.lower(),
                'name': username if username else 'Random',
                'room': self.room_name,
                'password': self.room_password
            }, 'ROOM')
            self.conn_socket.send(data)
            self.in_room_standby = True
            for button in self.button_list:
                button.active = False
        except Exception as m:
            self.log = str(m)

    def conn_will_close(self):
        self.dialogue_box_list[1].active = False



def main():
    """ Main method """
    game = BizingoGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
