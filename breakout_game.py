import tkinter as tk
"""
This class is inheritted from tkinter.Frame in order to use the mainloop method
in tkinter.Frame. an object of this class holds the status of the game.
"""
class Game(tk.Frame):
    def __init__(self, master):
        super(Game, self).__init__(master)
        self.root = master
        
        #creating the window
        self.lives = 0
        self.width = 610
        self.height = 400
        self.canvas = tk.Canvas(self, bg='#aaaaff', 
                                width = self.width,
                                height = self.height)
        
        #This geometry manager organizes widgets in blocks before placing them in the parent widget.
        self.canvas.pack()
        self.pack()

        self.items = {}#each paddle object is maped to a graphical object
        #declaring ball and paddle attributes but leave them empty until they are initializes by init_game_objs() and setup_game()
        self.ball = None
        self.paddle = None

        self.init_game_objs()#initializes the paddle and brick objects and draws them on the screen
        self.hud = None
        self.setup_game()
        self.canvas.focus_set()
        self.canvas.bind('<Left>', lambda _: self.paddle.move(-10))
        self.canvas.bind('<Right>', lambda _: self.paddle.move(10))

    """
    initializes the paddle and brick objects and draws them on the screen
    also fills the self.item dictionary
    """
    def init_game_objs(self):
        if self.ball is not None:
            self.ball.delete()
        if self.paddle is not None:
            self.paddle.delete()
        self.paddle = Paddle(self.canvas, self.width/2, 346)
        self.items[self.paddle.item] = self.paddle
        for x in range(5, self.width - 5, 75):
            self.add_brick(x + 37.5, 50, 2)
            self.add_brick(x + 37.5, 70, 1)
            self.add_brick(x + 37.5, 90, 1)

    """
    Initializes self.ball, adds it to the screan, initializes self.text and updates lives_text
    """
    def setup_game(self):
        self.add_ball()
        self.update_lives_text()
        self.text = self.draw_text(300, 200, 'Press Space to Start')
        self.canvas.bind('<space>', lambda _: self.start_game())#event of keyboard input is used to start the game
        
    """
    initializes a  brick object, draws it on the screen and adds it to item dictionary
    """
    def add_brick(self, x, y, hits):
        brick = Brick(self.canvas, x, y, hits)
        self.items[brick.item] = brick #each brick object is maped to a graphical object

    """
    initializes self.ball with a ball object and draws it on the screan
    """
    def add_ball(self):
        if self.ball is not None:
            self.ball.delete()
        paddle_coords = self.paddle.get_position()
        x = (paddle_coords[0] + paddle_coords[2]) * 0.5 #x coordinate is in the middle of the paddle
        self.ball = Ball(self.canvas, x, 310)
        self.paddle.set_ball(self.ball)

    def draw_text(self, x, y, text, size='40'):
        font = ('Helvetica', size)
        return self.canvas.create_text(x, y, text=text, font=font)
    
    """
    gets executed after the user presses the space bar. 
    """
    def start_game(self):
        self.canvas.unbind('<space>')
        self.canvas.delete(self.text)
        self.paddle.ball = None
        self.game_loop()
    """
    the function in execution when the game has started until the game has ended
    """
    def game_loop(self):
        self.check_collisions()#checking if the ball has hit a brick or a border line
        num_bricks = len(self.canvas.find_withtag('brick'))
        #winning by hittting all the balls
        if num_bricks == 0:
            self.ball.speed = None
            self.text = self.draw_text(300, 200, 'You win!')
            self.after(1000, self.play_again)
        #ball going out
        elif self.ball.get_position()[3] >= self.height:
            self.ball.speed = None
            self.lives -= 1
            if self.lives < 0:
                self.text = self.draw_text(300, 200, 'Game Over')
                self.after(1000, self.play_again)
            else:
                self.after(1000, self.setup_game)
        else:
            self.ball.update()
            self.after(50, self.game_loop)
    
    """
    checks if a ball has hit a brick or a border line and updates the velocity of the ball accordingly
    Also removes the brick that has been hit
    """
    def check_collisions(self):
        ball_coords = self.ball.get_position()
        items = self.canvas.find_overlapping(*ball_coords)
        objects = [self.items[x] for x in items \
               if x in self.items]
        self.ball.collide(objects)

    def update_lives_text(self):
        text = 'Lives: %s' % self.lives
        if self.hud is None:
            self.hud = self.draw_text(50, 20, text, 15)
        else:
            self.canvas.itemconfig(self.hud, text=text)

    def play_again(self):
        self.canvas.delete(self.text)
        self.text = self.draw_text(300,200, 'Play again? (Y or N)')
        self.canvas.bind('<y>', lambda _: self.restart_game())
        self.canvas.bind('<n>', lambda _: self.end_game())#exit game

    def restart_game(self):
        self.lives = 3
        self.canvas.delete(self.text)
        [self.items[x].delete() for x in self.items]
        self.init_game_objs()
        self.setup_game()

    def end_game(self):
        self.canvas.delete(self.text)
        self.text = self.draw_text(300,200, 'Thanks for playing!')
        #self.after(2000, self.root.quit())

