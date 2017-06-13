from kivy.app import App
from kivy.graphics import BorderImage
from kivy.uix.widget import Widget
from kivy.graphics import Color, BorderImage
from kivy.utils import get_color_from_hex
from kivy.properties import ListProperty, NumericProperty
from kivy.core.window import Keyboard
from kivy.core.window import Window
from kivy.vector import Vector
from kivy.animation import Animation
import random
spacing = 12

colors = (
    'EEE4DA', 'EDE0C8', 'F2B179', 'F59563',
    'F67C5F', 'F65E3B', 'EDCF72', 'EDCC61',
    'EDC850', 'EDC53F', 'EDC22E')
tile_colors = {2 ** i: color for i, color in
               enumerate(colors, start=1)}
key_vectors = {
    Keyboard.keycodes['up']: (0, 1),
    Keyboard.keycodes['right']: (1, 0),
    Keyboard.keycodes['down']: (0, -1),
    Keyboard.keycodes['left']: (-1, 0),
}

def all_cells(flip_x=False, flip_y=False):
    for x in (reversed(range(4)) if flip_x else range(4)):
        for y in (reversed(range(4)) if flip_y else range(4)):
            yield (x, y)

class Board(Widget):
    b = None
    moving = False
    score = NumericProperty(0)
    def __init__(self, **kwargs):
        super(Board, self).__init__(**kwargs)
        self.b = [[None for i in range(4)] for j in range(4)]
        self.resize()
        
    def reset(self):
        self.b = [[None for i in range(4)] for j in range(4)]
        self.new_tile()
        self.new_tile()
        self.moving = False
	self.score = 0
    def resize(self, *args):
        self.cell_size = (0.25 * (self.width - 5 * spacing), ) * 2
        self.canvas.before.clear()
        with self.canvas.before:
            BorderImage(pos=self.pos, size=self.size,source='/image/round.png')
            Color(*get_color_from_hex('CCC0B4'))
            for board_x, board_y in all_cells():
                BorderImage(pos=self.cell_pos(board_x, board_y),
                            size=self.cell_size,source='/image/round.png') 
        for board_x, board_y in all_cells():
            tile = self.b[board_x][board_y]
            if tile:
                tile.resize(pos=self.cell_pos(board_x, board_y),
                            size=self.cell_size)
    def cell_pos(self, board_x, board_y):
        return (self.x + board_x *
                (self.cell_size[0] + spacing) + spacing,
                self.y + board_y *
                (self.cell_size[1] + spacing) + spacing)
    on_pos = resize
    on_size = resize
    def valid_cell(self, board_x, board_y):
        return (board_x >= 0 and board_y >= 0 and
                board_x <= 3 and board_y <= 3)
    def can_move(self, board_x, board_y):
        return (self.valid_cell(board_x, board_y) and
                self.b[board_x][board_y] is None)
    def can_combine(self, board_x, board_y, number):
        return (self.valid_cell(board_x, board_y) and
                self.b[board_x][board_y] is not None and
                self.b[board_x][board_y].number == number)

    def is_deadlocked(self):
        for x, y in all_cells():
            if self.b[x][y] is None:
                return False # Step 1
            
            number = self.b[x][y].number
            if self.can_combine(x + 1, y, number) or self.can_combine(x, y + 1, number):
                return False # Step 2
        return True # Step 3
    def new_tile(self, *args):
        empty_cells = [(x, y) for x, y in all_cells() # Step 1
                       if self.b[x][y] is None]
        x, y = random.choice(empty_cells) # Step 2
        tile = Tile(pos=self.cell_pos(x, y), # Step 3
                    size=self.cell_size)
        self.b[x][y] = tile # Step 4
	
        self.add_widget(tile)
        if len(empty_cells) == 1 and self.is_deadlocked():
            	print('Game over (board is deadlocked)')
		self.end()
	self.moving = False
        
    
    def on_key_down(self, window, key, *args):
        
        if key in key_vectors:
            self.move(*key_vectors[key])

    def on_touch_up(self, touch):
        v = Vector(touch.pos) - Vector(touch.opos)
        if v.length() < 20:
            return
        
        if abs(v.x) > abs(v.y):
            v.y = 0
        else:
            v.x = 0
            
        self.move(*v.normalize())
    def move(self, dir_x, dir_y):
        if self.moving:
            return

        dir_x = int(dir_x)
        dir_y = int(dir_y)
        for board_x, board_y in all_cells(dir_x > 0, dir_y > 0):
            tile = self.b[board_x][board_y]
            if not tile:
                continue
                
            x, y = board_x, board_y
            while self.can_move(x + dir_x, y + dir_y):
                self.b[x][y] = None
                x += dir_x
                y += dir_y
                self.b[x][y] = tile
            if self.can_combine(x + dir_x, y + dir_y, tile.number):
		 
                self.b[x][y] = None
                x += dir_x
                y += dir_y
                self.remove_widget(self.b[x][y])
                self.b[x][y] = tile
                tile.number *= 2
		self.score += tile.number
                if (tile.number == 2048):
                    print('You win the game')
                tile.update_colors()
                                
            if x == board_x and y == board_y:
                continue # nothing has happened
            anim = Animation(pos=self.cell_pos(x, y),
                             duration=0.1, transition='linear')
            if not self.moving:
                anim.on_complete = self.new_tile
                self.moving = True
            anim.start(tile)
    def end(self):
		end = self.parent.ids.end.__self__
		self.remove_widget(end)
		self.add_widget(end)
		text = 'Game\nover!'
		for x, y in all_cells():
		    if self.b[x][y].number == 2048 or self.b[x][y].number>2048:
			text = 'WIN !'
		self.parent.ids.end_label.text = text
		Animation(opacity=1., d=.5).start(end)
    def restart(self):
		self.rebuild_backgroud()
		self.reset()
		
		#self.reposition()
		#Clock.schedule_once(self.spawn_number, .1)
		#Clock.schedule_once(self.spawn_number, .1)
		self.parent.ids.end.opacity = 0
    def rebuild_backgroud(self):
	self.canvas.clear()
	with self.canvas:
            Color(0xbb / 255., 0xad / 255., 0xa0 / 255.,)
            BorderImage(pos=self.pos, size=self.size, source='image/round.png')
	    Color(0xcc / 255., 0xc0 / 255., 0xb3 / 255.)
	    self.cell_size = (0.25 * (self.width - 5 * spacing), ) * 2
            for board_x, board_y in all_cells():
                BorderImage(pos=self.cell_pos(board_x, board_y),
                            size=self.cell_size,source='/image/round.png') 
            
