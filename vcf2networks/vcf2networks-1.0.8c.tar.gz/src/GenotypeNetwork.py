#!/usr/bin/env python
"""
----------------------------------
Genotype Network class and functions
----------------------------------

"""
#import igraph0 as igraph
import igraph
import itertools
import logging
#import pprint
import operator
#import cPickle
import random
import numpy
import igraph.vendor.texttable
try:
    import collections
except:
    from src import collections as collections
#import re
import ast
from custom_exceptions import *


class GenotypeNetwork(igraph.Graph):
    """
    Represents a Genotype Network

    ==============
    Description
    ==============
    
    Class to represent a GenotypeNetwork in python. 
      Uses the igraph C library and its python bindings.

    See the file docs/GenotypeNetworkTutorial.py for more examples and 
      doctests on how to use this class.

    ==============
    Parameters:
    ==============

    * chromosome_len    -> size of chromosomes
    * name              -> descriptive name for the network
    * parallelize       -> if True, use multicore module to build the network (not implemented yet)
    * args              -> other arguments to be passed to igraph.Graph

    ==============
    Examples
    ==============

    Create an empty Genotype Network:
    >>> phenotype1 = GenotypeNetwork(chromosome_len=3, name='phenotype1')

    Populate the graph from a set of genotypes:
    >>> genotypes = ['001', '010', '000']
    >>> phenotype1.populate_from_binary_strings(genotypes)
    
    # Print informations about the network:
    >>> print(phenotype1)
    Genotype Network (name = 'phenotype1', chromosome lenght = 3, |V| = 3, |E| = 2)

    >>> print(phenotype1.summary()) #doctest: +NORMALIZE_WHITESPACE
    3 nodes, 2 edges, undirected
    <BLANKLINE>
    Number of components: 1
    Diameter: 2
    Density: 0.6667
    Average path length: 1.3333

    # Print node degree distribution for the network
    >>> phenotype1.degree()
    [1, 1, 2]


    """
    def __init__(self, chromosome_len, name='', genotypes=None, parallelize=False, *args, **kwd):
        igraph.Graph.__init__(self, name=name, *args, **kwd)
        self['name'] = name
        self['chromosome_len'] = int(chromosome_len)
        self["pop"] = "glob"
        self["continent"] = "glob"
        self["snp_ids"] = ["NA"] * chromosome_len
        self["chromosomes"] = ["NA"] * chromosome_len
        self["positions"] = [numpy.nan] * chromosome_len
        self["ref_alleles"] = ["NA"] * chromosome_len

        if genotypes is not None:
            self.populate_from_binary_strings(genotypes, 
                            parallelize=parallelize)
 
        self.layout_initialized = False
        self.network_properties_calculated = False

    def __str__(self):
        """
        determine how the GenotypeNetwork will be printed

        >>> phenotype1 = GenotypeNetwork(5, 'myphenotype')
        >>> print phenotype1
        Genotype Network (name = 'myphenotype', chromosome lenght = 5, |V| = 0, |E| = 0)

        """
        representation = "Genotype Network (name = '{0}', chromosome lenght = {1}, |V| = {2}, |E| = {3})".format(
                                                self['name'], self['chromosome_len'], self.vcount(), self.ecount())
        return representation

    def summary(self):
        """
        Mimics the old igraph 0.5.4 summary() output.
    

        Example summary:

        >>> phenotype1 = GenotypeNetwork(chromosome_len=3, name='phenotype1')

        Populate the graph from a set of genotypes:
        >>> genotypes = ['001', '010', '000']
        >>> phenotype1.populate_from_binary_strings(genotypes)
        >>> print (igraph.Graph.summary(phenotype1))
        IGRAPH U--- 3 2 -- phenotype1
        + attr: chromosome_len (g), chromosomes (g), continent (g), distance_definition (g), individuals (g), name (g), pop (g), positions (g), ref_alleles (g), snp_ids (g), genotype (v), n_datapoints (v), value (v)

        >>> print(phenotype1.summary())
        3 nodes, 2 edges, undirected
        <BLANKLINE>
        Number of components: 1
        Diameter: 2
        Density: 0.6667
        Average path length: 1.3333

        """
        template = "{0} nodes, {1} edges, undirected\n\nNumber of components: {2}\nDiameter: {3}\nDensity: {4:.4f}\nAverage path length: {5:.4f}"
        output = template.format(self.vcount(), self.ecount(), len(self.components()), self.diameter(), self.density(), self.average_path_length())
        return(output)



    def __get_layout__(self):
        """
        Calculate the layout of the graph for plotting purposes.

        >>> phenotype1 = GenotypeNetwork(3, genotypes=['011', '010', '000'])
        >>> phenotype1.__get_layout__()
        >>> print phenotype1.vs['pos_x']
        [1, 2, 0]
        >>> print phenotype1.vs['pos_y']
        [0.5, -0.5, 0.5]
        >>> print phenotype1.vs['layout']
        [(1, 0.5), (2, -0.5), (0, 0.5)]

        This is an internal function called by self.plot() when needed.

        """
        self.vs['pos_x'] = [n['genotype'].count('1') for n in self.vs]
        self.vs['pos_y'] = [get_y_position(n['genotype']) for n in self.vs]
        self.vs['layout'] = zip(self.vs['pos_x'], self.vs['pos_y'])
        self.layout_initialized = True

    def __calculate_network_properties__(self):
        """
        Internal function to calculate many interesting network properties. 
        
        These will be stored as properties of the GenotypeNetwork object, and available when it is exported to graphML, and to functions such as self.csv_report()

        This function is not called unless one of the functions that need it is called (e.g. write_graphml, csv_report). 
        >>> mynet = GenotypeNetwork(chromosome_len=4,  name="Mygene", genotypes=["0000", "0000","0001", "0010", "0111"])
        >>> print mynet.csv_report()
        Mygene glob 4 5 4 2 2 2 0.3333 1.25 1.3333 1.0 2 0.25 0.4018

        n_genotypes is the number of genotypes used to generate the network. 
        In this case the number of nodes is 4, but n_genotypes is 5, because two genotypes ("0000" and "0000") were the same.
        >>> print mynet['n_genotypes']
        5

        The density is calculated by the igraph library
        >>> print mynet['density']
        0.3333

        av_datapoints_per_node is not related to density. Instead, it represents how many genotypes, on average, represent every node.
        In this case, it is between 1 and 2, as three nodes have 1 genotype, and one node ("0000") has 2.
        >>> print mynet['av_datapoints_per_node']
        1.25

        For other properties, see the documentation of igraph.
        >>> print mynet['n_components']
        2

        >>> print mynet['av_degree']
        1.0
        """
        # DESCRIPTIVE PROPERTIES
        # if gene attribute is not defined, define it as the network name
        if not 'gene' in self.attributes():
            self['gene'] = self['name']
        self['n_snps'] = self['chromosome_len']
        self['n_genotypes'] = sum(self.vs['n_datapoints'])
