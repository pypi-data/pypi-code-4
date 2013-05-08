import ConfigParser
import datetime
import timeparser


#choose a more restricted config for parsing times and dates:
timeparser.TimeFormats.config(
    seps=[':'],
    allow_no_sep=False,
    figures=[False, True, True],
    )
timeparser.DateFormats.config(
    seps=['.', '/', '-'],
    allow_no_sep=False,
    figures=[False, True, True],
    )
timeparser.DatetimeFormats.config(
    seps=[' ', '_'],
    allow_no_sep=False,
    )


class SmartParserMixin:
    """Extension for ConfigParser
    
    Adds some useful methods: getlist, gettime, xget and xitems
    """
    XGETTERS = ['getint', 'getfloat', 'getboolean', 'gettime', 'getdate',
            'getdatetime', 'getxlist']
    XTYPES = [int, float, timeparser.parsetime, timeparser.parsedate,
            timeparser.parsedatetime]

    def gettime(self, section, option):
        """
        Get option as datetime.time-instance.

        Args: section and option

        Which formats are accepted depens on the configuration of the
        timeparser-module. Feel free to change it.
        """
        return timeparser.parsetime(self.get(section, option))

    def getdate(self, section, option):
        """
        Get option as datetime.date-instance.

        Args: section and option

        Which formats are accepted depens on the configuration of the
        timeparser-module. Feel free to change it.
        """
        return timeparser.parsedate(self.get(section, option))

    def getdatetime(self, section, option):
        """
        Get option as datetime.datetime-instance.

        Args: section and option

        Which formats are accepted depens on the configuration of the
        timeparser-module. Feel free to change it.
        """
        return timeparser.parsedatetime(self.get(section, option))

    def getlist(self, section, option, minlen=1, types=list()):
        """
        Get option as list.

        Args:
            section and option
            minlen (int):       minimal lenght the list must have
            types (list):       list of callables to convert the list-items

        If types is given the nth list-item is converted into the nth type of
        types. If the last type of types is reached, convertion proceeding
        with the first type.
        So using a one-type-list will cause a convertion of all list-items into
        the same type.
        """
        list = self.get(section, option).split()
        if len(list) < minlen: raise ValueError('list smaller than %s' % minlen)
        if types:
            for i in range(len(list)): list[i] = types[i%len(types)](list[i])
        return list

    def getxlist(self, section, option, minlen=1, types=list()):
        """
        Get option as list. Also tries to convert the list-items.

        Args:
            section and option
            minlen (int):       minimal lenght the list must have
            types (list):       list of callables to convert the list-items

        List-items are converted into the first type that succeeds. If types is
        not given XTYPES is used.
        """
        list = self.getlist(section, option, minlen)
        for i in range(len(list)):
            for t in types or self.XTYPES:
                try: list[i] = t(list[i])
                except ValueError: continue
                else: break

        return list

    def xget(self, section, option, getters=list()):
        """
        Get option using the get-methods listed in getters or in XGETTERS.

        Args:
            section and option
            getters (list):     list of get-method-names
        """
        for method in getters or self.XGETTERS:
            args = [section, option]
            if 'list' in method: args.append(2)
            try: return getattr(self, method)(*args)
            except ValueError: continue

        return self.get(section, option)

    def xitems(self, section):
        """
        Get items of section using xget to recieve all options.

        Args: section
        """
        options = self.options(section)
        items = list()
        for opt in options:
            items.append((opt, self.xget(section, opt)))
        return items


class RawSmartParser(SmartParserMixin, ConfigParser.RawConfigParser):
    """
    SmartParser based on the ConfigParser.RawConfigParser.

    Provides methods to parse options as objects of the datetime-modules, as
    list of strings or as a list of different types.

    It also provides an additional get- and item-method (xget, xitem):
    These methods automatically try to convert values into different types.
    Also the values of the getxlist are tried to be converted automatically.

    There are two class-attributes: XGETTERS and XTYPES:

        XGETTERS = ['getint', 'getfloat', 'getboolean', 'gettime', 'getdate',
                'getdatetime', 'getxlist']
        XTYPES = [int, float, timeparser.parsetime, timeparser.parsedate,
                timeparser.parsedatetime]

    XGETTERS is a list of method-names that will be tried out by xget to
    get the option (if getters are not given).
    XTYPES is a list of callables (recieving a string and returning any kind of
    type you like) that will be tried out by getxlist to convert the
    list-items (if types are not given).
    Always the first succeeding one is used.
    """


class SmartParser(SmartParserMixin, ConfigParser.ConfigParser):
    """
    SmartParser based on the ConfigParser.ConfigParser.
    """


class SafeSmartParser(SmartParserMixin, ConfigParser.SafeConfigParser):
    """
    SmartParser based on the ConfigParser.SafeConfigParser.
    """




