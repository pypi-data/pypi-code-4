'''
Created on Aug 12, 2013

@author: ksahlin
'''

import os

import matplotlib.pyplot as plt


def histogram(x, param, bins=20, x_label='x', y_label='y', title='Histogram'):
    dest = os.path.join(param.output_directory, 'plots', title + '.png')
    plt.hist(x, bins)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)

    plt.savefig(dest)
    plt.clf()
    return()

def dot_plot(x, y, param, x_label='x', y_label='y', title='Dotplot'):
    dest = os.path.join(param.output_directory, 'plots', title + '.png')
    plt.scatter(x, y, marker='o')
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)
    plt.grid(True)

    plt.savefig(dest)
    plt.clf()
    return


def multiple_histogram(list_of_datasets, param, x_label='x', y_label='y', title='Stacked_histogram'):
    dest = os.path.join(param.output_directory, 'plots', title + '.png')
    # filter out if any of the lists contains 0 elemnets
    list_of_datasets = filter(lambda x: len(x) > 0, list_of_datasets)
    for dataset in list_of_datasets:
        plt.hist(dataset, alpha=0.5)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)

    plt.savefig(dest)
    plt.clf()

    return()





#def VizualizeGraph(G, param, Information):
#    import os
#    try:
#        import matplotlib
#        matplotlib.use('Agg')
#
#        try:
#            os.mkdir(param.output_directory + '/graph_regions' + str(int(param.mean_ins_size)))
#        except OSError:
#            #directory is already created
#            pass
#        counter = 1
#        import copy
#
#        G_copy = copy.deepcopy(G)
#        RemoveIsolatedContigs(G_copy, Information)
#        CB = nx.connected_component_subgraphs(G_copy)
#        for cycle in CB:
#            nx.draw(cycle)
#            matplotlib.pyplot.savefig(param.output_directory + 'graph_regions' + str(int(param.mean_ins_size)) + '/' + str(counter) + '.png')
#            matplotlib.pyplot.clf()
#            counter += 1
#    except ImportError:
#        pass
#    return()