#        self['n_genotypes'] = sum([len(individuals) for individuals in self.vs['node_individuals']])
        self['n_datapoints'] = self['n_genotypes']
        self['av_datapoints_per_node'] = round(numpy.mean(self.vs['n_datapoints']), 4)
        self['av_datapoints_per_vertex'] = self['av_datapoints_per_node']
        self.vs['perc_datapoints'] = numpy.divide(self.vs['n_datapoints'], 1.0 * sum(self.vs['n_datapoints']))
#        print("source and target:")
        self.es['perc_datapoints'] = [sum((self.vs(e.source)['perc_datapoints'][0], self.vs(e.target)['perc_datapoints'][0])) for e in self.es()]
#        print self.vs['n_datapoints']
#        print self.es['perc_datapoints']
        self.es['inv_perc_datapoints'] = numpy.divide(1.0, self.es['perc_datapoints'])
        self.vs['inv_perc_datapoints'] = numpy.divide(1.0, self.vs['perc_datapoints'])
#        print self.es['perc_datapoints']

        self['n_vertices'] = self.vcount()
        self['n_nodes'] = self['n_vertices']
        self['n_edges'] = self.ecount()
        self['n_components'] = len(self.components())


        # SNPs AND PHYSICAL POSITION PROPERTIES
#        print self['n_snps'], self['snp_ids'], len(self['snp_ids'])
        central_snp_index = (self['n_snps']-1)/2
        self['central_snp_position'] = self['positions'][central_snp_index]
        self['central_snp'] = self['snp_ids'][central_snp_index] # if the total number of SNPs is 10, the central SNP is the one in position 4 (or 5 counting from 1)
        self['chromosome'] = list(set(self['chromosomes']))[0]
        self['downstream_position'] = min(self['positions'])
        self['upstream_position'] = max(self['positions'])
#        print self.vs['positions']
#        print self['positions']
        if operator.isNumberType(self['upstream_position']) and not self['upstream_position'] is numpy.nan:
            self['region_size'] = int(self['upstream_position']) - int(self['downstream_position'])
        else:
            self['region_size'] = numpy.nan


        # PATH LENGTH PROPERTIES
        self['av_path_length'] = round(self.average_path_length(), 4)
#        print "edge weights (based on percentage of data points in the nodes connected):"
#        print self.es['perc_datapoints']
#        print [e.tuple for e in self.es()]
#        print self.shortest_paths(weights=self.es['perc_datapoints'])
        if self.ecount() == 0:
            self['av_w_path_length'] = numpy.nan
            self['av_w_path_length_inv'] = numpy.nan
        else:
            self['av_w_path_length'] = round(numpy.mean([path_len for path_len in sum(self.shortest_paths(weights=self.es['perc_datapoints']), []) if path_len > 0 and path_len != float('inf')]), 4)
            self['av_w_path_length_inv'] = round(numpy.mean([path_len for path_len in sum(self.shortest_paths(weights=self.es['inv_perc_datapoints']), []) if path_len > 0 and path_len != float('inf')]), 4)
#            self['av_w_path_length'] = round(numpy.mean([path_len for path_len in sum(self.shortest_paths(), []) if path_len > 0 and path_len != float('inf')]), 4)
#            self['av_w_path_length_inv'] = round(numpy.mean([path_len for path_len in sum(self.shortest_paths(), []) if path_len > 0 and path_len != float('inf')]), 4)
        self['var_path_length'] = round(self.path_length_hist().var, 4)
#        self['min_path_length'] = round(self.average_path_length(), 4)
#        self['max_path_length'] = round(self.average_path_length(), 4)
        self['diameter'] = self.diameter()


        ## DEGREE PROPERTIES
        self['av_degree'] = round(numpy.mean(self.degree()), 4)
        self['av_w_degree'] = round(numpy.mean(numpy.multiply(self.degree(), self.vs['perc_datapoints'])), 4)
        self['av_w_degree_inv'] = round(numpy.mean(numpy.multiply(self.degree(), self.vs['inv_perc_datapoints'])), 4)
        self['var_degree'] = round(numpy.var(self.degree()), 4)
        self['median_degree'] = round(numpy.median(self.degree()), 4)
        self['max_degree'] = self.maxdegree()

        self['av_closeness'] = round(numpy.mean(self.closeness()), 4)
        self['var_closeness'] = round(numpy.var(self.closeness()), 4)
        self['median_closeness'] = round(numpy.median(self.closeness()), 4)
        self['max_closeness'] = get_max(self.closeness())

        self['density'] = round(self.density(), 4)

        self['av_betweenness'] = round(numpy.mean(self.betweenness()), 4)
        self['var_betweenness'] = round(numpy.var(self.betweenness()), 4)
        self['median_betweenness'] = round(numpy.median(self.betweenness()), 4)
        self['max_betweenness'] = get_max(self.betweenness())
      
        self.network_properties_calculated = True


    def write_graphml(self, *args, **kwd):
        """
        The igraph 0.6 version doesn't support storing dict attributes to graphml files.

        This function is a wrapper to convert all dict attributes to strings before calling write_graphml.
        """
        newnetwork = self
        for attribute in newnetwork.attributes():
#            print "ATTRIBUTE: ", attribute, type(newnetwork[attribute]), type(newnetwork[attribute]) == dict
            if type(newnetwork[attribute]) == dict:
#                print "STORING", attribute, newnetwork 
                newnetwork[attribute] = str(self[attribute])
            if type(newnetwork[attribute]) == list:
#                print "STORING", attribute, newnetwork 
                newnetwork[attribute] = str(self[attribute])
