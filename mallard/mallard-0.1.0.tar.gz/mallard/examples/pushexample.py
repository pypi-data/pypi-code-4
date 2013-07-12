import time

from mallard import Mallard

if __name__ == "__main__":
    api_key = "<insert your key here>"

    # list of widgets to register
    # {name: widget_id}
    widgets = {
       "counter_1": 123456,
       "counter_2": 123457,
       }
    mallard = Mallard(api_key, widgets)
    
    # push a new value by name
    mallard.push(name="counter_1", value=100)

    # push a new value by id
    mallard.push(widget_id=123456, value=50, timestamp=time.time())
