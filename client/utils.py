def check_click_at_rect(x, y, rect):
    if x > rect[0] + rect[2] / 2:
        return False
    if x < rect[0] - rect[2] / 2:
        return False
    if y > rect[1] + rect[3] / 2:
        return False
    if y < rect[1] - rect[3] / 2:
        return False
    return True

def check_mouse_press_for_buttons(x, y, button_list):
    """ Given an x, y, see if we need to register any button clicks. """
    for button in button_list:
        if x > button.center_x + button.width / 2:
            continue
        if x < button.center_x - button.width / 2:
            continue
        if y > button.center_y + button.height / 2:
            continue
        if y < button.center_y - button.height / 2:
            continue
        button.on_press()


def check_mouse_release_for_buttons(_x, _y, button_list):
    """ If a mouse button has been released, see if we need to process
        any release events. """
    for button in button_list:
        if button.pressed:
            button.on_release()

def map_key_symbol_to_char(symbol):
    if symbol == 65288:
        return 'del'
    if symbol not in range(97, 123) and symbol not in range(48, 59) and symbol not in [32, 44, 45, 46, 47, 63, 95]:
        return ''
    return chr(symbol)