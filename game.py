import vizdoom as vzd
from vizdoom import Button
from vizdoom import Mode
import time

game = vzd.DoomGame()
game.set_doom_map('E1M1')
game.set_window_visible(True)
game.set_config({
    'screen_resolution' : vzd.ScreenResolution.RES_1400X1050
})
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

game.init()

while game.is_running():
    game.advance_action()
    time.sleep(.02)

game.close()
