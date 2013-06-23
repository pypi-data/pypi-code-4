from random import random
from math import pi

from pyagents import Agent, activate, Schedule

class Cell(Agent):
    def __init__(self, col, row):
        self.col = col
        self.row = row
        self.alive = False
        self.neighbours = []

    @activate(level='think')
    def think(self):
        self.neighbour_count = sum([1 for n in self.neighbours if n.alive])

    @activate(level='act')        
    def act(self):
        if self.neighbour_count not in (2, 3):
            self.alive = False
        elif not self.alive and self.neighbour_count == 3:
            self.alive = True
            
    def __repr__(self):
        return [' ', 'X'][self.alive]

    def draw(self, cr, *coefficients):
        if not self.alive:
            return
        cr.set_source_rgb(1, 1, 1)
        radius = 0.5
        cr.arc(
            coefficients[0]*(self.col+0.5), 
            coefficients[1]*(self.row+0.5), 
            radius * min(coefficients), 
            0, 
            2 * pi
        )
        cr.fill()


        
class Grid(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.cells = []
        for col in xrange(height):
            for row in xrange(width):
                self.cells.append(Cell(col, row))
#        self.cells = [Cell() for row in xrange(width * height)]
        for col in xrange(self.width):
            for row in xrange(self.height):
                self.add_neighbours_to(col, row)

    def add_neighbours_to(self, col, row):
        for dcol in [-1, 0, 1]:
            for drow in [-1, 0, 1]:
                if (dcol, drow) != (0, 0):
                    self.cell_at(col, row).neighbours.append(self.cell_at(col + dcol, row + drow))

    def cell_at(self, col, row):
        col %= self.width
        row %= self.height
        return self.cells[row * self.width + col]

    def randomise(self, density):
        for cell in self.cells:
            cell.alive = (random() < density)

    def __repr__(self):
        result = []
        for row in xrange(self.height):
            result.append(' '.join([str(self.cell_at(row, col)) for col in xrange(self.width)]))
        result.append('-'*self.width*2)
        return '\n'.join(result)

        
class Model(object):
    def __init__(self, **kwargs):
        self.schedule = Schedule('think', 'act')
        Cell.activate(self.schedule)
        self.width = kwargs['width']
        self.height = kwargs['height']
        self.grid = Grid(self.width, self.height)
        self.tick = 0
        self.density = 0.5
        self.grid.randomise(self.density)
        
    def __call__(self, density=0.5):
        self.density = density
        self.tick = 0
        self.grid.randomise(self.density)
        while True:
            self.step()
            print self
            if self.tick % 1000 == 0: print "tick: %03i" % self.tick
            
    def step(self):
        self.tick += 1
        self.schedule.execute(self.grid.cells)        

    def __repr__(self):
        return str(self.grid)

def main():
    gol = Model(width=50, height=40)
    gol(density=0.5)
    
if __name__ == "__main__":
    main()