#                print newnetwork[attribute][:30], type(newnetwork[attribute])
#        print [(a, type(a)) for a in newnetwork.attributes()]
        igraph.Graph.write_graphml(newnetwork, *args, **kwd)

    def populate_from_binary_strings(self, genotypes, 
                                            distance=1,
                                            parallelize=False):
        """
        populate the GenotypeNetwork from a list of genotypes
        >>> phenotype1 = GenotypeNetwork(3)
    
        ==========
        Parameters
        ==========

        genotypes must be a list containing strings of the same length, and composed only by "0" and "1" characters. 

        >>> genotypes = ['001', '010', '000', '000', '100', '000'] # note: duplicated genotypes are merged
        >>> phenotype1.populate_from_binary_strings(genotypes)
        >>> print phenotype1
        Genotype Network (name = '', chromosome lenght = 3, |V| = 4, |E| = 3)

        >>> print phenotype1.vs['genotype']
        ['010', '001', '000', '100']

        >>> print phenotype1.vs['value']
        [2, 1, 0, 4]

        >>> print phenotype1.summary() #doctest: +NORMALIZE_WHITESPACE
        4 nodes, 3 edges, undirected
        <BLANKLINE>
        Number of components: 1
        Diameter: 2
        Density: 0.5000
        Average path length: 1.5000

        See the file docs/GenotypeNetworkTutorial.py for more examples and doctests on how to use this class.

        """
        if parallelize is True:
            raise NotImplementedError
        if not (type(genotypes) in (list, tuple) ) or not (set([len(x) for x in genotypes]) == set([self['chromosome_len']])):
            raise GenotypeNetworkInitError("The list of genotypes provided to .populate_from_binary_strings is incorrect. {0} (network {1})".format(str(genotypes), self['name']))
        
        self['distance_definition'] = distance
        self['individuals'] = None

        genotype_counts = collections.Counter(genotypes)
        node_genotypes = []
        node_values = []
        node_n_datapoints = []
        self.add_vertices(len(genotype_counts.keys()))
        for (genotype, geno_count)  in genotype_counts.items():
            node_genotypes.append(genotype)
            try:
                node_values.append(int(genotype, base=2))
            except ValueError:
                raise GenotypeNetworkInitError("something went wrong when converting genotypes to binary strings. Check if any SNP is triallelic")
            node_n_datapoints.append(geno_count)
        self.vs['genotype'] = node_genotypes
        self.vs['value'] = node_values
        self.vs['n_datapoints'] = node_n_datapoints
        for genotype1 in self.vs:
#            logging.debug(str((genotype1.index, genotype1['name'], genotype1['value'])))
            for genotype2 in self.vs:
                if genotype1.index >= genotype2.index:
                    pair_distance = '{0:08b}'.format(genotype1['value']^genotype2['value']).count('1')
                    if pair_distance > 0 and pair_distance <= distance:
#                    print genotype1['name'], genotype2['name'],
#                    print '{:08b}'.format(genotype1['value']^genotype2['value']).count('1')
                        self.add_edge(genotype1.index, genotype2.index)


    def populate_from_binary_strings_and_individuals(self, genotypes,
                                                            distance=1,
                                                            individuals=False,
                                                            individuals_dict=False,
                                                            parallelize=False):
        """
        ======================
        Adding individual info
        ======================

        In the newer versions, it is possible to add information on individuals 
            and populations to the network.

        To do so, you need to provide a list of individuals, and a dictionary 
            containing the annotations on the individuals.

        The list of individuals must be of the same length as the genotypes, 
            and it will be assumed that there is correspondence between positions, 
            so that the genotype of the individual in the first position is also 
            in the first position of the genotypes list.

        >>> genotypes = ['001', '000', '000', '000']
        >>> individuals = ['HG1', 'HG2', 'HG3', 'HG4']
        >>> individuals_dict = {
        ...             'HG1': {'continent': 'EUR', 'subpop': 'TSC', 
        ...                     'phenotype1': 'ILLUMINA', 'phenotype2': 'tall', 'phenotype3': 'good'}, 
        ...             'HG2': {'continent': 'EUR', 'subpop': 'GBR', 
        ...                     'phenotype1': 'ABI_SOLID', 'phenotype2': 'tall', 'phenotype3': 'bad'}, 
        ...             'HG3': {'continent': 'AFR', 'subpop': 'AFR', 
        ...                     'phenotype1': 'ILLUMINA', 'phenotype2': 'short', 'phenotype3': 'neutral'}, 
        ...             'HG4': {'continent': 'AFR', 'subpop': 'YRI', 
        ...                     'phenotype1': 'ILLUMINA', 'phenotype2': 'tall', 'phenotype3': 'bad'}, 
        ... }
        >>> mynet = GenotypeNetwork(3)
        >>> mynet.populate_from_binary_strings_and_individuals(genotypes, individuals=individuals, individuals_dict=individuals_dict)
        >>> mynet.vs['genotype']
        ['001', '000']
        >>> mynet.vs['value']
        [1, 0]
        >>> mynet.vs['n_datapoints']
        [1, 3]
        >>> mynet.vs['node_individuals'] 
        [['HG1'], ['HG4', 'HG2', 'HG3']]
        >>> mynet.vs['continent']
        [['EUR'], ['AFR', 'EUR']]
        >>> mynet.vs['subpop']
        [['TSC'], ['AFR', 'GBR', 'YRI']]
        >>> mynet.vs['phenotype1']
        [['ILLUMINA'], ['ABI_SOLID', 'ILLUMINA']]
        >>> mynet.vs['phenotype2'] # the first node is only "tall", the second is both "tall" and "short"
        [['tall'], ['short', 'tall']]
        >>> mynet.vs['phenotype3'] # the first node is only "tall", the second is both "tall" and "short"
        [['good'], ['bad', 'neutral']]

        >>> print mynet.vs[1]['phenotype2']  # phenotype2 of node 000
        ['short', 'tall']

        >>> print mynet.vs[1]['phenotype1']  # phenotype2 of node 000
        ['ABI_SOLID', 'ILLUMINA']

        BEWARE: the order of individuals is shuffled after adding them to the network. So, in order to get the 
        annotation of a certain individual, you need to access to the individual_dict, which is stored as network attribute.
        >>> print mynet['individuals_dict']['HG3']['continent']
        AFR
        """
        # Check that the genotypes argument contains a list of strings of the same length
#        print "GENOTYPES",  genotypes[0:5]
#        print "INDIVIDUALS", individuals[0:5]
#        print "INDIVIDUALS_DICT", individuals_dict.items()[0:2]

        if not (type(genotypes) in (list, tuple) ) or not (set([len(x) for x in genotypes]) == set([self['chromosome_len']])):
            raise GenotypeNetworkInitError("The list of genotypes provided to .populate_from_binary_strings_and_individuals is incorrect. {0} (network {1})".format(str(set(genotypes)), self['name']))
        
        self['distance_definition'] = distance

        # if there are no information on individuals, this method is more efficient to add nodes.
        if not (len(genotypes) == len(individuals)):
