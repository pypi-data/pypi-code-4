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

    def __init__(self, name=None, df=None):
        "Init from a Series/Dataframe (df) of a file (name)"
        if df is not None:
            self.df = df
        elif name in self.names:
            self.name = name
            self.df = self.load(name)
            self.df.name = name


    names = ['AME2003', 'AME2003all', 'AME2012', 'AME2012all', 'DUZU', 'FRDM95', 'KTUY05', 'ETFSI12', 'HFB14']

    def load(self, name):
        "Imports a mass table from a file"
        filename = os.path.join(package_dir, 'data', name.upper() + '.txt')
        df = pd.read_csv(filename, header=0, delim_whitespace=True, index_col=[0, 1])
        return df['M']

    @classmethod
    def from_list(cls, l, name=None):
        return Table(df=l, name=name)

    @property
    def Z(self):
        return self.df.index.get_level_values('Z').values

    @property
    def N(self):
        return self.df.index.get_level_values('N').values

    @property
    def A(self):
        return self.Z + self.N

    def __getitem__(self, param):
        """Access [] operator"""
        if isinstance(param, tuple):
            Z = param[0]
            N = param[1]
            try:
                return self.df.ix[(Z, N)]
            except IndexError:
                return None
        else:
            return self.df[param]

    def __getattr__(self, attr):
        # TODO: Pythonize
        "Pass properties and method calls to the DataFrame object"
        instance_method = getattr(self.df, attr)
        if callable(instance_method):
            def fn(*args):
                result = instance_method(*args)   # ()->call the instance method
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

    def align(self, *args, **kwargs):
        result = self.df.align(*args, **kwargs)[0]
        return Table(result.name, result)

    def select(self, condition, name=None):
        """
        Selects nuclei according to condition

        Parameters
        ----------
        condition : function, signature: condition(Z,N)->boolean

        Example:
        ----------
        greater_than_8 = lambda Z,N: Z > 8 and N > 8
        Table('AME2003').select(greater_than_8)
        """
        idx = [(Z, N) for Z, N in self.df.index if condition(Z, N)]
        return Table(df=self.df[idx], name=name)

    @property
    @memoize
    def odd_odd(self):
        return self.select(lambda Z,N: (Z % 2) and (N % 2), name=self.name)
    
    @property
    @memoize    
    def odd_even(self):
        return self.select(lambda Z,N: (Z % 2) and not(N % 2), name=self.name)
    
    @property
    @memoize    
    def even_odd(self):
        return self.select(lambda Z,N: not(Z % 2) and (N % 2), name=self.name)
    
    @property
    @memoize    
    def even_even(self):
        return self.select(lambda Z,N: not(Z % 2) and not(N % 2), name=self.name)  

    def error(self, relative_to='AME2003'):
        ''
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
        return self.df - Table(relative_to).df

    def rmse(self, relative_to='AME2003'):
        'Calculate mean squared error'
        error = self.error(relative_to=relative_to)
        return math.sqrt((error ** 2).mean())

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
        return self.Z * (M_P + M_E) + (self.A - self.Z) * M_N - (self.df + self.A * AMU)

    @property
    @memoize
    def q_alpha(self):
        """Return Q_alpha"""
        M_ALPHA = 2.4249156         # He4 mass excess in MeV
        f = lambda parent, daugther: parent - daugther - M_ALPHA
        return self.derived('Q_alpha', (0, -2), f)

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
        (relZ, relN) = relative_coords
        daughter_idx = [(x[0] + relZ, x[1] + relN) for x in self.df.index]
        values = formula(self.df.values, self.df[daughter_idx].values)
        return Table(df=pd.Series(values, index=self.df.index, name=name + '(' + self.name + ')'))

    def __repr__(self):
        return self.df.__repr__()

    def __str__(self):
        return self.df.__str__()

    def join(self, join='outer', *tables):
        return Table(df=pd.concat([self.df] + [table.df for table in tables], axis=1))

if __name__ == '__main__':
    print Table('AME2003').head().join(Table('AME2012').head(), Table('DUZU').odd_odd.head())
    print Table('AME2012all').tail()
    print Table('AME2012').tail()
    print Table.from_list([1,1])
