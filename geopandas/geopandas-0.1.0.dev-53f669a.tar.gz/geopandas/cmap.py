from matplotlib.colors import LinearSegmentedColormap

def tableau20(N=20):
    """ Implement the Tableau 20 colormap for matplotlib

    http://tableaufriction.blogspot.in/2012/11/finally-you-can-use-tableau-data-colors.html
    """
    colors = [(227, 119, 194), (23, 190, 207), (158, 218, 229),
              (188, 189, 34), (199, 199, 199), (219, 219, 141),
              (127, 127, 127), (140, 86, 75), (196, 156, 148),
              (247, 182, 210), (148, 103, 189), (152, 223, 138),
              (197, 176, 213), (214, 39, 40), (255, 152, 150),
              (31, 119, 180), (44, 160, 44), (174, 199, 232),
              (255, 127, 14), (255, 187, 120)]
    r, g, b = zip(*colors)
    data = {'red' : [(i / (N - 1.0), v/255.0, v/255.0) for i, v in enumerate(r)],
             'green' : [(i / (N - 1.0), v/255.0, v/255.0) for i, v in enumerate(g)],
             'blue' : [(i / (N - 1.0), v/255.0, v/255.0) for i, v in enumerate(b)]}
    cmap = LinearSegmentedColormap('tableau20', data, N=N)
    return cmap