#                logging.debug( genotypes)
#                logging.debug( individuals)
#                logging.debug( individuals_dict.keys())
            raise GenotypeNetworkInitError("individuals var must be of the same length as genotypes")
        
        self['individuals'] = individuals
        self['individuals_dict'] = individuals_dict

        # These lists contain values related to each node. Each element of these lists is relative to a single node.
        node_genotypes = []
        node_n_datapoints = []
        node_individuals = [] 
        node_continent = []         # TODO: clean node_continent, node_subpops, etc...
        node_subpops = []
        node_phenotypes = {}
        phenotypes_keys = [x for x in individuals_dict[individuals_dict.keys()[0]].keys() if x not in ['name', ]]
        allcontinents = []
        self['phenotypes'] = phenotypes_keys
        self['allphenotype_statuses'] = {}
        for phenotype_key in phenotypes_keys:
            node_phenotypes[phenotype_key] = []
            self['allphenotype_statuses'][phenotype_key] = []

        for i in range(len(genotypes)):
            genotype = genotypes[i]
            individual = individuals[i]
            individual_key = individual.replace('_1', '').replace('_2', '')
            continent = individuals_dict[individual_key]['continent']
            if continent not in allcontinents:
                allcontinents.append(continent)
            subpop = individuals_dict[individual_key]['subpop']
#            print phenotypes_keys
#                node_phenotypes[phenotype_key].append(individuals_dict[individual_key][phenotype_key])

            if genotype not in node_genotypes:
                node_genotypes.append(genotype)
                node_n_datapoints.append(1)
                node_individuals.append(set([individual]))
                node_continent.append(set([continent]))
                node_subpops.append(set([subpop]))
#                for phenotype_key in phenotypes_keys:
#                    node_phenotypes[phenotype_key] = [individuals_dict[individual_key][phenotype_key]]
                for phenotype_key in phenotypes_keys:
                    phenotype_status = individuals_dict[individual_key][phenotype_key]
                    node_phenotypes[phenotype_key].append(set([phenotype_status]))
                    if phenotype_status not in self['allphenotype_statuses'][phenotype_key]:
                       self['allphenotype_statuses'][phenotype_key].append(phenotype_status) 
##                node_techniques.append(set([t for t in techniques]))
            else:
                current_node_index = node_genotypes.index(genotype)
                node_n_datapoints[current_node_index] += 1
                node_individuals[current_node_index].add(individual)
                node_continent[current_node_index].add(continent)
                node_subpops[current_node_index].add(subpop)
                for phenotype_key in phenotypes_keys:
                    phenotype_status = individuals_dict[individual_key][phenotype_key]
                    node_phenotypes[phenotype_key][current_node_index].add(phenotype_status)
                    if phenotype_status not in self['allphenotype_statuses'][phenotype_key]:
                       self['allphenotype_statuses'][phenotype_key].append(phenotype_status) 
#                for phenotype_key in phenotypes_keys:
#                    node_phenotypes[phenotype_key].append(individuals_dict[individual_key][phenotype_key])
##                    node_phenotypes[phenotype_key] = individuals_dict[individual_key][phenotype_key]
##                node_techniques[current_node_index].update(set([t for t in techniques]))
#            print genotype, node_phenotypes

        self.add_vertices(len(node_genotypes))
        self['allcontinents'] = allcontinents
        self.vs['genotype'] = node_genotypes
        self.vs['n_datapoints'] = node_n_datapoints
        try:
            self.vs['value'] = [int(n, base=2) for n in node_genotypes]
        except ValueError:
            raise GenotypeNetworkInitError("something went wrong when converting genotypes to binary strings. Check if any SNP is triallelic")
        self.vs['node_individuals'] = [list(n) for n in node_individuals]
        self.vs['continent'] = [list(n) for n in node_continent]
        self.vs['cont_str'] = ['_'.join(conts) for conts in self.vs['continent']]
        self.vs['subpop'] = [list(n) for n in node_subpops]
        self['allphenotypes_statuses'] = {}
        for phenotype_key in phenotypes_keys:
            self.vs[phenotype_key] = [sorted(list(n)) for n in node_phenotypes[phenotype_key]]
#        for phenotype_key in all_phenotypes:


        # Calculate edges
        for genotype1 in self.vs:
#            logging.debug(str((genotype1.index, genotype1['name'], genotype1['value'])))
            for genotype2 in self.vs:
                if genotype1.index >= genotype2.index:
                    pair_distance = '{0:08b}'.format(genotype1['value']^genotype2['value']).count('1')
                    if pair_distance > 0 and pair_distance <= distance:
