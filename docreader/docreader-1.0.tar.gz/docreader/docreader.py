"""
DocReader

A utility for reading a CSV file and mapping it's contents to python objects
based on the field names in the document.

Contains classes for reading loosly structured documents containing rows of 
text (eg. CSV files) and turning them into slightly higher level lists of
dictionaries.

Typical usage is to create a subclass of DocReader and define the cols attribute
once. To use it, instantiate the subclass with an open file-like object (that 
supports the iterator protocol and returns a full line of text on each next()
call).

Iterating over the DocReader subclass instance will then yield a dict where the
keys are as defined in the cols attribute and the values are the cell's logical
values that have passed through the correct conversion function.

The cols attribute is itself is either a list of column names or a dictionary 
mapping keys (which will be used as the keys in the final returned data) to an 
options dictionary for that column.

An options dictionary can have the following keys:
    - column: The name of the column as it appears in the document
    - convert: A callable that will be called with the string associated with
        the data in this cell. Often a type (eg int, float) or a lambda.

>>> import decimal
>>> def _price(val):
...     txt = val.replace('$', '').strip().lower()
...     txt = txt or None
...     return decimal.Decimal(txt)
...
>>> class MyReader(DocReader):
...     cols = dict(
...         a = dict(column='a', convert=int),
...         q = dict(column='b'),
...         c = dict(column='c', convert=lambda x: int(x)),
...         price = dict(convert=_price),
...     )
...
>>> import StringIO
>>> #Ignore the use of chr(10), doctest doesn't like \n.
>>> list(MyReader(StringIO.StringIO("a,b,c,price" + chr(10) + "1,2,3,$45.6" + chr(10) + "4,5,6,$55")))
[{u'a': 1, u'q': u'2', u'c': 3, u'price': Decimal('45.6')}, {u'a': 4, u'q': u'5', u'c': 6, u'price': Decimal('55')}]
>>> list(MyReader(StringIO.StringIO("a,b" + chr(10) + "1,2")))
Traceback (most recent call last):
...
MissingColumnException: Columns missing from input: c, price

"""
import csv

__all__ = ['DocReader', 'MissingColumnException']

class MissingColumnException(ValueError):
    def set_cols(self, cols):
        self.columns = cols
        return self #Allow chaining

class StreamConverter(object):
    """A conversion description that can convert one list of data into a processed dict using the cols attribute.
   
    >>> class MyConverter(StreamConverter):
    ...     cols = ['a', 'b', 'c']
    ... 
    >>> c = MyConverter(iter([[4,5,6],[6,7,8]]))
    >>> c.map_fieldnames(['a','b','c'])
    >>> list(c)
    [{u'a': 4, u'c': 6, u'b': 5}, {u'a': 6, u'c': 8, u'b': 7}]

    >>> class MyConverter(StreamConverter):
    ...     cols = dict(
    ...         a=dict(convert=int),
    ...         q=dict(column='b', convert=int),
    ...         c=dict(convert=lambda z: 'nope'),
    ...     )
    ... 
    >>> c = MyConverter(iter([[4,5,6],[6,7,8]]))
    >>> c.map_fieldnames(['a','b','c'])
    >>> list(c)
    [{u'a': 4, u'q': 5, u'c': 'nope'}, {u'a': 6, u'q': 7, u'c': 'nope'}]
    """
    drop_blank=True
    encoding = 'utf-8-sig'
    def __init__(self, data_iterator, encoding=None):
        if encoding:
            self.encoding = encoding
        self.data_iter = data_iterator
    
    def __iter__(self):
        """Return self.

        This object is it's own iterator."""
        return self
    
    def map_fieldnames(self, fields):
        """Parse the fields dictionary to prepare for mapping."""
        old_fn_list = fields
        new_fn_list = []
        cols = {}
        if hasattr(self.cols, 'items'): #Cols may be a dict
           for colname, opts in self.cols.iteritems():
                opts['name'] = colname
                if 'column' in opts:
                    cols[opts['column']] = opts
                else:
                    cols[colname] = opts
        else: #Or a list of column names
            cols = dict((x, dict(name=x)) for x in self.cols)
        for on in old_fn_list:
            if on in cols:
                new_fn_list.append(cols[on]['name'])
                cols.pop(on)
                continue
            on = on.lower()
            if on in cols:
                new_fn_list.append(cols[on]['name'])
                cols.pop(on)
                continue
            on = ' '.join(on.strip().split())
            if on in cols:
                new_fn_list.append(cols[on]['name'])
                cols.pop(on)
                continue
            on = on.replace(' ', '_')
            if on in cols:
                new_fn_list.append(cols[on]['name'])
                cols.pop(on)
                continue
            new_fn_list.append(None)
        if len(cols):
            cols = sorted(cols)
            raise MissingColumnException("Columns missing from input: %s"%(', '.join(cols))).set_cols(cols)
        self._fieldnames = [x.decode(self.encoding) if hasattr(x, 'decode') else x for x in new_fn_list]

    def __next__(self):
        """Iterate over the data, convert it, and return it modified"""
        oldret = next(self.data_iter)
        ret = dict(zip(self._fieldnames, [x.decode(self.encoding) if hasattr(x, 'decode') else x for x in oldret]))
        if self.drop_blank:
            if None in oldret:
                oldret.pop(None)
        if not hasattr(self.cols, 'items'):
            return ret
        #dict with options
        for colname, opts in self.cols.iteritems():
            if 'convert' in opts:
                key = opts['name']
                cfunc = opts['convert']
                if key in ret:
                    ret[key] = cfunc(ret[key])
        return ret
    next = __next__

class DocReader(object):
    r"""A replacement csv.DictReader that relies on column definitions defined in a subclass and deals with encoding issues.
    
    Examples:
    class MyReader(DocReader):
        cols = ['a', 'b', 'c']
    >>> class MyReader(DocReader):
    ...    cols = dict(
    ...        a = dict(column='a', convert=int),
    ...        q = dict(column='b'),
    ...        c = dict(column='c', convert=lambda x: int(x)),
    ...    )
    ...
    >>> import StringIO
    >>> list(MyReader(StringIO.StringIO("a,b,c\n1,2,3\n4,5,6")))
    [{u'a': 1, u'q': u'2', u'c': 3}, {u'a': 4, u'q': u'5', u'c': 6}]
    """
    drop_blank=True
    encoding = 'utf-8-sig'
    conv_class = StreamConverter
    def __init__(self, openfile, encoding=None, *args, **kwargs):
        if encoding:
            self.encoding = encoding
        self._r = csv.reader(openfile, *args, **kwargs)
        self._conv = self.conv_class(self._r, encoding=self.encoding)
        self._conv.cols = self.cols
        self._conv.map_fieldnames(next(self._r)) #Map field names from beginning of file
    
    def __iter__(self):
        return self

    def __next__(self):
        return next(self._conv)
    next = __next__


if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True)
