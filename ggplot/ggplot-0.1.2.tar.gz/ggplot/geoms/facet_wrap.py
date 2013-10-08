from copy import deepcopy


class facet_wrap(object):
    def __init__(self, x=None):
        self.x = x

    def __radd__(self, gg):

        x = gg.data.get(self.x)
        if x is None:
            n_dim_x = 1
        else:
            n_dim_x = x.nunique()
        
        if len(x)==1:
            n_dim_y = 1
        else:
            n_dim_y = n_dim_x - (n_dim_x / 2)
            n_dim_x = n_dim_x / 2

        gg.n_dim_x, gg.n_dim_y = n_dim_x, n_dim_y
        facets = []
        facets.append(self.x)
        gg.facets = facets

        return deepcopy(gg)