#                    print genotype1['name'], genotype2['name'],
#                    print '{:08b}'.format(genotype1['value']^genotype2['value']).count('1')
                        self.add_edge(genotype1.index, genotype2.index)

    def subgraph_by_continent(self, continent_name, n_individuals=0, random_seed=False):
        """
        Create a subgraph of the network by extracing all the individuals belonging to a continent

        This is basically a wrapper for __subgraph_by_continent__, without the need for specifying individuals id manually.

        The parameter "continent_name" can take a few special keywords, to indicate a subset of individuals:
        - continent_name == "global_noAMR" -> all individuals, except Native Americans.
        - continent_name == "global_sub"   -> all individuals, but subsampling based on n_individuals.

                                  x             x      x
        >>> genotypes = ['001', '011', '000', '000', '100', '010']
        >>> individuals = ['HG1', 'HG2', 'HG3', 'HG4', 'HG5', 'HG6']
        >>> individuals_dict = {
        ...             'HG1': {'continent': 'EUR', 'subpop': 'TSC', 'phenotype1': 'good'}, 
        ...             'HG2': {'continent': 'AFR', 'subpop': 'AFR', 'phenotype1': 'good'}, 
        ...             'HG3': {'continent': 'EUR', 'subpop': 'AFR', 'phenotype1': 'bad'}, 
        ...             'HG4': {'continent': 'AFR', 'subpop': 'YRI', 'phenotype1': 'good'}, 
        ...             'HG5': {'continent': 'AFR', 'subpop': 'YRI', 'phenotype1': 'bad'}, 
        ...             'HG6': {'continent': 'AMR', 'subpop': 'AMR', 'phenotype1': 'good'}, 
        ... }
        >>> mynet = GenotypeNetwork(3, name='mynet')
        >>> mynet.populate_from_binary_strings_and_individuals(genotypes=genotypes, individuals=individuals, individuals_dict=individuals_dict)

        >>> AFR_net = mynet.subgraph_by_continent('AFR')
        >>> print AFR_net
        Genotype Network (name = 'mynet_AFR', chromosome lenght = 3, |V| = 3, |E| = 1)

        >>> AFR_net.vs['genotype']
        ['011', '000', '100']
        >>> AFR_net.vs['node_individuals']
        [['HG2'], ['HG4'], ['HG5']]
        >>> AFR_net.vs['continent']
        [['AFR'], ['AFR', 'EUR'], ['AFR']]
        >>> AFR_net.vs['n_datapoints']
        [1, 1, 1]
        
        Note: if you want to select the nodes belonging to a pop manually, use this list comprehension:
        >>> node_indexes = [v.index for v in mynet.vs if 'AFR' in v['continent']]
        >>> print node_indexes
        [1, 2, 3]

        Test: all network attributes should be the same for a network and its subset 
        >>> sorted(AFR_net.attributes()) == sorted(mynet.attributes())
        True

        Test: the same as above, for vertices
        >>> mynet.vertex_attributes() == AFR_net.vertex_attributes()
        True

        Test: select only 2 individuals
        >>> subgraph = mynet.subgraph_by_continent('AFR', random_seed=2, n_individuals=2)
        >>> print [v['genotype'] for v in subgraph.vs()]
        ['011', '000']
        >>> print [v['node_individuals'] for v in subgraph.vs()]
        [['HG2'], ['HG4']]
        >>> print [v['continent'] for v in subgraph.vs()]
        [['AFR'], ['AFR', 'EUR']]

        >>> subgraph = mynet.subgraph_by_continent('AFR', random_seed=10, n_individuals=2)
        >>> print [v['genotype'] for v in subgraph.vs()]
        ['011', '100']


        # Special keywords
        >>> subgraph_AMR = mynet.subgraph_by_continent('AMR')
        >>> print [v['genotype'] for v in subgraph_AMR.vs()]
        ['010']

#        >>> subgraph_AMR = mynet.subgraph_by_continent('global_noAMR')  # global_noAMR keyword not supported in vcf2networks
#        >>> print [v['genotype'] for v in subgraph_AMR.vs()]
#        ['001', '011', '000', '100']
#        >>> subgraph_AMR = mynet.subgraph_by_continent('global_noAMR', random_seed=10, n_individuals=2)
#        >>> print [v['genotype'] for v in subgraph_AMR.vs()]
#        ['001', '100']
        >>> subgraph_AMR = mynet.subgraph_by_continent('global_sub', random_seed=10, n_individuals=2)
        >>> print [v['genotype'] for v in subgraph_AMR.vs()]
        ['011', '010']
        >>> subgraph_AMR = mynet.subgraph_by_continent('global_sub', random_seed=10, n_individuals=30)
        >>> print subgraph_AMR
        None
        """
        subgraph = self.subgraph_by_phenotype('continent', continent_name, n_individuals=n_individuals, random_seed=random_seed)
        return subgraph

    def __subgraph_by_phenotype__(self, nodes, phenotype, phenotype_status, selected_individuals=False):
        """
        subgraph a network by a given phenotype, keeping only the individuals having a given phenotype_status. 
        
        This method is called internally by .subgraph_by_pop
        
        This is designed to subgraph networks that have information on 
            individuals; for subgraphing a normal network, 
            it would be better to use the standard 
            igraph.Graph.subgraph function.
        """
        subgraph = igraph.Graph.subgraph(self, nodes)
#        subgraph.layout_initialized = False
        subgraph.network_properties_calculated = False

        subgraph['name'] = self['name'] + '_' + phenotype_status
#        subgraph['pop'] = continent
#        subgraph['continent'] = continent
        subgraph[phenotype] = phenotype_status
#        print type(subgraph['individuals_dict'])
#        print subgraph['individuals_dict'][0:100]
#        print subgraph['individuals_dict'][-100:]
#        print ast.literal_eval(subgraph['individuals_dict'])
        if isinstance(subgraph['individuals_dict'], str):
#            print subgraph['individuals_dict']
            subgraph['individuals_dict'] = ast.literal_eval(subgraph['individuals_dict'])
#        print type(subgraph['individuals_dict'])
        if selected_individuals is False:
            subgraph_individuals = [ind.replace("'", '') for ind in subgraph['individuals'] if subgraph['individuals_dict'][ind.replace("'", '').replace('_1', '').replace('_2', '')][phenotype] == phenotype_status]
        else:
            subgraph_individuals = [ind.replace("'", '') for ind in selected_individuals]
        subgraph['individuals'] = subgraph_individuals 

        # http://code.activestate.com/recipes/115417-subset-of-a-dictionary/
        subgraph['individuals_dict'] = dict((ind, subgraph['individuals_dict'][ind]) for ind in subgraph_individuals if ind in subgraph['individuals_dict'])
        for node in subgraph.vs:
#            node['node_individuals'] = [ind for ind in node['node_individuals'] if ind in subgraph_individuals]
            node['node_individuals'] = [ind for ind in node['node_individuals'] if ind in subgraph_individuals]
