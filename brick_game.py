import tkinter as tk
import random
import math
import copy
class Game(tk.Canvas):
    textDisplayed = False
    lines = 20
    sec = 0
    barHeight = 20
    barSpeed = 10
    ballSpeed = 7
    bricks = []
    brickWidth = 50
    brickHeight = 20
    brickByLine = 16
    brickColors = {
        "r": "#e74c3c",
        "g": "#2ecc71",
        "b": "#3498db",
        "t": "#1abc9c",
        "p": "#9b59b6",
        "y": "#f1c40f",
        "o": "#e67e22",
    }
    scrHeight = 500
    scrWidth = brickWidth*brickByLine

    def init(self, root):
        tk.Canvas.init(self, root, bg="#ffffff", bd=0, highlightthickness=0, relief="ridge", width=self.scrWidth, height=self.scrHeight)
        self.pack()
        self.timeContainer = self.create_text(self.scrWidth/2, self.scrHeight*4/5, text="00:00:00", fill="#cccccc", font=("Arial", 30), justify="center")
        self.shield = self.create_rectangle(0, 0, 0, 0, width=0)
        self.bar = self.create_rectangle(0, 0, 0, 0, fill="#7f8c8d", width=0)
        self.ball = self.create_oval(0, 0, 0, 0, width=0)
        self.ballNext = self.create_oval(0, 0, 0, 0, width=0, state="hidden")
        self.level(1)
        self.nextFrame()

    def reset(self):
        self.barWidth = 100
        self.ballRadius = 7
        self.coords(self.shield, (0, self.scrHeight-5, self.scrWidth, self.scrHeight))
        self.itemconfig(self.shield, fill=self.brickColors["b"], state="hidden")
        self.coords(self.bar, ((self.scrWidth - self.barWidth)/2, self.scrHeight - self.barHeight, (self.scrWidth + self.barWidth)/2, self.scrHeight))
        self.coords(self.ball, (self.scrWidth/2 - self.ballRadius, self.scrHeight - self.barHeight - 2*self.ballRadius, self.scrWidth/2 + self.ballRadius, self.scrHeight - self.barHeight))
        self.itemconfig(self.ball, fill="#2c3e50")
        self.coords(self.ballNext, tk._flatten(self.coords(self.ball)))
        self.effects = {
            "ballFire": [0, 0],
            "barTall": [0, 0],
            "ballTall": [0, 0],
            "shield": [0, -1],
        }
        self.effectsPrev = copy.deepcopy(self.effects)
        self.ballThrown = False
        self.keyPressed = [False, False]
        self.losed = False
        self.won = False
        self.ballAngle = math.radians(90)
        for brick in self.bricks:
            self.delete(brick)
            del brick

    def level(self, level):
        self.reset()
        self.levelNum = level
        self.bricks = []
        try:
            file = open(str(level)+".txt")
            content = list(file.read().replace("\n", ""))[:(self.brickByLine*self.lines)]
            file.close()
            for i, el in enumerate(content):
                col = i%self.brickByLine
                line = i//self.brickByLine
                if el != ".":
                    self.brick.append(self.create_rectangle(col*self.brickWidth, line*self.brickHeight, (col+1)*self.brickWidth, (line+1)*self.brickHeight, fill=self.brickColors[el], width=2, outline="#ffffff"))
        
        except IOError:
            self.displayText("GAME ENDED IN\n" + "%02d mn %02d sec %02d" % (int(self.sec)//60, int(self.sec)%60, (self.sec*100)%100), hide = False)
            return
        self.displayText("LEVEL\n"+str(self.levelNum))
        
    def nextFrame(self):
        if self.ballThrown and not(self.textDisplayed):
            self.moveBall()

        if not(self.textDisplayed):
            self.updateTime()
            
        self.updateEffects()

        if self.keyPressed[0]:
            self.moveBar(-game.barSpeed)
        elif self.keyPressed[1]:
            self.moveBar(game.barSpeed)

        if not(self.textDisplayed):
            if self.won:
                self.displayText("WON!", callback = lambda: self.level(self.levelNum+1))
            elif self.losed:
                self.displayText("LOST!", callback = lambda: self.level(self.levelNum))
        
        self.after(int(1000/60), self.nextFrame)

    def moveBar(self, x):
        barCoords = self.coords(self.bar)
        if barCoords[0] < 10 and x < 0:
            x = -barCoords[0]
        elif barCoords[2] > self.scrWidth - 10 and x > 0:
            x = self.scrWidth - barCoords[2]
        
        self.move(self.bar, x, 0)
        if not(self.ballThrown):
            self.move(self.ball, x, 0)

    def moveBall(self):
        self.move(self.ballNext, self.ballSpeed*math.cos(self.ballAngle), -self.ballSpeed*math.sin(self.ballAngle))
        ballNextCoords = self.coords(self.ballNext)
        i = 0
        while i < len(self.bricks):
            collision = self.collision(self.ball, self.bricks[i])
            collisionNext = self.collision(self.ballNext, self.bricks[i])
            if not collisionNext:
                brickColor = self.itemcget(self.bricks[i], "fill")
                if brickColor == self.brickColors["g"]:
                    self.effects["barTall"][0] = 1
                    self.effects["barTall"][1] = 240
                elif brickColor == self.brickColors["b"]:
                    self.effects["shield"][0] = 1
                elif brickColor == self.brickColors["p"]:
                    self.effects["ballFire"][0] += 1
                    self.effects["ballFire"][1] = 240
                elif brickColor == self.brickColors["t"]:
                    self.effects["ballTall"][0] = 1
                    self.effects["ballTall"][1] = 240

                if not(self.effects["ballFire"][0]):
                    if collision == 1 or collision == 3:
                        self.ballAngle = math.radians(180) - self.ballAngle
                    if collision == 2 or collision == 4:
                        self.ballAngle = -self.ballAngle
                if brickColor == self.brickColors["r"]:
                    self.itemconfig(self.bricks[i], fill=self.brickColors["o"])
                elif brickColor == self.brickColors["o"]:
                    self.itemconfig(self.bricks[i], fill=self.brickColors["y"])
                else:
                    self.delete(self.bricks[i])
                    del self.bricks[i]
            i += 1

        self.won = len(self.bricks) == 0
        if ballNextCoords[0] < 0 or ballNextCoords[2] > self.scrWidth:
            self.ballAngle = math.radians(180) - self.ballAngle
        elif ballNextCoords[1] < 0:
            self.ballAngle = -self.ballAngle
        elif not(self.collision(self.ballNext, self.bar)):
            ballCenter = self.coords(self.ball)[0] + self.ballRadius
            barCenter = self.coords(self.bar)[0] + self.barWidth/2
            angleX = ballCenter - barCenter
            angleOrigin = (-self.ballAngle) % (3.14159*2)
            angleComputed = math.radians(-70/(self.barWidth/2)*angleX + 90)
            self.ballAngle = (1 - (abs(angleX)/(self.barWidth/2))*0.25)*angleOrigin + ((abs(angleX)/(self.barWidth/2))*0.25)*angleComputed
        elif not(self.collision(self.ballNext, self.shield)):
            if self.effects["shield"][0]:
                self.ballAngle = -self.ballAngle
                self.effects["shield"][0] = 0
            else :
                self.losed = True

        self.move(self.ball, self.ballSpeed*math.cos(self.ballAngle), -self.ballSpeed*math.sin(self.ballAngle))
        self.coords(self.ballNext, tk._flatten(self.coords(self.ball)))

    def updateEffects(self):
        for key in self.effects.keys():
            if self.effects[key][1] > 0:
                self.effects[key][1] -= 1
            if self.effects[key][1] == 0:
                self.effects[key][0] = 0
        if self.effects["ballFire"][0]:
            self.itemconfig(self.ball, fill=self.brickColors["p"])
        else:
            self.itemconfig(self.ball, fill="#2c3e50")
        if self.effects["barTall"][0] != self.effectsPrev["barTall"][0]:
            diff = self.effects["barTall"][0] - self.effectsPrev["barTall"][0]
            self.barWidth += diff*60
            coords = self.coords(self.bar)
            self.coords(self.bar, tk._flatten((coords[0]-diff*30, coords[1], coords[2]+diff*30, coords[3])))
        if self.effects["ballTall"][0] != self.effectsPrev["ballTall"][0]:
            diff = self.effects["ballTall"][0] - self.effectsPrev["ballTall"][0]
            self.ballRadius += diff*10
            coords = self.coords(self.ball)
            self.coords(self.ball, tk._flatten((coords[0]-diff*10, coords[1]-diff*10, coords[2]+diff*10, coords[3]+diff*10)))

        if self.effects["shield"][0]:
            self.itemconfig(self.shield, fill=self.brickColors["b"], state="normal")
        else:
            self.itemconfig(self.shield, state="hidden")

        self.effectsPrev = copy.deepcopy(self.effects)
    def updateTime(self):
        self.sec += 1/60
        self.itemconfig(self.timeContainer, text="%02d:%02d:%02d" % (int(self.sec)//60, int(self.sec)%60, (self.sec*100)%100))

    def displayText(self, text, hide = True, callback = None):
        self.textDisplayed = True
        self.textContainer = self.create_rectangle(0, 0, self.scrWidth, self.scrHeight, fill="#ffffff", width=0, stipple="gray50")
        self.text = self.create_text(self.scrWidth/2, self.scrHeight/2, text=text, font=("Arial", 25), justify="center")
        if hide:
            self.after(3000, self.hideText)
        if callback != None:
            self.after(3000, callback)

    def hideText(self):
        self.textDisplayed = False
        self.delete(self.textContainer)
        self.delete(self.text)

    def collision(self, el1, el2):
        collisionCounter = 0

        objectCoords = self.coords(el1)
        obstacleCoords = self.coords(el2)
        
        if objectCoords[2] < obstacleCoords[0] + 5:
            collisionCounter = 1
        if objectCoords[3] < obstacleCoords[1] + 5:
            collisionCounter = 2
        if objectCoords[0] > obstacleCoords[2] - 5:
            collisionCounter = 3
        if objectCoords[1] > obstacleCoords[3] - 5:
            collisionCounter = 4
                
        return collisionCounter

def eventsPress(event):
    global game, hasEvent

    if event.keysym == "Left":
        game.keyPressed[0] = 1
    elif event.keysym == "Right":
        game.keyPressed[1] = 1
    elif event.keysym == "space" and not(game.textDisplayed):
        game.ballThrown = True

def eventsRelease(event):
    global game, hasEvent
    
    if event.keysym == "Left":
        game.keyPressed[0] = 0
    elif event.keysym == "Right":
        game.keyPressed[1] = 0

root = tk.Tk()
root.title("Brick Breaker")
root.resizable(0,0)
root.bind("<Key>", eventsPress)
root.bind("<KeyRelease>", eventsRelease)

game = Game(root)
root.mainloop()