from random import random, choice, shuffle
from time import sleep
from collections import defaultdict
from math import pi

from pyagents import Agent, activate, Schedule


class Cell(Agent):
    def __init__(self, grid, col, row, threshold):
        self.grid = grid
        self.col = col
        self.row = row
        self.threshold = threshold        
        self.type = None
        self.empty = True
        self.happy = 0

    def neighbours(self):
        return self.grid.neighbours_at(self.col, self.row)

    @activate(level='move')
    def think(self):
        if self.empty:
            return
        neighbours = self.neighbours()
        neighbour_count = sum([1 for n in neighbours if not n.empty])
        similar_count = sum([1 for n in neighbours if not n.empty and n.type == self.type])
        if neighbour_count:
            similar_proportion = float(similar_count) / float(neighbour_count)
        else:
            similar_proportion = 0.0
        self.happy = similar_proportion >= self.threshold
        if not self.happy:
            self.grid.move_to_empty(self)

    def __repr__(self):
        return [self.type[0], ' '][self.empty]

    def draw(self, cr, x, y, extra=False):
        if self.empty:
            return
        base = self.happy * 0.5
        cr.set_source_rgb(base + 0.5 * (self.type=='R'), base + 0.5 * (self.type=='G'), base + 0.5 * (self.type=='B'))
#        cr.rectangle(x * (self.col+0.5), y * (self.row+0.5), x, y)
        cr.arc(x * (self.col+0.5), y * (self.row+0.5), 0.5 * min([x, y]), 0, 2 * pi)
        cr.fill()

class Grid(object):
    """the grid knows where all the neighbours are"""
    def __init__(self, width, height, minth, maxth):
        self.width = width
        self.height = height
        self.neighbours = defaultdict(list)
        self.cells = []
        self.empties = []
        for row in xrange(self.height):
            for col in xrange(self.width):
                self.cells.append(Cell(self, col, row, minth + (maxth - minth) * random()))
        for row in xrange(self.height):
            for col in xrange(self.width):
                self.add_neighbours_to(col, row)
        shuffle(self.cells)

    def add_neighbours_to(self, col, row):
        for new_row in [row-1, row, row+1]:
            for new_col in [col-1, col, col+1]:
                if (new_col, new_row) == (col, row):
                    continue
                if new_col < 0 or new_row < 0:
                    continue
                if new_col >= self.width or new_row >= self.height:
                    continue
                self.neighbours[(col, row)].append(self.cell_at(new_col, new_row))

    def neighbours_at(self, col, row):
        return self.neighbours[(col, row)]
    
    def cell_at(self, col, row):
        return self.cells[row * self.width + col]

    def randomise(self, density, types):
        self.empties = []
        for cell in self.cells:
            cell.empty = random() > density
            cell.type = choice(types)
            if cell.empty:
                self.empties.append(cell)

    def move_to_empty(self, cell):
        target = choice(self.empties)
        cell.type, target.type = target.type, cell.type
        cell.empty, target.empty = True, False
        self.empties.remove(target)
        self.empties.append(cell)


    def __repr__(self):
        result = []
        result.append('-'*self.width)
        for row in xrange(self.height):
            result.append(''.join([str(self.cell_at(col, row)) for col in xrange(self.width)]))
        result.append('-'*self.width)
        return '\n'.join(result)


class Model(object):
    def __init__(self, **kwargs):
        self.schedule = Schedule('move')
        Cell.activate(self.schedule)
        self.width = kwargs['width']
        self.height = kwargs['height']
        self.types = kwargs['types']
        self.density = kwargs['density']
        self.minth = kwargs['minth']
        self.maxth = kwargs['maxth']
        self.grid = Grid(self.width, self.height, self.minth, self.maxth)
        self.tick = 0
        self.grid.randomise(self.density, self.types)

    def run(self):
        self.tick = 0
        while True:
            self.step()
            print self
            sleep(0.05)
            
    def step(self):
        self.tick += 1
        self.schedule.execute(self.grid.cells)

    def __repr__(self):
        return str(self.grid)

def main():
    th = (random(), random())
    minth, maxth = min(th), max(th)
    model = Model(width=120, height=45, density=0.75, types=['.', '#', 'O'], minth=minth, maxth=maxth)
    model.run()
    
if __name__ == "__main__":
    main()