#            print "genotype", node['genotype'], "INds", node['node_individuals']
            node['n_datapoints'] = len(node['node_individuals'])
        return subgraph


    def subgraph_by_phenotype(self, phenotype, phenotype_status, n_individuals=0, random_seed=False):
        """
        Create a subgraph of the network by extracing all the individuals belonging having a given phenotype status

        This is basically a wrapper for __subgraph_by_phenotype__, without the need for specifying individuals id manually.

#        The parameter "continent_name" can take a few special keywords, to indicate a subset of individuals:
#        - continent_name == "global_noAMR" -> all individuals, except Native Americans.
#        - continent_name == "global_sub"   -> all individuals, but subsampling based on n_individuals.

                                  x             x      x
        >>> genotypes = ['001', '011', '000', '000', '100', '010']
        >>> individuals = ['HG1', 'HG2', 'HG3', 'HG4', 'HG5', 'HG6']
        >>> individuals_dict = {
        ...             'HG1': {'continent': 'EUR', 'subpop': 'TSC', 'phenotype1': 'happy'}, 
        ...             'HG2': {'continent': 'AFR', 'subpop': 'AFR', 'phenotype1': 'sad'}, 
        ...             'HG3': {'continent': 'EUR', 'subpop': 'AFR', 'phenotype1': 'happy'}, 
        ...             'HG4': {'continent': 'AFR', 'subpop': 'YRI', 'phenotype1': 'sad'}, 
        ...             'HG5': {'continent': 'AFR', 'subpop': 'YRI', 'phenotype1': 'happy'}, 
        ...             'HG6': {'continent': 'AMR', 'subpop': 'AMR', 'phenotype1': 'happy'}, 
        ... }
        >>> mynet = GenotypeNetwork(3, name='mynet')
        >>> mynet.populate_from_binary_strings_and_individuals(genotypes=genotypes, individuals=individuals, individuals_dict=individuals_dict)

        >>> print mynet.vs['phenotype1']
        [['happy'], ['sad'], ['happy', 'sad'], ['happy'], ['happy']]

        >>> happy_net = mynet.subgraph_by_phenotype('phenotype1', 'happy')
        >>> print happy_net
        Genotype Network (name = 'mynet_happy', chromosome lenght = 3, |V| = 4, |E| = 3)

        >>> happy_net.vs['genotype']
        ['001', '000', '100', '010']
        >>> happy_net.vs['node_individuals']
        [['HG1'], ['HG3'], ['HG5'], ['HG6']]
        >>> happy_net.vs['phenotype1']
        [['happy'], ['happy', 'sad'], ['happy'], ['happy']]
        >>> happy_net.vs['n_datapoints']
        [1, 1, 1, 1]
        >>> happy_net.vs['continent']
        [['EUR'], ['AFR', 'EUR'], ['AFR'], ['AMR']]

        >>> AFR_net = mynet.subgraph_by_phenotype('continent', 'AFR')
        >>> print AFR_net
        Genotype Network (name = 'mynet_AFR', chromosome lenght = 3, |V| = 3, |E| = 1)

        >>> AFR_net.vs['genotype']
        ['011', '000', '100']
        >>> AFR_net.vs['node_individuals']
        [['HG2'], ['HG4'], ['HG5']]
        >>> AFR_net.vs['continent']
        [['AFR'], ['AFR', 'EUR'], ['AFR']]
        >>> AFR_net.vs['n_datapoints']
        [1, 1, 1]
        
        >>> subgraph = mynet.subgraph_by_phenotype('phenotype1', 'happy', random_seed=10, n_individuals=2)
        >>> print [v['genotype'] for v in subgraph.vs()]
        ['001', '010']


        """
#        print [v.attributes() for v in self.vs if 'EUR' in v['continent'] or 'AFR' in v['continent'] or 'ASN' in v['continent']]
        if n_individuals == 0:
            # If n_individuals is 0, select all the individuals from the population.
#            print [v[phenotype] for v in self.vs]
            nodes = [v.index for v in self.vs if phenotype_status in v[phenotype]]
            selected_individuals = False
#            print continent_name, selected_individuals
        else:
            selected_individuals = []
            phenotype_list = []
#            print self[phenotype]
            if phenotype_status == 'global_sub':
                phenotype_list = self['allphenotype_statuses'][phenotype] 
            else: 
                phenotype_list = [phenotype_status]
#            print self['allphenotype_statuses'][phenotype]
#            print phenotype_list
            for ind_key in self['individuals']:
                ind = ind_key.replace('_1', '').replace('_2', '')
                if self['individuals_dict'][ind][phenotype] in phenotype_list:
                    selected_individuals.append(ind_key)


            # subsampling individuals
            if len(selected_individuals) < n_individuals:
                logging.warn(
                    "Not enough individuals in the population to sample (pop: {0}; total individuals: {1}; individuals requested: {2})".format(
                        phenotype_status, len(selected_individuals), n_individuals)
                    )
                return None
            else:
                if random_seed:
                    random.seed(random_seed)
#                random.seed(2)
                random.shuffle(selected_individuals)
                selected_individuals = selected_individuals[:n_individuals]
                nodes = [[v.index for v in self.vs() if ind in v['node_individuals']][0] for ind in selected_individuals]
            
#            print selected_individuals[:4]
#        print pop_individuals
        subgraph = self.__subgraph_by_phenotype__(nodes, phenotype, phenotype_status, selected_individuals=selected_individuals)
        return subgraph

    def csv_report(self, report_attributes = ["name", "continent", "n_snps", "n_genotypes", "n_vertices", "n_edges", "n_components",
                             "diameter", "density", "av_datapoints_per_node", "av_path_length", "av_degree", "max_degree",
                            "av_betweenness", "av_closeness"
                            ]
                       ):
        """
        Print summary statistics for a genotype network

        Example:
        >>> mynet = GenotypeNetwork(chromosome_len=3,  name="Mygene", genotypes=["000", "100","001", "010", "111"])
        >>> print mynet.csv_report()
        Mygene glob 3 5 5 3 2 2 0.3 1.0 1.5 1.2 3 0.6 0.38
        """
#    print network.summary()
        self.__calculate_network_properties__()
#        logging.debug ([(att, att in self.attributes()) for att in report_attributes])
        report_values = [str(self[att]) for att in report_attributes]
        report = ' '.join(report_values)
        return report


    def values_by_node(self, report_attributes=None, header=True):
        """
        Print all the network values, one line per node.

        This function is useful if you want to plot histograms or bloxpot of the 
            property distributions for a network.
        
        >>> phenotype1 = GenotypeNetwork(3, name='phenotype1', genotypes=['011', '010', '000'])
        >>> print (phenotype1.values_by_node()) #doctest: +NORMALIZE_WHITESPACE
        #name       genotype   degree  betweenness  closeness
        phenotype1  010        2       1.0          1.0 
        phenotype1  011        1       0.0          0.6667  
        phenotype1  000        1       0.0          0.6667  

        >>> print (phenotype1.values_by_node(report_attributes=['genotype', 'degree'])) #doctest: +NORMALIZE_WHITESPACE
        #genotype   degree
        010 2   
        011 1   
        000 1   

        """
#        self.__calculate_network_properties__()

        if report_attributes is None:
            report_attributes = ['name', 'genotype', 'degree', 'betweenness', 'closeness']

        if header is True:
            report = "#" + "\t".join(report_attributes) + '\n'
        else:
            report = ""
        for node in self.vs:
            node_id = node.index
            node_attributes = []

            for attribute in report_attributes:
                if attribute in self.vertex_attributes():
                    node_attributes.append(str(round_if_float(node[attribute])))
#                    print node[attribute],
                elif hasattr(self, attribute):
#                elif attribute in ("n_edges", ):
#                    print(attribute, eval("self."+attribute+"()"))
                    node_attributes.append(str(round_if_float(eval("self."+attribute+"()")[node_id])))