class Tile(Widget):
    font_size = NumericProperty(24)
    number = NumericProperty(2) # Text shown on the tile
    color = ListProperty(get_color_from_hex(tile_colors[2]))
    number_color = ListProperty(get_color_from_hex('776E65'))
    def __init__(self, number=2, **kwargs):
        super(Tile, self).__init__(**kwargs)
        self.font_size = 0.5 * self.width
        self.number = number
        self.update_colors()
        
        
    def update_colors(self):
        self.color = get_color_from_hex(tile_colors[self.number])
        if self.number > 4:
            self.number_color = get_color_from_hex('F9F6F2')
            
    def resize(self, pos, size):
        self.pos = pos
        self.size = size
        self.font_size = 0.5 * self.width

class gameApp(App):
		
    def on_start(self):
        board = self.root.ids.board
        board.reset()
        Window.bind(on_key_down=board.on_key_down)
    def new_tile(self, *args):
        empty_cells = [(x, y) for x, y in all_cells() # Step 1
                       if self.b[x][y] is None]
        x, y = random.choice(empty_cells) # Step 2
        tile = Tile(pos=self.cell_pos(x, y), # Step 3
                    size=self.cell_size)
        self.b[x][y] = tile # Step 4
        self.add_widget(tile)

    def reset(self):
        self.b = [[None for i in range(4)]
                  for j in range(4)] # same as before
        self.new_tile()
        self.new_tile() # put down 2 tiles   
    def on_pause(self):
		return True 
    def on_resume(self):
		pass
if __name__=='__main__':
    gameApp().run()
