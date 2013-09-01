#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ._compact import tkinter

class FiltersBar(tkinter.Frame):
    """
    XXX
    """
    def __init__(self, parent, **kwargs):
        tkinter.Frame.__init__(self, parent)
        self._initialize(**kwargs)

    def _initialize(self, filters):
        filters = filters + ['<Add new>']
        container1 = tkinter.Frame(self)
        container1.grid(row=1, column=0, sticky='EW')
        for i in range(len(filters + 1)): # Dummy filter for creating new ones
            container1.grid_columnconfigure(i, weight=1)

        def _on_filter_change(*args, **kwargs):
            print(args, kwargs)
        self.filter_strings = [StringVar(f, _on_filter_change)
                               for f in filters]
        entries = [tkinter.Entry(container1, textvariable=filter_string)
                    for filter_string in self.filter_strings]
        for (i, entry) in enumerate(entries):
            entry.focus_force()
            entry.grid(row=0, column=i, sticky='EW')
            entry.bind("<Return>", self.on_press_enter_event)


class Filter(tkinter.Entry):

    def __init__(self, parent, value):
        tkinter.Entry.__init__(self, parent)

        def _on_filter_change(*args, **kwargs):
            print(args, kwargs)
            self.event_generate('<<FilterChange>>')

        self.value = StringVar(value, _on_filter_change)

    @property
    def value(self):
        return self.value.get()



if __name__ == '__main__':
    root = tkinter.Tk()
    frame = tkinter.Frame(root)
    frame.grid(row=0, column=0, sticky='EW')
    root.mainloop()
