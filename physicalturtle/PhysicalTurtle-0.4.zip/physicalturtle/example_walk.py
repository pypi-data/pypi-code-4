# Name:      physicalturtle/example_walk.py
# Purpose:   Examples of two ways to do a random walk
# Copyright: (c) 2012/2013: Mike Sandford
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject
# to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

#-----------------------------------------------------------------------

""" This example program shows two methods for drawing a constrained
    random walk. This is a random walk where the path is not allowed
    to cross itself. If the turtle is not able to move in a certain
    direction then other directions may be tried, but eventually the
    turtle may run into a dead end and the walk will stop.

    The geometry for detecting an intersection with a solid line has
    some particular characteristics that need to be considered in some
    circumstances.

    The three rules of interest are:

    1. A turtle that is coincident with an existing solid line cannot
       move. It is, in effect, always in collision with the line it is
       on and the total movement in any direction is zero.

    2. A turtle that is drawing a solid line (`pen_set_solid`) is not
       tested for line inersection and will happily cross other solid
       lines.

    3. A turtle with pen up is not tested for line inersection and
       will happily cross other solid lines.

    The first is a consequence of the geometry. The second is a
    pragmatic fix. If the second rule did not exist then a turtle
    drawing a solid line would never get beyond a single movement
    because it is always coincident with the line it has just drawn.
    The third rule is a pragmatic necessity to allow a turtle to be
    placed inside a solid boundary.

    This is not a problem in many situations. It generally makes sense
    to draw a solid world and then move ordinary turtles around within
    it. However, for the random walk excercise it seems appropriate to
    have the turtle leave a solid path behind so that the intersection
    detection can be used to prevent the path crossing itself. Rule 2
    says that we cannot detect an intersection if we are drawing a
    solid line, and rule 1 says that we cannot simply switch between
    solid and not solid.

    This example shows two approaches.

    The look-ahead approach assumes that the path is drawn by a turtle
    with pen_set_solid. We use a temporary turtle to probe ahead in
    the chosen direction. This temporary turtle must be not solid
    (rule 2), and cannot start from the end of the main path (rule
    1). To address this we make the temporary turtle start a small
    increment away from the main path, along the chosen direction for
    the next step. In practice, we can take advantage of rule 3 and
    make use of our main turtle instead of creating and deleting a
    temporary one. There's not much difference between these two;
    using the one turtle for both functions shows up the parallels
    between the look-ahead and fill-behind approaches.

    The fill-behind approach uses a not-solid turtle to draw the path,
    and then, once a new path section has been fixed upon, another
    turtle is used to draw a solid line over the previous section.

    The fill-behind approach is reliable, where the look-ahead
    approach is not.  In the look-ahead approach it is possible for
    the turtle to end up very close to a solid line such that the
    initial escape increment is enough to jump over that solid
    line. The walk path can therefore, sometimes, cross itself.
"""
#-----------------------------------------------------------------------
import random
import math
from physicalturtle import Turtle

#-----------------------------------------------------------------------
# Define some usefull limits
MAX_MOVE = 60 # Never more than this move forward
MIN_MOVE = 20  # Never less than this move forward

POSSIBLE_ROTATION = [-135, -90, -45, 45, 90, 135]

#-----------------------------------------------------------------------
# Define a function to test for forward space. This is based on the
# 'touch_front' method.
def available_distance(tk, target_distance, offset_distance=0):
    """ Return the actual distance that can be moved on the current
        heading.

        :tk: A turtle instance, assumed to be drawing a 'solid' line.

        :target_distance: The distance we want to move.

        :offset_distance: Optional offset. The probe is set to start
            from this offset (in the direction of the current heading).
    """
    is_down = tk.isdown()
    if not is_down:
        # Must be pendown to be able to bump into things
        return target_distance
    # Optional step forward
    if offset_distance:
        # Assume we are pen_set_solid - Version 0.2 does not give us
        # any hint!
        tk.pen_unset_solid()
        tk.penup()
        tk.forward(offset_distance)
        tk.pendown()
    tk.forward(target_distance-offset_distance)
    op = tk.last_distance()+offset_distance
    tk.undo() # forward motion
    if offset_distance:
        tk.undo() # initial forward motion and pen up/down
        tk.undo()
        tk.undo()
        tk.pen_set_solid()
    return op

#-----------------------------------------------------------------------
# Look Ahead

