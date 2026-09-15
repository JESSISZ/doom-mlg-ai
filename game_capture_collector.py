import vizdoom as vzd
from vizdoom import Button, Mode, ScreenFormat, ScreenResolution
import time
import cv2
import numpy as np
import os
import re

game = vzd.DoomGame()
game.set_doom_map("map02")
game.set_window_visible(True)
game.set_config({
    'screen_resolution' : ScreenResolution.RES_1400X1050
})
game.set_screen_format(ScreenFormat.BGR24)
#game.set_render_hud(True) #Comment this for a better capture of the image
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
/captures (maybe)
'''

CAPTURES_DIR = "captures"
os.makedirs(CAPTURES_DIR, exist_ok= True)
# Biggest number in doom atack photos
existing_numbers = [
        int(match.group(1))
        for f in os.listdir(CAPTURES_DIR)
        if (match := re.search(r"doom_attack_(\d+)\.jpg", f))
    ]
photo_counter = max(existing_numbers) if existing_numbers else 0

since_last_shot = 0

while not game.is_episode_finished():
    game.advance_action()
    now = time.time()

    time_window = (now - since_last_shot)
    shot = True if game.get_last_action()[4] == True else False

    #Adjust this parameter for allowing more captures in a smaller time window
    if shot and time_window >= .7:

        state = game.get_state()
        frame = state.screen_buffer
        photo_counter += 1

        file_name = os.path.join(CAPTURES_DIR, f"doom_attack_{photo_counter}.jpg")
        cv2.imwrite(file_name, frame)

        since_last_shot = time.time()


game.close()