#                    print 
                elif attribute in self.attributes():
                    # if the attribute is not relative to the node, look for it 
                    #   in the network attributes.
                    node_attributes.append(str(round_if_float(self[attribute])))
                elif attribute.startswith('network_') and attribute[8:] in self.attributes():
                    # if the attribute name starts with network_ (e.g. network_name), get the network property.
                    node_attributes.append(str(round_if_float(self[attribute[8:]])))
                else:
                    raise GenotypeNetworkAttributeError('attribute "{0}" not found'.format(attribute))
            report += '\t'.join(node_attributes) + '\n'
#            print report_values            
        return report[:-1]

    def plot(self, **args):
        """
        Utility function to plot the Genotype Network.

        This function is a wrapper of the igraph.plot function, except that it plots 
          the network using a standard layout, facilitating the comparison of different networks.

        It accepts all the parameters of igraph.plot, except that some attributes have default values.

        Let's make an example of Genotype Network:

        #doctest: +SKIP
        >> from src.GenotypeNetwork import *

        #doctest: +SKIP
        >> g = debug_GenotypeNetwork()  # this will give an example of GenotypeNetwork, with 4 nodes and 5 individuals

        Plot the network. By default, the genotypes will be used as node labels: #doctest: +SKIP
        >> g.plot()

        Plot the network, using the individuals names instead of the genotypes:  #doctest: +SKIP
        >> g.plot(
        ...        vertex_label=[",".join(v['node_individuals']) for v in g.vs()])

        Plot the network, using individuals as labels, and the number of individuals as node size: #doctest: +SKIP
        >> g.plot(
        ...         vertex_label=[','.join(v['node_individuals']) for v in g.vs()], 
        ...         vertex_size=[len(v['node_individuals']*10) for v in g.vs(), ]


        To save the plot to a file, just pass the parameter "target" #doctest: +SKIP
        >> g.plot(target="mynet.png")
        

        NOTE: the code to calculate node position is actually very inefficient. Applying it to networks larger than 20 SNPs may cause memory errors.
        In this case, it is recommended to call the igraph.plot function directly, giving it the GenotypeNetwork as first argument: #doctest: +SKIP
        >> igraph.plot(g, 
        ...         vertex_label=[','.join(v['node_individuals']) for v in g.vs()], 
        ...         vertex_size=[len(v['node_individuals']*10) for v in g.vs()]
        """

        args.setdefault("vertex_size", 100/self['chromosome_len'])
        args.setdefault('palette', igraph.palettes['red-blue'])
        args.setdefault("vertex_label", self.vs['genotype'])
        args.setdefault("vertex_label_size", 100/self['chromosome_len'])
        args.setdefault("margins", [50,50,50,50])

        if not 'layout' in args:
            if self.layout_initialized is False:
                self.__get_layout__()
            args['layout'] = self.vs['layout']

        igraph.plot(self, **args)
       
def network_from_graphmlz(graphmlfile_path):
    """
    wrapper for network_from_file
    """
    return network_from_file(graphmlfile_path, fileformat='graphmlz')

def network_from_graphml(graphmlfile_path):
    """
    wrapper for network_from_file
    """
    return network_from_file(graphmlfile_path, fileformat='graphml')

def network_from_file(graphmlfile_path, fileformat='graphml'):
    """
    import a GenotypeNetwork from a graphml file.

    The function igraph.load returns a igraph.Graph object, but I want a GenotypeNetwork object, so I need this wrapper function to reconvert.

    Note that this function would work with any format, not only graphml.

    Note2: the returned network has a new attribute, vs['id'], created when the network is converted to graphml in the first place.
    """
    if fileformat == 'graphml':
        loaded_network = igraph.Graph.Read_GraphML(graphmlfile_path)
    elif fileformat == 'graphmlz':
        loaded_network = igraph.Graph.Read_GraphMLz(graphmlfile_path)
    else:
        loaded_network = igraph.load(graphmlfile_path)
    chromosome_len = int(loaded_network['chromosome_len'])

    network = GenotypeNetwork(int(chromosome_len))
    network.add_vertices(loaded_network.vcount())
    network.add_edges(loaded_network.get_edgelist())
    network.layout_initialized = False
    network.network_properties_calculated = False

#    network['individuals'] = 
    for att in loaded_network.attributes():
        current_att = loaded_network[att]
        if att in ('chromosome_len', 'distance_definition'):
            current_att = int(current_att)
        network[att] = current_att
    network['individuals'] = ast.literal_eval(network['individuals'])
#    print network["positions"]
#    network['positions'] = ast.literal_eval(network['positions'])
#    network['chromosomes'] = ast.literal_eval(network['chromosomes'])
#    logging.debug( igraph.Graph.summary(network))
    network['individuals_dict'] = ast.literal_eval(network['individuals_dict'])
    for v_att in loaded_network.vertex_attributes():
        current_vatt = loaded_network.vs[v_att]
        if v_att in ('n_datapoints', ):
            current_vatt = [int(i) for i in current_vatt]
        network.vs[v_att] = current_vatt
#    print loaded_network.es
    for e_att in loaded_network.edge_attributes():
        network.es[e_att] = loaded_network.es[e_att]
    return network
       
def get_y_position(node):
    """
    Given a node, return its y position

    This code is pretty crappy, and it is not efficient for > 20 nodes.

    Parameters:

        * n = node, as a binary string. Trailing 0s are important, 
            for example: '0010' will give different results than '10'

    >>> get_y_position('001')
    -0.5

    >>> get_y_position('010')
    0.5

    >>> get_y_position('100')
    1.5

    >>> get_y_position('11000')
    5.0

    >>> get_y_position('00011')
    -4.0

    >>> get_y_position('01100')
    1.0

    >>> get_y_position('01010')
    0.0

    """

    one_count = node.count('1')

    all_values = kbits(len(node), one_count)
    nodeset_len = len(all_values) 
#    pos_y = -(all_values.index(node) + nodeset_len/2.)
    pos_y = -all_values.index(node) + nodeset_len/2.
#    l = ['01'] * one_count
#    l.extend(['00']*(len(node)-one_count))
#    logging.debug(l)
#    all_values = [''.join(n) for n in itertools.product(*l)]
#    logging.debug( all_values)
#    pos_y = all_values.index(node)

    return pos_y



def kbits(chromosome_len, one_occurrencies):
    """
    Generate all combinations of genotypes of lenght chromosome_len that have one_occurrencies '1's

    Credits: http://stackoverflow.com/questions/1851134/generate-all-binary-strings-of-length-n-with-k-bits-set
    """
    result = []
    for bits in itertools.combinations(range(chromosome_len), one_occurrencies):
        current_str = ['0'] * chromosome_len
        for bit in bits:
            current_str[bit] = '1'
        result.append(''.join(current_str))
    return result

