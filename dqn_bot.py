import time
import cv2
import numpy as np
import vizdoom as vzd
from vizdoom import Button, Mode, ScreenFormat, ScreenResolution

game = vzd.DoomGame()

game.set_window_visible(1)
game.set_doom_map("map02")
game.set_mode(Mode.SPECTATOR)
game.set_config({
    'screen_resolution' : ScreenResolution.RES_640X480
})
game.set_screen_format(ScreenFormat.BGR24)
game.set_depth_buffer_enabled(1)
game.set_labels_buffer_enabled(1)
game.set_available_buttons([
    Button.MOVE_FORWARD,
    Button.MOVE_BACKWARD, 
    Button.MOVE_LEFT, 
    Button.MOVE_RIGHT, 
    Button.ATTACK,
    Button.TURN_LEFT,
    Button.TURN_RIGHT,
    Button.USE,
    Button.TURN_LEFT_RIGHT_DELTA,
    ])

game.init()

FRAME_SKIP = 2
SCREEN_W = 640
SCREEN_L = 480
CENTER_SCREEN_X = SCREEN_W // 2
PX_GRADE= 90/640
SMOOTHING_FACTOR = 60
NUM_BEAMS = 5 
HORIZON_Y = SCREEN_L // 2

#In this case, I'm going to leave a 10px margin between the two borders

BEAMS_X = np.linspace(10, 630, NUM_BEAMS, dtype=int)

def getBeams(depthBuffer):
    return np.array(depthBuffer[HORIZON_Y, BEAMS_X], np.int16) / 255.0 


while not game.is_episode_finished():
    game.advance_action()
    state = game.get_state()
    if state is None:
        continue

    frame = state.screen_buffer.copy()

    for x, dist in zip(BEAMS_X, getBeams(state.depth_buffer)):
        cv2.circle(frame, (int(x), HORIZON_Y), 5, (0, 0, 255), -1)
        cv2.putText(frame, f"{dist:.2f}", (int(x) - 12, HORIZON_Y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)

    cv2.imshow("Beams", frame)
    key = cv2.waitKey(1) & 0xFF
    #PRESS C TO KILL AI
    if key == ord('c'):
        break

