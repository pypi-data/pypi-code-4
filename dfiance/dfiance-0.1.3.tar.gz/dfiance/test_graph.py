# TODO test graphing code for Polymorph, SchemaMapping, PyType

from base import Field
from schema import SchemaObj
from basic import Int, Number, String
from list import List
from dictifiable import DictifiableDictifier
from graph import TypeGraphNode, ValueGraphNode, BoundTypeGraphNode

from vertigo import bottom_up

from textwrap import dedent
import difflib


class Point(SchemaObj):
    field_types = dict(x=Number(), y=Number())
    def __init__(self, x, y):
        super(Point, self).__init__(x=x, y=y)

    def __repr__(self):
        return "Point({}, {})".format(self.x, self.y)


class Snake(SchemaObj):
    field_types = dict(color = String(), segments = List(Point.dfier()))

    def __repr__(self):
        return "{} Snake".format(self.color.title())


class SnakeGame(SchemaObj):
    field_types = dict(
        snakes = List(Snake.dfier()),
        treasures = List(Point.dfier()),
        score = Int()
    )

    def __repr__(self):
        return "Snake Game"


def plot(fn, max=3):
    return [Point(x=fn(x)[0], y=fn(x)[1]) for x in range(0, max)]


@bottom_up
def format(value, path, children, _, indent=1, format=unicode):
    line = format(value)
    if path:
        line = u"{}{}: ".format(' '*indent*len(path), path[-1]) + line
    return '\n'.join([line] + list(children.values()))


def format_dfier(dfier):
    if isinstance(dfier, Field):
        return format_dfier(dfier.dfier)
    if isinstance(dfier, DictifiableDictifier):
        return dfier.cls.__name__
    if isinstance(dfier, type):
        return dfier.__name__
    return type(dfier).__name__


def cmp_texts(actual, expected):
    differ = difflib.Differ()
    actual = dedent(actual).strip()
    expected = dedent(expected).strip()
    if actual != expected:
        print '\n'.join(differ.compare(actual, expected))
        assert False, "Expected match!"


game = SnakeGame(
    snakes = [
        Snake(color='blue', segments=plot(lambda x: (x, 7))),
        Snake(color='red', segments=plot(lambda x: (10-x, x+1))),
        Snake(color='green', segments=plot(lambda x: (0,x+2))),
    ],
    treasures = [Point(1,2), Point(5,5), Point(3.8, 1.9)],
    score = 16,
)


def test_type_graph():
    cmp_texts(format(TypeGraphNode(SnakeGame), format=format_dfier), '''
        SnakeGame
         treasures: List
          elt_type: Point
           y: Number
           x: Number
         score: Int
         snakes: List
          elt_type: Snake
           color: String
           segments: List
            elt_type: Point
             y: Number
             x: Number
    ''')


def test_val_graph():
    cmp_texts(format(ValueGraphNode(game)), '''
        Snake Game
         treasures: [Point(1, 2), Point(5, 5), Point(3.8, 1.9)]
          0: Point(1, 2)
           y: 2
           x: 1
          1: Point(5, 5)
           y: 5
           x: 5
          2: Point(3.8, 1.9)
           y: 1.9
           x: 3.8
         score: 16
         snakes: [Blue Snake, Red Snake, Green Snake]
          0: Blue Snake
           color: blue
           segments: [Point(0, 7), Point(1, 7), Point(2, 7)]
            0: Point(0, 7)
             y: 7
             x: 0
            1: Point(1, 7)
             y: 7
             x: 1
            2: Point(2, 7)
             y: 7
             x: 2
          1: Red Snake
           color: red
           segments: [Point(10, 1), Point(9, 2), Point(8, 3)]
            0: Point(10, 1)
             y: 1
             x: 10
            1: Point(9, 2)
             y: 2
             x: 9
            2: Point(8, 3)
             y: 3
             x: 8
          2: Green Snake
           color: green
           segments: [Point(0, 2), Point(0, 3), Point(0, 4)]
            0: Point(0, 2)
             y: 2
             x: 0
            1: Point(0, 3)
             y: 3
             x: 0
            2: Point(0, 4)
             y: 4
             x: 0
    ''')


def test_bound_graph():
    cmp_texts(format(BoundTypeGraphNode(game), format=format_dfier), '''
        SnakeGame
         treasures: List
          0: Point
           y: Number
           x: Number
          1: Point
           y: Number
           x: Number
          2: Point
           y: Number
           x: Number
         score: Int
         snakes: List
          0: Snake
           color: String
           segments: List
            0: Point
             y: Number
             x: Number
            1: Point
             y: Number
             x: Number
            2: Point
             y: Number
             x: Number
          1: Snake
           color: String
           segments: List
            0: Point
             y: Number
             x: Number
            1: Point
             y: Number
             x: Number
            2: Point
             y: Number
             x: Number
          2: Snake
           color: String
           segments: List
            0: Point
             y: Number
             x: Number
            1: Point
             y: Number
             x: Number
            2: Point
             y: Number
             x: Number
    ''')

if __name__ == '__main__':
    test_type_graph()
    test_val_graph()
    test_bound_graph()
