import time
import cv2
import numpy as np
import vizdoom as vzd
from vizdoom import Button, Mode, ScreenFormat, ScreenResolution
from ultralytics import YOLO

MODEL_PATH = "runs/detect/train/weights/best.pt"

model = YOLO(MODEL_PATH)

game = vzd.DoomGame()

game.set_window_visible(1)
game.set_doom_map("map02")
game.set_mode(Mode.PLAYER)
game.set_config({
    'screen_resolution' : ScreenResolution.RES_640X480
})
game.set_screen_format(ScreenFormat.BGR24)
game.set_render_hud(1)
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

lastBoxes = []
frameIdx = 0

maxArea = 0
maxAreaIdx = 0

def getBoxesData(boxes : list, lastBoxes : list) -> None:

    for box in boxes:
        xyxy = box.xyxy[0].cpu().numpy().astype(int)
        conf = float(box.conf[0].cpu().numpy())
        clsId = int(box.cls[0].cpu().numpy())
        clsName = model.names[clsId]
        lastBoxes.append((xyxy[0], xyxy[1], xyxy[2], xyxy[3], conf, clsName))

def drawBoxes(lastBoxes : list) -> None:
    for x1, y1, x2, y2, conf, cls_name in lastBoxes:
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(
            frame,
            f"{cls_name} {conf:.2f}",
            (x1, max(20, y1 - 8)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 0),
            2            
        )

def getBiggestBoxIndex(lastBoxes : list) -> tuple[int]:
    maxArea = 0
    maxAreaIdx = 0

    for i, (x1, y1, x2, y2, *_) in enumerate(lastBoxes):
        rectangleArea = abs(x1 - x2) * abs(y1 - y2)
        cx = (x1 + x2) // 2
        distanceToCenter = abs(cx - CENTER_SCREEN_X)
        score = rectangleArea / (distanceToCenter + SMOOTHING_FACTOR)

        if maxArea < score:
            maxArea = score
            maxAreaIdx = i

    return maxArea, maxAreaIdx

def getActions(x1, x2):
    cx = (x1 + x2) // 2
    distance_px = cx - CENTER_SCREEN_X

    if abs(distance_px) < 4:
        turn = 0.0
    else:
        turn = distance_px * PX_GRADE * 0.7
    
    attack = 1.0 if abs(distance_px) <= 15 else 0.0

    return turn, attack

while not game.is_episode_finished():

    state = game.get_state()
    if state is None:
        continue

    frame = state.screen_buffer.copy()
    frameIdx += 1

    if frameIdx %  FRAME_SKIP == 0:

        res = model.predict(
            frame,
            conf = 0.75,
            imgsz = 640,
            device = "mps", #Again, I'm using a Apple Silicon Chip, in case you are using a Nvidia GPU comment this
            verbose = False
        )

        lastBoxes.clear()

        if len(res) and res[0].boxes:
            boxes = res[0].boxes
            getBoxesData(boxes, lastBoxes)

        maxArea , maxAreaIdx = getBiggestBoxIndex(lastBoxes)

    drawBoxes(lastBoxes) 
    
    turn = 0.0
    attack = 0.0

    if frameIdx % FRAME_SKIP == 0 and maxArea and len(lastBoxes):
        x1, y1, x2, y2, *_ = lastBoxes[maxAreaIdx]
        turn, attack = getActions(x1, x2)

    cv2.imshow("wiener", frame)

    key = cv2.waitKey(1) & 0xFF
    #PRESS C TO KILL AI
    if key == ord('c'):
        break

    # Uncomment this actions only if you want to try the Aimbot
    # actions = {
    #         Button.MOVE_FORWARD: 1.0 if key == ord('w') else 0.0,
    #         Button.MOVE_BACKWARD: 1.0 if key == ord('s') else 0.0,
    #         Button.MOVE_LEFT: 1.0 if key == ord('a') else 0.0,
    #         Button.MOVE_RIGHT: 1.0 if key == ord('d') else 0.0,
    #         Button.TURN_RIGHT: 1.0 if key == ord('e') else 0.0,
    #         Button.TURN_LEFT: 1.0 if key == ord('q') else 0.0,
    #         Button.TURN_LEFT_RIGHT_DELTA: turn,
    #         Button.ATTACK: attack
    #     }
    # game.make_action([actions.get(b, 0.0) for b in game.get_available_buttons()])

game.close()
cv2.destroyAllWindows()

