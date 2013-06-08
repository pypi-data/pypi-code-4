#! /usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import timedelta

class DiffGetter(object):
    ALG_START=0
    START='start'
    END='end'
    RESUME='resume'

    states = {
        # CURSTATE: NEXT_STATES, NEW_DIFFSUM_FN(cur diff sum, prev item, cur item)
        ALG_START: ([END], lambda _, _1, _2: timedelta(0)),
        END: ([START, RESUME], lambda s, p, i: s + (p.created_at - i.created_at)),
        RESUME: ([END], lambda s, _, _1: s),
    }

    # FIXME: for this use-case if the first record isnt END state, create it from now()

    state = (ALG_START, None, None)
    items = []

    def got(self, item):
        if item.activity not in self.states[self.state[0]][0]:
            raise RuntimeError("invalid state")

        self.state = (item.activity, item, self.states[self.state[0]][1](self.state[2], self.state[1], item))
        #log.debug("new state: (%s, %s, %s)" % state)
        self.items.insert(0, item)

    def continue_(self):
        if self.items == []:
            return True

        return not self.items[0].activity == 'start'

    def result(self):
        return self.items, self.state


class StartGetter(object):
    def __init__(self, *args, **kw):
        super(StartGetter, self).__init__(*args, **kw)
        self._item = None

    def continue_(self):
        return not self._item

    def got(self, item):
        if item.activity == 'start':
            self._item = item

    def result(self):
        return self._item