def find_neighbors(genotype, genotypes):
    """
    Determine which genotypes are neighbors of a given genotype

    This function is not implemented yet, but I may use if for parallel calculations.
    """
    pass

def is_neighbor(genotype1, genotype2):
    """
    Determine if two genotypes are neighbors

    Note: in the end this function is not used, but I will keep it here for the doctests.

    >>> is_neighbor('000', '001')
    True
    >>> is_neighbor('001', '000')
    True
    >>> is_neighbor('000', '000')
    False
    >>> is_neighbor('000', '111')
    False
    >>> is_neighbor('0000', '111')
    False
    >>> is_neighbor('0001', '0010')
    False
    >>> is_neighbor('0000', '10')
    True

    """
    return '{0:08b}'.format(int(genotype1, base=2)^int(genotype2, base=2)).count('1') == 1

def random_genotype_network(chromosome_len, sample_size, max_variation=None, seed=None):
    """
    Generate a random genotype network, for debugging purposes

    Note: this is a quick and dirty function, and some nodes may be duplicated

    >>> net = random_genotype_network(10, 150, 2**10-1, 10)
    >>> print net.summary() #doctest: +NORMALIZE_WHITESPACE
    140 nodes, 96 edges, undirected
    <BLANKLINE>
    Number of components: 50
    Diameter: 13
    Density: 0.0099
    Average path length: 4.0907

    """
    if max_variation is None:
        max_variation = 2 ** chromosome_len - 1
    if seed is not None:
        random.seed(seed)
    genotype_format = "{0:0" + str(chromosome_len) + "b}"
    genotypes = [genotype_format.format(random.randint(0, max_variation)) for i in range(sample_size)]                
    network = GenotypeNetwork(chromosome_len, genotypes=genotypes)
    return(network)

def get_mean(numbers):
    """
    Calculate mean of a list of numbers, as silly python doesn't have this function by default (and I don't want to import numpy)
    >>> get_mean((1, 3))
    2.0
    >>> print get_mean(())
    nan
    """
    if len(numbers) > 0:
        return round((1.0 * sum(numbers) / len(numbers)), 4)
    else:
        return numpy.nan

def round_if_float(number):
    """
    if number is a float, round it to 4 decimals

    >>> round_if_float(0.4) == 0.4
    True
    >>> round_if_float("dsada")
    'dsada'
    >>> round_if_float(0.1234567)
    0.1235
    >>> round_if_float(0)
    0
    """
#    print number, type(number)
    if isinstance(number, float):
        return round(number, 4)
    else:
        return number

def get_max(numbers):
    """
    Wrapper for silly python, that returns an error if the max function is called on a empty list

    >>> get_max([1.0,2.0,3.0])
    3.0
    >>> get_max([1,2,3])
    3
    >>> print get_max([])
    None
    """
    if len(numbers) > 0:
        maxvalue = max(numbers)
        if isinstance(maxvalue, float):
            maxvalue = round(maxvalue, 4)
    else:
        maxvalue = None
    return maxvalue


def exampleNetwork():
    """
    An example Genotype Network, window_size 3, n. individuals 5

    """
    genotypes = ['001', '011', '000', '000', '100']
    individuals = ['HG1', 'HG2', 'HG3', 'HG4', 'HG5']
    individuals_dict = {
         'HG1': {'continent': 'EUR', 'subpop': 'TSC', 'phenotype1': 'good'}, 
         'HG2': {'continent': 'AFR', 'subpop': 'AFR', 'phenotype1': 'bad'}, 
         'HG3': {'continent': 'EUR', 'subpop': 'AFR', 'phenotype1': 'good'}, 
         'HG4': {'continent': 'AFR', 'subpop': 'YRI', 'phenotype1': 'good'}, 
         'HG5': {'continent': 'AFR', 'subpop': 'YRI', 'phenotype1': 'good'}, 
         }
    mynet = GenotypeNetwork(3, name='mynet')
    mynet.populate_from_binary_strings_and_individuals(genotypes=genotypes, individuals=individuals, individuals_dict=individuals_dict)
    return mynet

def exampleNetworkBig():
    """
    A more complex example of Genotype Network

    """
    name = "diploid_network"
    chromosome_len = 7
    genotypes =   [
            '0000000',    
            '0001000',   
            '1000000',   
            '0000001',   
            '0000010',   
            '0001010',   
            '1000111',   
            '0111110',   
            '0101110',   
            '0100110',
            '0100011',
            '0100010',
            '0101010',
            '0111010',
            '0000100',
            '0100000',
            '0001010',
            '1010101']
                
    individuals = ['HG' + str(i/2) + '_' + str((i%2)+1) for i in range(len(genotypes))]
    individuals_dict = {
                    'HG0': {'continent': 'EUR', 'subpop': 'TSC', 'phenotype1': 'good'}, 
                    'HG1': {'continent': 'EUR', 'subpop': 'TSC', 'phenotype1': 'good'}, 
                    'HG2': {'continent': 'EUR', 'subpop': 'GBR', 'phenotype1': 'bad'}, 
                    'HG3': {'continent': 'AFR', 'subpop': 'AFR', 'phenotype1': 'bad'}, 
                    'HG4': {'continent': 'AFR', 'subpop': 'YRI', 'phenotype1': 'good'}, 
                    'HG5': {'continent': 'AFR', 'subpop': 'YRI', 'phenotype1': 'good'}, 
                    'HG6': {'continent': 'AFR', 'subpop': 'YRI', 'phenotype1': 'good'}, 
                    'HG7': {'continent': 'AFR', 'subpop': 'YRI', 'phenotype1': 'bad'}, 
                    'HG8': {'continent': 'EUR', 'subpop': 'GBR', 'phenotype1': 'neutral'}, 
    }

    mynet = GenotypeNetwork(7, name='mynet')
    mynet.populate_from_binary_strings_and_individuals(genotypes=genotypes, individuals=individuals, individuals_dict=individuals_dict)
    return mynet

def plot_ExampleBig():
    g = exampleNetworkBig()
    g.__get_layout__()
    igraph.plot(g, layout=g.vs['layout'], vertex_size=60, vertex_label=g.vs['genotype'], vertex_shape='rectangle')



if __name__ == '__main__':
#    import logging
    import doctest
#    logging.basicConfig(level=logging.DEBUG)
    doctest.testmod()

