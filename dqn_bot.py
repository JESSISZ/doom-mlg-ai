import cv2
import numpy as np
import vizdoom as vzd
from vizdoom import Button, Mode, ScreenFormat, ScreenResolution
from vizdoom import GameVariable
from collections import defaultdict

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
game.set_available_game_variables([
        GameVariable.POSITION_X,
        GameVariable.POSITION_Y,
        GameVariable.ANGLE,
        GameVariable.HEALTH
    ])

game.init()

#Screen
FRAME_SKIP = 2
SCREEN_W = 640
SCREEN_L = 480
CENTER_SCREEN_X = SCREEN_W // 2
PX_GRADE= 90/640
#Beams Viz
NUM_BEAMS = 5 
HORIZON_Y = SCREEN_L // 2
#In this case, I'm going to leave a 10px margin between the two borders
BEAMS_X = np.linspace(10, 630, NUM_BEAMS, dtype=int)
#Bubble
BUBBLE_RADIUS = 600.0
ITEMS_SET = {
    "Medikit", "Stimpack", "HealthBonus", "GreenArmor", "BlueArmor", "ArmorBonus",
    "Clip", "Shell", "BoxOfAmmo", "BoxOfShells", "Shotgun", "Chaingun",
    "RedCard", "BlueCard", "YellowCard"
}
#Map
CELL_SIZE = 128.0
visitedCells = defaultdict(int)

def getBeams(depthBuffer):
    return np.array(depthBuffer[HORIZON_Y, BEAMS_X], np.int16) / 255.0 

def getAvailableItems(items, px, py):
    onBubbleItems = []

    for item in items:
        if item.object_name in ITEMS_SET:
            d = np.hypot(item.object_position_x - px, item.object_position_y - py)

            if d <= BUBBLE_RADIUS:
                cx = item.x + item.width // 2
                cy = item.y + item.height // 2

                onBubbleItems.append((cx,cy,d,item.object_name))

    return onBubbleItems

def updateCell(cx, cy):
    visitedCells[(int(cx), int(cy))] += 1

def getFrontCell(px, py, angle):
    rad = np.deg2rad(angle)
    frontCell = (int((px + np.cos(rad) * CELL_SIZE) // CELL_SIZE),
                 int((py + np.sin(rad) * CELL_SIZE) // CELL_SIZE))
    return frontCell, visitedCells.get(frontCell, 0)

while not game.is_episode_finished():
    game.advance_action()
    state = game.get_state()

    if state is None:
        continue

    frame = state.screen_buffer.copy()
    px, py, angle = state.game_variables[:3]
    cell_x, cell_y = int(px // CELL_SIZE), int(py // CELL_SIZE)
    updateCell(cell_x, cell_y)

    items = state.labels
    frontCell, frontVisits = getFrontCell(px, py, angle)
    currVisits = visitedCells[(cell_x, cell_y)]

    fog_status = "Not vis" if frontVisits == 0 else f"Vis ({frontVisits})"
    fog_color = (0, 255, 0) if frontVisits == 0 else (0, 165, 255)
    cv2.putText(frame, f"Cell: ({cell_x}, {cell_y}) | Visits: {currVisits}", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)
    cv2.putText(frame, f"Front {frontCell}: {fog_status}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.55, fog_color, 2)
    cv2.putText(frame, f"Discovered Cells: {len(visitedCells)}",(10, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 0), 2)

    for x, dist in zip(BEAMS_X, getBeams(state.depth_buffer)):
        cv2.circle(frame, (int(x), HORIZON_Y), 5, (0, 0, 255), -1)
        cv2.putText(frame, f"{dist:.2f}", (int(x) - 12, HORIZON_Y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)

    for cx, cy, d, name in getAvailableItems(items, px, py):
        cv2.circle(frame, (int(cx), int(cy)), 15, (255, 255, 0), 2)
        cv2.putText(frame, f"{name} {d:.0f}", (int(cx) - 20, int(cy) - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)

    cv2.imshow("Beams", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord('c'):
        break

