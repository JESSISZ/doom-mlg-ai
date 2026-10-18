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


class PerceptionSensors:
    def __init__(self, **kwargs):
        self.screen_w = 640
        self.screen_l = 480
        self.horizon_y = self.screen_l // 2
        self.num_beams = 5
        self.bubble_radius = 600.0
        self.margin = 10
        self.cell_size = 128.0
        self.items_set = {
            "Medikit", "Stimpack", "HealthBonus", "GreenArmor", "BlueArmor", "ArmorBonus",
            "Clip", "Shell", "BoxOfAmmo", "BoxOfShells", "Shotgun", "Chaingun",
            "RedCard", "BlueCard", "YellowCard"
        }

        self.__dict__.update(kwargs)

        self.beams_x = np.linspace(self.margin, self.screen_w - self.margin, self.num_beams, dtype=int)
        self.visited_cells = defaultdict(int)

    def getBeamsDepth(self, depthBuffer: np.ndarray) -> np.ndarray:
        return np.array(depthBuffer[self.horizon_y, self.beams_x], np.int16) / 255.0

    def getAvailableItems(self, items, px: float, py: float) -> list:
        onBubbleItems = []

        for item in items:
            if item.object_name in self.items_set:
                d = np.hypot(item.object_position_x - px, item.object_position_y - py)
                if d <= self.bubble_radius:
                    cx = item.x + item.width // 2
                    cy = item.y + item.height // 2
                    onBubbleItems.append((cx, cy, d, item.object_name))

        return onBubbleItems

    def updateCell(self, cx: int, cy: int):
        self.visited_cells[(int(cx), int(cy))] += 1

    def getFrontCell(self, px: float, py: float, angle: float):
        rad = np.deg2rad(angle)
        
        frontCell = (int((px + np.cos(rad) * self.cell_size) // self.cell_size),
                     int((py + np.sin(rad) * self.cell_size) // self.cell_size))
        
        return frontCell, self.visited_cells.get(frontCell, 0)


sensors = PerceptionSensors()

while not game.is_episode_finished():
    game.advance_action()
    state = game.get_state()

    if state is None:
        continue

    frame = state.screen_buffer.copy()
    px, py, angle = state.game_variables[:3]
    cell_x, cell_y = int(px // sensors.cell_size), int(py // sensors.cell_size)
    sensors.updateCell(cell_x, cell_y)

    items = state.labels
    frontCell, frontVisits = sensors.getFrontCell(px, py, angle)
    currVisits = sensors.visited_cells[(cell_x, cell_y)]

    fog_status = "Not vis" if frontVisits == 0 else f"Vis ({frontVisits})"
    fog_color = (0, 255, 0) if frontVisits == 0 else (0, 165, 255)
    cv2.putText(frame, f"Cell: ({cell_x}, {cell_y}) | Visits: {currVisits}", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)
    cv2.putText(frame, f"Front {frontCell}: {fog_status}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.55, fog_color, 2)
    cv2.putText(frame, f"Discovered Cells: {len(sensors.visited_cells)}", (10, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 0), 2)

    for x, dist in zip(sensors.beams_x, sensors.getBeamsDepth(state.depth_buffer)):
        cv2.circle(frame, (int(x), sensors.horizon_y), 5, (0, 0, 255), -1)
        cv2.putText(frame, f"{dist:.2f}", (int(x) - 12, sensors.horizon_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)

    for cx, cy, d, name in sensors.getAvailableItems(items, px, py):
        cv2.circle(frame, (int(cx), int(cy)), 15, (255, 255, 0), 2)
        cv2.putText(frame, f"{name} {d:.0f}", (int(cx) - 20, int(cy) - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)

    cv2.imshow("Beams", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord('c'):
        break

