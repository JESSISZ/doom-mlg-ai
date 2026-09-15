import vizdoom as vzd
from vizdoom import Button, Mode, ScreenFormat, ScreenResolution
import time
import cv2
import numpy as np
import os

game = vzd.DoomGame()
game.set_doom_map('E1M1')
game.set_window_visible(True)
game.set_config({
    'screen_resolution' : ScreenResolution.RES_1400X1050
})
game.set_screen_format(ScreenFormat.BGR24)
game.set_render_hud(True)
game.set_available_buttons([
    Button.MOVE_FORWARD,
    Button.MOVE_BACKWARD, 
    Button.MOVE_LEFT, 
    Button.MOVE_RIGHT, 
    Button.ATTACK,
    Button.TURN_LEFT,
    Button.TURN_RIGHT,
    Button.USE
    ])
game.set_mode(Mode.SPECTATOR)
game.set_sound_enabled(True)

game.init()

'''
Captures Section:
pwd : doom-mlg-ai/
ls 
/captures
'''

CAPTURES_DIR = "captures"
photo_counter = 0

while not game.is_episode_finished():
    game.advance_action()

    if game.get_last_action()[4] == True:
        
        state = game.get_state()
        frame = state.screen_buffer
        photo_counter += 1

        file_name = os.path.join(CAPTURES_DIR, f"doom_attack_{photo_counter}.jpg")

        cv2.imwrite(file_name, frame)



    time.sleep(.1)

game.close()
