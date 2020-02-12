import arcade
import random
import os
import utils, components

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Bizingo"

class BizingoGame(arcade.Window):

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        self.server_address = ""
        self.connected = False

        self.button_list = None

        self.half_width = self.width/2
        self.half_height = self.height/2
        self.theme = None

    def setup(self):
        self.button_list = []
        self.sprite_list = arcade.SpriteList()

        arcade.set_background_color(arcade.color.ALICE_BLUE)

        self.add_menu_sprites()
        self.set_theme()
        self.add_dialogue_box()
        self.add_button()

    def add_menu_sprites(self):
        flag = arcade.Sprite(':resources:images/items/flagRed1.png')
        flag.center_x = self.width - 266
        flag.center_y = self.half_height * 1.8  
        flag.scale = 0.3
        self.sprite_list.append(flag)

    def set_theme(self):
        self.theme = arcade.gui.Theme()
        self.set_dialogue_box_texture()
        self.set_button_texture()
        self.theme.set_font(24, arcade.color.WHITE)

    def set_dialogue_box_texture(self):
        dialogue_box = ":resources:gui_themes/Fantasy/DialogueBox/DialogueBox.png"
        self.theme.add_dialogue_box_texture(dialogue_box)

    def set_button_texture(self):
        normal = ":resources:gui_themes/Fantasy/Buttons/Normal.png"
        hover = ":resources:gui_themes/Fantasy/Buttons/Hover.png"
        clicked = ":resources:gui_themes/Fantasy/Buttons/Clicked.png"
        locked = ":resources:gui_themes/Fantasy/Buttons/Locked.png"
        self.theme.add_button_textures(normal, hover, clicked, locked)

    def add_dialogue_box(self):
        color = (220, 228, 255)
        dialoguebox = arcade.gui.DialogueBox(self.half_width, self.half_height, self.half_width*1.1,
                                             self.half_height*1.5, color, self.theme)
        conn_button = components.CloseDialogButton(dialoguebox, self.half_width, self.half_height-(self.half_height/2) + 80, width=160, text="Connect", theme=self.theme)
        close_button = components.CloseDialogButton(dialoguebox, self.half_width, self.half_height-(self.half_height/2) + 20, theme=self.theme)
        dialoguebox.button_list.append(conn_button)
        dialoguebox.button_list.append(close_button)
        message = "Type Server Address"
        
        dialoguebox.text_list.append(arcade.gui.TextLabel(message, self.half_width, self.half_height + 60, self.theme.font_color))
        self.dialogue_box_list.append(dialoguebox)

    def add_button(self):
        show_button = components.ShowDialogButton(self.dialogue_box_list[0], self.width-150, self.half_height * 1.8, theme=self.theme)
        self.button_list.append(show_button)

    def on_draw(self):
        arcade.start_render()
        super().on_draw()

        if self.dialogue_box_list[0].active and self.server_address:
            x_offset = len(self.server_address) * 6
            arcade.draw_text(self.server_address, self.half_width-x_offset, self.half_height-20, arcade.color.BLACK, 18)
        
        if not self.dialogue_box_list[0].active:
            self.sprite_list.draw()
            for button in self.button_list:
                button.draw()

    def on_update(self, delta_time):
        if self.dialogue_box_list[0].active:
            return

    def on_key_release(self, symbol, modifiers):
        if not self.dialogue_box_list[0].active:
            return
        char = utils.map_key_symbol_to_char(symbol)
        if char == 'del' and len(self.server_address) > 0:
            self.server_address = self.server_address[:-1]
        else:
            self.server_address += char

    def on_mouse_press(self, x, y, button, key_modifiers):
        utils.check_mouse_press_for_buttons(x, y, self.button_list + self.dialogue_box_list[0].button_list)

    def on_mouse_release(self, x, y, button, key_modifiers):
        utils.check_mouse_release_for_buttons(x, y, self.button_list + self.dialogue_box_list[0].button_list)

    def set_connection(self, is_connected):
        self.connected = is_connected
        texture = 'flagGreen1.png' if is_connected else 'flagRed1.png'
        self.sprite_list[0].texture = arcade.load_texture(':resources:images/items/' + texture)



def main():
    """ Main method """
    game = BizingoGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
