# Objective & Date

*** 


## Allow the model to see:

#### 14 September 2026

Well, in the morning of this day was when I came up with this idea, I googled over [Gymnasium](https://gymnasium.farama.org) about multiple games and I came up with VizDoom but I first had to get familiarized with this API.

In late night I learned that VizDoom allowed you to access to the Memory Buffer but this project wasn't going to be this easy, I thought about using a light YOLO  model to get the box of enemies and adjust the player sight to the enemy.

To train the model I needed a lot of images, that's why I made a [game capture collector](../game_capture_collector.py), at first I thought about recording a whole gameplay, but since this was going to make the data collection more complex because there could be moments with zero action and zero monsters, I made a statement where every time I attacked I would take a capture of the game, and to avoid taking a lot of captures in a second because the game is running on 35 fps the game would only take the capture if the time since the last capture was more than .7 seconds.

##### Training the YOLO model.

Training the YOLO model was probably one of the most boring things I will do in this project, I took almost 1 hour of labeling monsters, at the end I took ~300 captures which was a lot, at least for me.