def set_of_moves_a(tk, max_count=0):
    """ Generator for a set of valid next moves for the given turtle.

        :tk: A turtle instance, assumed to be drawing a 'solid' line.

    """
    # Choose an orientation. Repeat if no possible move. Do this even
    # on first entry, just in case someone else has been drawing solid
    # lines.
    this_increment = 2 # Hard coded for clarity - must be < MIN_MOVE
    yield_count = 0
    yield_increment = 1 if max_count else 0
    available_moves = range(len(POSSIBLE_ROTATION))
    target_distance = random.randint(MIN_MOVE, MAX_MOVE)
    heading = tk.heading()
    while len(available_moves) and yield_count <= max_count:
        head_index = random.choice(available_moves)
        rotation = POSSIBLE_ROTATION[head_index]
        del available_moves[available_moves.index(head_index)]
        tk.setheading(heading) # Back to starting direction
        tk.left(rotation) # And try this candidate
        offered_distance = available_distance(tk, target_distance,
                                              this_increment)
        if offered_distance >= MIN_MOVE:
            # Found a valid move
            yield_count += yield_increment
            yield tk.heading(), offered_distance
            # Back in after processing - reset choices
            available_moves = range(len(POSSIBLE_ROTATION))
            target_distance = random.randint(MIN_MOVE, MAX_MOVE)
            heading = tk.heading()
    #+--
    raise StopIteration

def run_ahead():
    tk = Turtle()
    tk.pendown()
    tk.pencolor('blue')
    tk.pen_set_solid()

    for heading, length in set_of_moves_a(tk, 100):
        tk.setheading(heading)
        tk.forward(length)
    raw_input()

#-----------------------------------------------------------------------
# Fill behind

def set_of_moves_b(tk, max_count=0):
    """ Generator for a set of valid next moves for the given turtle.

        :tk: A turtle instance, assumed to be drawing a 'solid' line.

    """
    # Choose an orientation. Repeat if no possible move. Do this even
    # on first entry, just in case someone else has been drawing solid
    # lines.
    this_increment = 2 # Hard coded for clarity - must be < MIN_MOVE
    yield_count = 0
    yield_increment = 1 if max_count else 0
    available_moves = range(len(POSSIBLE_ROTATION))
    target_distance = random.randint(MIN_MOVE, MAX_MOVE)
    heading = tk.heading()
    while len(available_moves) and yield_count <= max_count:
        head_index = random.choice(available_moves)
        rotation = POSSIBLE_ROTATION[head_index]
        del available_moves[available_moves.index(head_index)]
        tk.setheading(heading) # Back to starting direction
        tk.left(rotation) # And try this candidate
        offered_distance = available_distance(tk, target_distance)
        if offered_distance >= MIN_MOVE:
            # Found a valid move
            yield_count += yield_increment
            yield tk.heading(), offered_distance
            # Back in after processing - reset choices
            available_moves = range(len(POSSIBLE_ROTATION))
            target_distance = random.randint(MIN_MOVE, MAX_MOVE)
            heading = tk.heading()
    #+--
    raise StopIteration

def run_behind():
    tk = Turtle()
    tk.pendown()
    tk.pencolor('red')

    wall = Turtle()
    wall.pendown()
    wall.pencolor('blue')
    wall.pen_set_solid()

    last_heading = None
    for heading, length in set_of_moves_a(tk, 100):
        this_start = tk.position()
        tk.setheading(heading)
        tk.forward(length)
        if last_heading is not None:
            wall.setheading(last_heading)
            wall.goto(this_start)
        last_heading = heading
    #+--
    wall.setheading(last_heading)
    wall.goto(tk.position())
    raw_input()

if __name__ == '__main__':
    import optparse
    usage = "%prog -a | -b"
    description = ("Produce a constrained random walk using either look"
                    " ahead (-a) or fill behind (-b)")
    parser = optparse.OptionParser(usage=usage, description=description)
    parser.add_option('-a',
                      dest="ahead",
                      action='store_true',
                      help=("Draw the walk in 'solid' lines and use a "
                            "probe turtle look ahead to see if a chosen "
                            "next move is possible."),
        )
    parser.add_option('-b',
                      dest="ahead",
                      action='store_false',
                      help=("Draw the walk invisibly and fill in the "
                            "previous step with a 'solid' line after "
                            "the next step has been chosen."),
        )
    options, args = parser.parse_args()
    if options.ahead is None:
        parser.error("Please choose a drawing method")

    if options.ahead:
        run_ahead()
    else:
        run_behind()

    #-----------------------------------------------------------------------
