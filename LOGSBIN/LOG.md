# Hey there coder.

In this specific MD folder I'm going to be posting every step, decision, tools and problems I will face during the realization of this project. This isn't an important markdown file, you can just skip it, I might get kinda corny.

---

### Why did I choose to do this:

Well, during my whole life I've played plenty video games, and I'm always curious about what's happening under every game, but that was a little too simple, I wanted to add a little bit of spice, that's when I remembered some youtube videos where people trained an AI to play video games, and I wanted to do so.

I don't want to sound like a bighead but at first I thought this was going to be piece of cake, which I eventually noticed it was not going to be like that.

#### Which games was I thinking about?

To be honest just a few games pop into my mind, and they were:

- Doom (1993)
- Super Mario Bros (NES)
- Super Monkey Ball

But I finally decided Doom since it was the only game 3D that I knew it had a gymnasium to train my model, if I like this project I will eventually make one using Mario.

***

## Which technologies am I using?

At first I just wanted to use [FreeDoom](https://freedoom.github.io) which uses the original Doom engine to run the game, and then gather information in memory, but [VizDoom](https://vizdoom.farama.org) already hands you all of this data and creates an environment that eases the training of an AI model.

##### OpenCV & Roboflow-YOLO

VizDoom gives you access to the Depth Buffer and Auto Labeling, which is great but I think this is kinda like cheating since is not real Computer Vision, this is why I thought about training a custom YOLO model for data classification.

For the training of the YOLO model you can look over [STEPS.md](./STEPS.md).

