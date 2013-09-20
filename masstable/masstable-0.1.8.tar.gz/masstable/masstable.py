import pandas as pd
import os
import math
# TODO: Improve Access operator

package_dir, _ = os.path.split(__file__)


def memoize(f):
    """Really fast memoizer"""
    class memodict(dict):

        def __missing__(self, key):
            ret = self[key] = f(key)
            return ret
    return memodict().__getitem__


class Table(object):

    def __init__(self, name='', df=None):
        "Init from a Series/Dataframe (df) of a file (name)"
        if df is not None:  # init from dataframe
            self.df = df
            self.name = name
        elif name in self.names:  # init from name
            self.name = name
            self.df = self.from_name(name).df
            # self.df.name = name
        else:
            print ('Error: Invalid table name. Valid names are:')
            print (' '.join(Table.names))
            return None

    names = ['AME2003', 'AME2003all', 'AME2012', 'AME2012all', 'AME1995', 'AME1995all',
             'DUZU', 'FRDM95', 'KTUY05', 'ETFSI12', 'HFB14', 'HFB26', 'TCSM12', 'BR2013', 'MAJA88',
             'GK88', 'WS32010', 'WS32011', 'SVM13']

    @classmethod
    def from_name(cls, name):
        "Imports a mass table from a file"
        filename = os.path.join(package_dir, 'data', name + '.txt')
        return cls.from_file(filename, name)

    @classmethod
    def from_file(cls, filename, name=''):
        "Imports a mass table from a file"
        df = pd.read_csv(filename, header=0, delim_whitespace=True, index_col=[0, 1])['M']
        df.name = name
        return cls(df=df, name=name)

    @classmethod
    def from_ZNM(cls, Z, N, M, name=''):
        """
        Creates a table from array Z,N,M

        Example:
        ________

        >>> Z = [82, 82, 83]
        >>> N = [126, 127, 130]
        >>> M = [-21.34, -18.0, -14.45]
        >>> Table.from_ZNM(Z, N, M, name='Custom Table')
        Z   N
        82  126   -21.34
            127   -18.00
        83  130   -14.45
        Name: Custom Table, dtype: float64
        """
        df = pd.DataFrame.from_dict({'Z': Z, 'N': N, 'M': M}).set_index(['Z', 'N'])['M']
        df.name = name
        return cls(df=df, name=name)

    @classmethod
    def from_array(cls, arr, name=''):
        Z, N, M = arr.T
        return cls.from_ZNM(Z, N, M, name)

    def to_file(self, filename):
        with open(filename, 'w') as f:
            f.write('Z   N   M\n')
        self.df.to_csv(filename, sep='\t', mode='a')

    @property
    def Z(self):
        return self.df.index.get_level_values('Z').values

    @property
    def N(self):
        return self.df.index.get_level_values('N').values

    @property
    def A(self):
        return self.Z + self.N

    def __getitem__(self, index):
        """Access [] operator
        Examples:

        >>> Table('DUZU')[82, 126:127]
                DUZU
        Z   N
        82  126 -22.29
            127 -17.87

        >>> Table('AME2012all')[118, :]
                AME2012all
        Z   N
        118 173  198.93
            174  199.27
            175  201.43

        """
        if isinstance(index, tuple) and len(index)==2:
            if isinstance(index[0], int):               # single N: "[82, :]"
                startZ, stopZ = index[0], index[0]

            if isinstance(index[1], int):
                startN, stopN = index[1], index[1]      # single N: "[:, 126]"

            if isinstance(index[0], slice):             # Z slice: "[:, 126]"
                startZ, stopZ, stepZ = index[0].start, index[0].stop, index[0].step

            if isinstance(index[1], slice):              # N slice: "[:, 126]"
                startN, stopN, stepN = index[1].start, index[1].stop, index[1].step

            if not startZ: startZ = min(self.Z) # might be optimized
            if not stopZ:  stopZ = max(self.Z)
            if not startN: startN = min(self.N)
            if not stopN:  stopN = max(self.N)

            x = self.df.reset_index()
            x = x.loc[(x.Z>=startZ)&(x.Z<=stopZ)&(x.N>=startN)&(x.N<=stopN)]
            return x.set_index(['Z', 'N']).sortlevel(0)

    def __setitem__(self, key, value):
        Z = key[0]
        N = key[1]
        self.df.ix[(Z,N)] = value

    def __getattr__(self, attr):
        # TODO: Pythonize
        "Pass properties and method calls to the DataFrame object"
        instance_method = getattr(self.df, attr)
        if callable(instance_method):
            def fn(*args, **kwargs):
                result = instance_method(*args, **kwargs)   # ()->call the instance method
                if isinstance(result, (pd.DataFrame, pd.Series)):
                    try:
                        name = result.name
                    except AttributeError:
                        name = None
                    return Table(name=name, df=result)  # wrap in Table class
            return fn
        else:
            return instance_method

    def __iter__(self):
        for e in self.df.iteritems():
            yield e

    def __add__(self, other):
        return Table(df=self.df + other.df,
                     name="{}+{}".format(self.name, other.name))

    def __sub__(self, other):
        return Table(df=self.df - other.df,
                     name="{}+{}".format(self.name, other.name))

    def align(self, *args, **kwargs):
        result = self.df.align(*args, **kwargs)[0]
        return Table(result.name, result)

    def select(self, condition, name=''):
        """
        Selects nuclei according to condition

        Parameters
        ----------
        condition : function,
            Can have one of the signatures f(M), f(Z,N) or f(Z, N, M)
            must return a boolean value
        name: string, optional name for the resulting Table
        Example:
        ----------
        greater_than_8 = lambda Z,N: Z > 8 and N > 8
        Table('AME2003').select(greater_than_8)
        """
        if condition.func_code.co_argcount == 1:
            idx = [(Z, N) for (Z, N), M in self if condition(M)]
        if condition.func_code.co_argcount == 2:
            idx = [(Z, N) for (Z, N) in self.index if condition(Z, N)]
        if condition.func_code.co_argcount == 3:
            idx = [(Z, N) for (Z, N), M in self if condition(Z, N, M)]
        index = pd.MultiIndex.from_tuples(idx, names=['Z', 'N'])
        return Table(df=self.df.ix[index], name=name)

    @classmethod
    def empty(cls, name=''):
        return cls(df=pd.DataFrame(index=[], columns=[]), name=name)

    def __len__(self):
        "Return the total number of nuclei"
        return len(self.df)

    def intersection(self, table):
        """
        Select nuclei which also belong to table

        Parameters
        ----------
        table: Table, Table object

        Example:
        ----------
        Table('AME2003').intersection(Table('AME1995'))
        """
        idx = self.df.index & table.df.index
        return Table(df=self.df[idx], name=self.name)

    def not_in(self, table):
        """
        Select nuclei not in table

        Parameters
        ----------
        table: Table, Table object from where nuclei should be removed

        Example:
        ----------
        Find the new nuclei in AME2003 with Z,N >= 8:

        >>> condition = lambda Z,N: Z>=8 and N>=8
        >>> len(Table('AME2003').select(condition).not_in(Table('AME1995')))
        389
        """
        idx = self.df.index - table.df.index
        return Table(df=self.df[idx], name=self.name)

    @property
    @memoize
    def odd_odd(self):
        return self.select(lambda Z, N: (Z % 2) and (N % 2), name=self.name)

    @property
    @memoize
    def odd_even(self):
        return self.select(lambda Z, N: (Z % 2) and not(N % 2), name=self.name)

    @property
    @memoize
    def even_odd(self):
        return self.select(lambda Z, N: not(Z % 2) and (N % 2), name=self.name)

    @property
    @memoize
    def even_even(self):
        return self.select(lambda Z, N: not(Z % 2) and not(N % 2), name=self.name)

    def error(self, relative_to='AME2003'):
        """
        Calculate error difference

        Parameters
        ----------
        relative_to : string,
            a valid mass table name.

        Example:
        ----------
        Table('DUZU').error(relative_to='AME2003')
        """
        df = self.df - Table(relative_to).df
        return Table(df=df)

    def rmse(self, relative_to='AME2003'):
        """Calculate root mean squared error

        Parameters
        ----------
        relative_to : string,
            a valid mass table name.

        Example:
        ----------
        >>> template = '{0:10}|{1:^6.2f}|{2:^6.2f}|{3:^6.2f}'
        >>> print 'Model      ', 'AME95 ', 'AME03 ', 'AME12 '  #  Table header
        ... for name in Table.names:
        ...     print template.format(name, Table(name).rmse(relative_to='AME1995'),
        ...                             Table(name).rmse(relative_to='AME2003'),
        ...                             Table(name).rmse(relative_to='AME2012'))
        Model       AME95  AME03  AME12
        AME2003   | 0.13 | 0.00 | 0.13
        AME2003all| 0.42 | 0.40 | 0.71
        AME2012   | 0.16 | 0.13 | 0.00
        AME2012all| 0.43 | 0.43 | 0.69
        AME1995   | 0.00 | 0.13 | 0.16
        AME1995all| 0.00 | 0.17 | 0.21
        DUZU      | 0.52 | 0.52 | 0.76
        FRDM95    | 0.79 | 0.78 | 0.95
        KTUY05    | 0.78 | 0.77 | 1.03
        ETFSI12   | 0.84 | 0.84 | 1.04
        HFB14     | 0.84 | 0.83 | 1.02
        """

        error = self.error(relative_to=relative_to)
        return math.sqrt((error.df ** 2).mean())

    @property
    @memoize
    def binding_energy(self):
        M_P = 938.2723
        # MeV
        M_E = 0.5110
        # MeV
        M_N = 939.5656
        # MeV
        AMU = 931.494028
        # MeV
        df = self.Z * (M_P + M_E) + (self.A - self.Z) * M_N - (self.df + self.A * AMU)
        return Table(df=df, name='BE' + '(' + self.name + ')')

    @property
    @memoize
    def q_alpha(self):
        """Return Q_alpha"""
        M_ALPHA = 2.4249156         # He4 mass excess in MeV
        f = lambda parent, daugther: parent - daugther - M_ALPHA
        return self.derived('Q_alpha', (-2, -2), f)

    @property
    @memoize
    def q_beta(self):
        """Return Q_beta"""
        f = lambda parent, daugther: parent - daugther
        return self.derived('Q_beta', (1, -1), f)

    @property
    @memoize
    def s2n(self):
        """Return 2 neutron separation energy"""
        M_N = 8.0713171         # neutron mass excess in MeV
        f = lambda parent, daugther: -parent + daugther + 2 * M_N
        return self.derived('s2n', (0, -2), f)

    @property
    @memoize
    def s1n(self):
        """Return 1 neutron separation energy"""
        M_N = 8.0713171         # neutron mass excess in MeV
        f = lambda parent, daugther: -parent + daugther + M_N
        return self.derived('s1n', (0, -1), f)

    @property
    @memoize
    def s2p(self):
        """Return 2 proton separation energy"""
        M_P = 7.28897050         # proton mass excess in MeV
        f = lambda parent, daugther: -parent + daugther + 2 * M_P
        return self.derived('s2p', (-2, 0), f)

    @property
    @memoize
    def s1p(self):
        """Return 1 proton separation energy"""
        M_P = 7.28897050         # proton mass excess in MeV
        f = lambda parent, daugther: -parent + daugther + M_P
        return self.derived('s1p', (-1, 0), f)

    def derived(self, name, relative_coords, formula):
        """Helper function for derived quantities"""
        relZ, relN = relative_coords
        daughter_idx = [(x[0] + relZ, x[1] + relN) for x in self.df.index]
        values = formula(self.df.values, self.df.loc[daughter_idx].values)
        return Table(df=pd.Series(values, index=self.df.index, name=name + '(' + self.name + ')'))

    @property
    @memoize
    def ds2n(self):
        idx = [(x[0] + 0, x[1] + 2) for x in self.df.index]
        values = self.s2n.values - self.s2n.loc[idx].values
        return Table(df=pd.Series(values, index=self.df.index, name='ds2n' + '(' + self.name + ')'))

    @property
    @memoize
    def ds2p(self):
        idx = [(x[0] + 2, x[1]) for x in self.df.index]
        values = self.s2p.values - self.s2p.loc[idx].values
        return Table(df=pd.Series(values, index=self.df.index, name='ds2p' + '(' + self.name + ')'))

    def __repr__(self):
        return self.df.__repr__()

    def __str__(self):
        return self.df.__str__()

    def join(self, join='outer', *tables):
        return Table(df=pd.concat([self.df] + [table.df for table in tables], axis=1))

if __name__ == '__main__':
    # print Table('AME2003').head().join(Table('AME2012').head(), Table('DUZU').odd_odd.head())
    # print Table.from_file('data/AME1995.txt', 'test')
    # print Table.load('AME1995')
    # print Table('GK88')
    # print Table('FRDM95').
    print Table('FRDM95')[101, 220]
    # print Table('AME2012').tail()
    # print Table.from_list([1,1])
