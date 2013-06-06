"""
Piper will help you apply sequential transforms to your data set.

Each pipe in the pipeline is a simple function that takes an item and a context
object. It returns an iterable of the outputs, which get passed to the next
pipe. It's strictly serial, so at each stage of the pipeline the first object
gets fully processed before anything is done with the second.

:copyright: (c) 2013, Anton Backer.
:license: ISC, see LICENSE for more details.
"""

from functools import wraps
from itertools import dropwhile


class Session(dict):
    """Pipeline communication facility.

    Pipes can use it for two things:
       1. As a simple way to share state.
       2. To finalize output items. Finalized items skip the remainder of the
          pipeline and are output as-is.
    """
    def __init__(self):
        self._finalized = False

    def finalize_item(self):
        """Finalize the next output item.

        This moves the item out of flow, letting it skip the remaining pipes in
        the pipeline.

        Good for exactly one item. If your pipe returns more than one output
        per input, it will finalize the first one. If the pipe is a generator,
        you can finalize any number of items by calling this just prior to
        yielding.
        """
        self._finalized = True

    def consume_finalized(self):
        """Reset the flag set by :meth:`finalize_item`"""
        finalized = self._finalized
        self._finalized = False
        return finalized


def flow(iterable, pipes, session=Session()):
    """Flow data through a pipeline of transforms.

    Takes an iterable and a list of functions ("pipes") to pass it through. The
    output of each pipe serves as the input to the next. The final result is
    just another iterable.

    If the pipes are generators, ``flow`` will be entirely lazy.

    Empty values (``None``) are valid in the pipeline. None-pipes are always
    skipped; their only use is as destination markers for the items finalized
    above. Flow for all items, finalized or not, is resumed following the
    none-pipe.
    """
    if not any(pipes):
        for out_item in iterable:
            yield out_item
        return
    for in_item in iterable:
        if session.consume_finalized():
            remaining_pipes = list(dropwhile(lambda p: p is not None, pipes))
            for out_item in flow([in_item], remaining_pipes, session):
                yield out_item
        else:
            remaining_pipes = list(dropwhile(lambda p: p is None, pipes))
            output = remaining_pipes[0](in_item, session)
            for out_item in flow(output, remaining_pipes[1:], session):
                yield out_item


def pipe(fn):
    """Make a conventional 1:1 function pipeline-friendly"""
    @wraps(fn)
    def wrapper(item, session):
        yield fn(item)
    return wrapper


def verbose(pipe):
    """Make a pipe print verbose information to stdout"""
    if not pipe:
        return pipe

    @wraps(pipe)
    def wrapper(in_item, session):
        print("%s:" % pipe.__name__)
        print("\tInput:", in_item)
        counter = 0
        for out_item in pipe(in_item, session):
            print("\tOutput[%i]:" % counter, out_item)
            yield out_item
    return wrapper
