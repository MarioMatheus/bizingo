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

        self.pause = False
        # self.coin_list = None
        self.button_list = None

        self.half_width = self.width/2
        self.half_height = self.height/2
        self.theme = None

    def setup(self):
        self.button_list = []

        play_button = components.DefaultTextButton(60, 570, 'Connect',self.resume_program)
        self.button_list.append(play_button)

        quit_button = components.DefaultTextButton(60, 515, 'Quit', self.pause_program)
        self.button_list.append(quit_button)

        arcade.set_background_color(arcade.color.ALICE_BLUE)
        self.set_theme()
        self.add_dialogue_box()
        # self.add_text()
        self.add_button()

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

    def on_draw(self):
        arcade.start_render()
        super().on_draw()

        for button in self.button_list:
            button.draw()

        for text in self.dialogue_box_list[0].text_list:
            text.draw()

    def on_update(self, delta_time):
        if self.pause:
            return
        
        if self.dialogue_box_list[0].active:
            return

    def add_dialogue_box(self):
        color = (220, 228, 255)
        dialoguebox = arcade.gui.DialogueBox(self.half_width, self.half_height, self.half_width*1.1,
                                             self.half_height*1.5, color, self.theme)
        close_button = components.CloseDialogButton(dialoguebox, self.half_width, self.half_height-(self.half_height/2) + 40,
                                   theme=self.theme)
        dialoguebox.button_list.append(close_button)
        message = "Hello I am a Dialogue Box."
        dialoguebox.text_list.append(arcade.gui.TextBox(message, self.half_width, self.half_height/2, self.theme.font_color))
        self.dialogue_box_list.append(dialoguebox)

    def add_button(self):
        show_button = components.ShowDialogButton(self.dialogue_box_list[0], self.width-100, self.half_height, theme=self.theme)
        self.button_list.append(show_button)

    def on_mouse_press(self, x, y, button, key_modifiers):
        utils.check_mouse_press_for_buttons(x, y, self.button_list + self.dialogue_box_list[0].button_list)

    def on_mouse_release(self, x, y, button, key_modifiers):
        utils.check_mouse_release_for_buttons(x, y, self.button_list + self.dialogue_box_list[0].button_list)

    def pause_program(self):
        self.pause = True

    def resume_program(self):
        self.pause = False

def main():
    """ Main method """
    game = BizingoGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