"""
objects in the game, for example paddle, ball , brick and be initiallized as GameObject and use its methods
"""
class GameObject(object):
    def __init__(self, canvas, item):
        self.canvas = canvas
        self.item = item

    def get_position(self):
        return self.canvas.coords(self.item)

    def move(self, x, y):
        self.canvas.move(self.item, x, y)

    def delete(self):
        self.canvas.delete(self.item)
        
"""
used for creating ball object and use methods update and collide to take action according to the status of the ball
"""
class Ball(GameObject):
    def __init__(self, canvas, x, y):
        self.radius = 10
        self.direction = [1, -1]#initial direction
        self.speed = 10
        item = canvas.create_oval(x - self.radius, y - self.radius,
                                  x + self.radius, y + self.radius,
                                  fill = 'white')
        super(Ball, self).__init__(canvas, item)
        
    #update the position of the ball
    def update(self):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        if coords[0] <= 0 or coords[2] >= width:#if boundry line has been touched
            self.direction[0] *= -1
        if coords[1] <= 0:
            self.direction[1] *= -1
        x = self.direction[0] * self.speed
        y = self.direction[1] * self.speed
        self.move(x, y)
    """
    executes when the ball has hit eaither a boundary line or a brick
    """
    def collide(self, game_objects):
        coords = self.get_position()
        x = (coords[0] + coords[2]) * 0.5
        
        #if it has hit a boundary line
        if len(game_objects) > 1:
            self.direction[1] *= -1# move in the opposite direction
        elif len(game_objects) == 1:
            game_object = game_objects[0]
            coords = game_object.get_position()
            if x > coords[2]:
                self.direction[0] = 1
            elif x < coords[0]:
                self.direction[0] = -1
            else:
                self.direction[1] *= -1
                
        # if it has hit a brick
        for game_object in game_objects:
            if isinstance(game_object, Brick):
                game_object.hit()

class Paddle(GameObject):
    def __init__(self, canvas, x, y):
        self.width = 80
        self.height = 10
        self.ball = None
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill='blue')
        super(Paddle, self).__init__(canvas, item)

    def set_ball(self, ball):
        self.ball = ball

    def move(self, offset):#offset is the amount the ball has moved
        coords = self.get_position()
        width = self.canvas.winfo_width()
        if coords[0] + offset >= 0 and \ #if the paddle has reached the boundry dont move
            coords[2] + offset <= width:
            super(Paddle, self).move(offset, 0)
            if self.ball is not None:
                self.ball.move(offset, 0)

class Brick(GameObject):
    COLORS = {1: '#999999', 2: '#555555', 3: '#222222'}# the three keys correspond to the three states of the brick

    def __init__(self, canvas, x, y, hits):
        self.width = 75
        self.height = 20
        self.hits = hits
        color = Brick.COLORS[hits]
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill=color, tags='brick')
        super(Brick, self).__init__(canvas, item)
    """
    remove brick from screan if it has been hit
    """
    def hit(self):
        self.hits -= 1
        if self.hits == 0:
            self.delete()
        else:
            self.canvas.itemconfig(self.item, fill = Brick.COLORS[self.hits])
            
#programs entry point starts here
if __name__ == '__main__':
    root = tk.Tk()
    root.title("Hello Pong!")
    game = Game(root)
    game.mainloop()
