import arcade
import random
import os
import utils, components

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Bizingo"

class BizingoGame(arcade.Window):
    """
    Main application class.

    NOTE: Go ahead and delete the methods you don't need.
    If you do need a method, delete the 'pass' and replace it
    with your own code. Don't leave 'pass' in this program.
    """

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        # Set the working directory (where we expect to find files) to the same
        # directory this .py file is in. You can leave this out of your own
        # code, but it is needed to easily run the examples using "python -m"
        # as mentioned at the top of this program.
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        arcade.set_background_color(arcade.color.AMAZON)

        self.pause = False
        # self.coin_list = None
        self.button_list = None

    def setup(self):
        # Create your sprites and sprite lists here
        # self.coin_list = arcade.SpriteList()
        # for i in range(10):
        #     coin = arcade.Sprite(":resources:images/items/coinGold.png", 0.25)
        #     coin.center_x = random.randrange(SCREEN_WIDTH)
        #     coin.center_y = random.randrange(SCREEN_HEIGHT)
        #     coin.change_y = -1
        #     self.coin_list.append(coin)

        # Create our on-screen GUI buttons
        self.button_list = []

        play_button = components.DefaultTextButton(60, 570, 'Connect',self.resume_program)
        self.button_list.append(play_button)

        quit_button = components.DefaultTextButton(60, 515, 'Quit', self.pause_program)
        self.button_list.append(quit_button)

    def on_draw(self):
        """
        Render the screen.
        """

        arcade.start_render()

        # Draw the coins
        # self.coin_list.draw()

        # Draw the buttons
        for button in self.button_list:
            button.draw()

    def on_update(self, delta_time):
        """
        All the logic to move, and the game logic goes here.
        Normally, you'll call update() on the sprite lists that
        need it.
        """

        if self.pause:
            return

        # self.coin_list.update()

        # for coin in self.coin_list:
        #     if coin.top < 0:
        #         coin.bottom = SCREEN_HEIGHT

    def on_mouse_press(self, x, y, button, key_modifiers):
        """
        Called when the user presses a mouse button.
        """
        utils.check_mouse_press_for_buttons(x, y, self.button_list)

    def on_mouse_release(self, x, y, button, key_modifiers):
        """
        Called when a user releases a mouse button.
        """
        utils.check_mouse_release_for_buttons(x, y, self.button_list)

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
