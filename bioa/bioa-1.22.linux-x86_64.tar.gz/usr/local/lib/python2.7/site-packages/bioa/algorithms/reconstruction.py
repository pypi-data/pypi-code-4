# -*- coding: utf-8 -*-
"""
================================================
Algorithms for Viral Quasispecies Reconstruction
================================================
"""

__all__ = ["frequency_em",
           "max_bandwidth_strategy",
           "random_bandwidth_strategy",
           "max_frequency_strategy",
           "greedy_fork_resolution",
           "random_fork_resolution",
           "min_forest_fork_resolution",
           "least_squares_fork_balance",
           "min_unsplittable_flows_resolution",
           "amplicon_frequency_matrix_strategy",
           "amplicon_frequency_matrix_strategy_from_graph",
           "update_freq_matrix_from_lp_output"]


__author__ = """Nicholas Mancuso (nick.mancuso@gmail.com)"""
#   Copyright (C) 2011-2012 by
#   Nicholas Mancuso <nick.mancuso@gmail.com>
#   Bassam Tork <basamt@gmail.com>
#   All rights reserved.
#   BSD license.

import math
import collections as coll
import itertools as itools
import logging
import random as rdm
import sys
import bioa
import numpy
import networkx as netx


def frequency_em(graph, quasispecies, epsilon=0.001):
    """ Estimate the quasispecies' frequencies via Expectation Maximization.

    Parameters
    ----------
    graph : ReadGraph
        The read graph used to reconstruct the viral population.

    quasispecies : dict
        The reconstructed quasispecies.

    epsilon : float (optional, default=0.001)
        Threshold for convergence.

    Returns
    -------
    quasispecies : dict
        The reconstructed quasispecies with new frequencies.
    """

    em_graph = netx.Graph()

    # helper functions for frequency, probability, and counts
    def _get_qfreq(qsps):
        return em_graph.node[qsps]["freq"]

    def _set_qfreq(qsps, freq):
        em_graph.node[qsps]["freq"] = freq

    def _get_rfreq(read):
        return em_graph.node[read]["count"]

    def _get_p(qsps, r):
        return em_graph[qsps][r]["p"]

    def _set_p(qsps, r, p):
        em_graph[qsps][r]["p"] = p

    reads = graph.get_read_nodes()
    total_freq = 0.0
    for read in reads:
        freq = graph.get_node_freq(read)
        total_freq += freq
        em_graph.add_node(read, count=freq, color=1)

    init_f = 1.0 / len(quasispecies)
    for qsps in quasispecies:
        em_graph.add_node(qsps, color=0, freq=init_f)
        for read in quasispecies[qsps]:
            if read in [graph.sink, graph.source] \
                    or read not in reads:
                continue
            em_graph.add_edge(qsps, read)

    freqs = {qsps: _get_qfreq(qsps) for qsps in quasispecies}
    while True:
        # E step
        for qsps in quasispecies:
            f_qsps = _get_qfreq(qsps)
            for read in em_graph.neighbors(qsps):
                total_f = sum(_get_qfreq(nbr) for nbr in em_graph.neighbors(read))
                _set_p(qsps, read, f_qsps / total_f)

        # M step
        for qsps in quasispecies:
            total_p = sum(_get_p(qsps, r) * _get_rfreq(r) for r in em_graph.neighbors(qsps))
            qfreq = total_p / sum(_get_rfreq(r) for r in em_graph.neighbors(qsps))
            _set_qfreq(qsps, qfreq)

        delta_f = sum((_get_qfreq(qsps) - freqs[qsps]) ** 2.0 for qsps in quasispecies)
        if delta_f < epsilon:
            break

        freqs = {qsps: _get_qfreq(qsps) for qsps in quasispecies}

    total_f = sum(freq for freq in freqs.values())
    return {qsps: freq / total_f for qsps, freq in freqs.items()}


def amplicon_frequency_matrix_strategy_from_graph(graph, use_chi_sqrd=False):
    """ Reconstructs quasispecies from the supplied graph.

    An amplicon strategy is used to pair reads with one another using a most
    consistent function.

    Parameters
    ----------
    graph : DecliquedAmpliconReadGraph
        Amplicon read graph with fork vertices added.

    use_chi_sqrd : bool (optional, default=False)
        Whether to use the chi squared test in selecting a guide or the
        uniform distribution.

    Returns
    -------
    quasispecies : dict
        Quasispecies spectrum with sequences as keys and frequency as value.
    """
    if not graph:
        raise ValueError("Proper read graph expected!")

    freq_matrix = bioa.FrequencyMatrix(graph.get_amplicons(), True)
    se_positions = graph.get_start_end_positions()
    return _guide_distribution_method(freq_matrix, se_positions, use_chi_sqrd)


def amplicon_frequency_matrix_strategy(amplicons, use_chi_sqrd=False, norm=False):
    """ Reconstructs quasispecies from the supplied read matrix.

    An amplicon strategy is used to pair reads with one another using a most
    consistent function.

    Parameters
    ----------
    amplicons : Amplicons
       Amplicons data-structure where each amplicon is a list of reads. This will
       be used to construct the frequency matrix.

    use_chi_sqrd : bool (optional, default=False)
        Whether to use the chi squared test in selecting a guide or the uniform
        distribution.

    norm : bool (optional, default=False)
        Whether or not to normalize read counts to frequencies.

    Returns
    -------
    quasispecies : dict
        Quasispecies spectrum with sequences as keys and frequency as value.
    """

    if norm:
        freq_matrix = bioa.FrequencyMatrix.construct_normalized_freq_matrix(amplicons, True)
    else:
        freq_matrix = bioa.FrequencyMatrix(amplicons, True)

    return _guide_distribution_method(freq_matrix, amplicons.se_positions, use_chi_sqrd)


def max_bandwidth_strategy(graph, epsilon=1e-3, factor=1.0, until_covered=False, use_em=False):
    """ Finds quasispecies over an amplicon-based read graph by repeatedly
    finding the max bandwidth path until there is no possibly path from the
    source to the sink.

    Parameters
    ----------
    graph : DecliquedAmpliconReadGraph
        Amplicon read graph with fork vertices added.

    freq_name : str (optional, default="count")
        Name of the frequency or count property to use.

    epsilon : float (optional, default=1e-3)
        Threshold for edge values to consider.

    factor : float (optional, default=1.0)
        This is a scaling factor to reduce edge weights by. By default
        it will not change the amount.

    until_covered : bool (optional, default=False)
        Setting 'until_covered' to True will only output the first set
        of quasispecies to cover all edges. Setting to False will output
        the entire set.

    use_em : bool (optional, default=False)
        Determines whether or not to use naive frequency assignment to the
        Quasispecies or to use the Expectation Maximization method.

    Returns
    -------
    quasispecies : dict
        Quasispecies spectrum with sequences as keys and frequency as value.
    """
    if not graph:
        raise ValueError("Non-empty Read-Graph expected!")

    def _max_band(graph):
        """ Find maximum bandwidth s-t path
        """
        source = graph.source
        return bioa.max_bandwidth(graph.graph, source, "count", epsilon)

    return _general_path_resolution(graph, _max_band, factor, until_covered, use_em)


def random_bandwidth_strategy(graph, freq_name="count", epsilon=1e-3, factor=1.0):
    """ Finds quasispecies over an amplicon-based read graph by repeatedly
    finding a random max-bandwidth path until there is no possible path
    from the source to the sink.

    Parameters
    ----------
    graph : DecliquedAmpliconReadGraph
        Amplicon read graph with fork vertices added.

    freq_name : str (optional, default="count")
        Name of the frequency or count property to use.

    epsilon : float (optional, default=1e-3)
        Threshold for edge values to consider.

    factor : float (optional, default=1.0)
        This is a scaling factor to reduce edge weights by. By default it will
        not change the amount.

    Returns
    -------
    quasispecies : dict
        Quasispecies spectrum with sequences as keys and frequency as value.
    """
    if not graph:
        raise ValueError("Non-empty Read-Graph expected!")

    def _rand_path(graph):
        """ Find a random s-t path in the graph such that each edge has at
            least epsilon count over it.
        """
        source = graph.source
        sink = graph.sink
        bwidth = {sink: sys.maxint}
        path = {source: [source]}

        node = source
        while node != sink:

            # filter only valid successors
            choices = [succ for succ in graph.successors(node) \
                        if graph.get_edge_freq(node, succ) > epsilon]

            # return if we are stuck
            if not choices:
                return {}, {}

            # randomly choose a successor
            next_node = rdm.choice(choices)
            count = graph.get_edge_freq(node, next_node)

            # if count is less, set as max bandwidth
            if count < bwidth[sink]:
                bwidth[sink] = count

            # path to next node is the path to current node, plus itself
            path[next_node] = path[node] + [next_node]
            node = next_node

        return bwidth, path

    return _general_path_resolution(graph, _rand_path, factor)


def max_frequency_strategy(graph, epsilon=1e-3, factor=1.0, until_covered=False):
    """ Finds quasispecies over an amplicon-based read graph by repeatedly
    finding a maximum andwidth path until there is no possible path
    from the source to the sink.

    Parameters
    ----------
    graph : DecliquedAmpliconReadGraph
        Amplicon read graph with fork vertices added.

    freq_name : str (optional, default="count")
        Name of the frequency or count property to use.

    epsilon : float (optional, default=1e-3)
        Threshold for edge values to consider.

    factor : float (optional, default=1.0)
        This is a scaling factor to reduce edge weights by. By default
        it will not change the amount.

    until_covered : bool (optional, default=False)
        Setting 'until_covered' to True will only output the first set
        of quasispecies to cover all edges. Setting to False will output
        the entire set.

    Returns
    -------
    quasispecies : dict
        Quasispecies spectrum with sequences as keys and frequency as value.
    """
    if not graph:
        raise ValueError("Non-empty Read-Graph expected!")

    def _max_freq_path(graph):
        """ Find a max-frequency s-t path in the graph such that each edge has
            at least epsilon count over it.
        """
        sink = graph.sink
        source = graph.source
        path = {}
        dist = {source: 0}
        final = {sink: [sink]}

        # since our graph is acyclic and directed (DAG) we can just use
        # topological sort + dynamic programming to solve in linear time.
        for node in netx.topological_sort(graph.graph):
            # if we haven't gotten to this node by now, we can't use it.
            if node not in dist:
                continue

            for next_node in graph.successors(node):
                # if cost to this edge is less than epsilon we can't use it
                ecost = graph.get_edge_freq(node, next_node)
                if ecost < epsilon:
                    continue
                # if the current cost to next_node is less than the cost using
                # (node, next_node) edge replace it
                cost = dist[node] + ecost
                if dist.get(next_node, epsilon) < cost:
                    dist[next_node] = cost
                    path[next_node] = node

        # if the max isn't the sink node, we didnt find a valid path
        if max(dist, key=lambda x: dist[x]) != sink:
            return {}, {}

        node = sink
        while node != source:
            next_node = path[node]
            final[sink].append(next_node)
            node = next_node
        final[sink].reverse()

        return dist, final

    return _general_path_resolution(graph, _max_freq_path, factor, until_covered)


def greedy_fork_resolution(graph, perfect_match=True):
    """ Greedily resolve forks in the read graph.

    Parameters
    ----------
    graph : DecliquedAmpliconReadGraph
        Amplicon read graph with fork vertices added.

    perfect_match : bool (optional, default=True)
        Whether to match values that are equal before considering
        maximums.

    Returns
    -------
    graph : DecliquedAmpliconReadGraph
        Modified read graph with all forks resolved.
    """
    if not graph:
        raise ValueError("Non-empty Read-Graph expected!")

    epsilon = 0.001

    def _find_match(pq, value):
        match = None
        for read, count in pq:
            if math.fabs(value - count) <= epsilon:
                match = read
                break
        if match:
            pq.remove_node(match)

        return match

    def _find_perfect_matches(lpq, rpq, lmax, lread, rmax, rread):
        match_tuple = None
        if lmax >= rmax:
            if math.fabs(lmax - rmax) < epsilon:
                match_tuple = (lread, rread, lmax)
            else:
                match = _find_match(rpq, lmax)
                if match:
                    match_tuple = (lread, match, lmax)
                    rpq.add_node(rmax, rread)
        else:
            if math.fabs(lmax - rmax) < epsilon:
                match_tuple = (lread, rread, rmax)
            else:
                match = _find_match(lpq, rmax)
                if match:
                    match_tuple = (match, rread, rmax)
                    lpq.add_node(lmax, lread)

        return match_tuple

    def _greedy_resolve(lreads, rreads):
        # build max priority queues to get the max count read from
        # both the left reads and the right reads of the biclique
        resolution = []
        lpq = bioa.PQueue(lreads, behave="max")
        rpq = bioa.PQueue(rreads, behave="max")
        # greedily pair up reads, reducing their counts
        while lpq and rpq:
            lread, lmax = lpq.get_max()
            rread, rmax = rpq.get_max()

            if perfect_match:
                match = _find_perfect_matches(lpq, rpq, lmax, \
                            lread, rmax, rread)
                # we found a perfect matchup. continue
                if match:
                    resolution.append(match)
                    continue

            minmax = min([lmax, rmax])
            lmax -= minmax
            rmax -= minmax

            # Considering that the _sum_ of both sides is equal,
            # one, or both, may be exhausted of counts.
            if lmax > 0:
                lpq.add_node(lmax, lread)
            elif rmax > 0:
                rpq.add_node(rmax, rread)

            resolution.append((lread, rread, minmax))

        return resolution

    return _general_fork_resolution(graph, _greedy_resolve)


def random_fork_resolution(graph):
    """ Resolve forks by random matching fork vertices.

    Parameters
    ----------
    graph : DecliquedAmpliconReadGraph
        Amplicon read graph with fork vertices added.

    Returns
    -------
    graph : DecliquedAmpliconReadGraph
        Modified read graph with all forks resolved.
    """
    if not graph:
        raise ValueError("Non-empty Read-Graph expected!")

    def _random_resolve(lreads, rreads):
        # build a set for left and right sides of the fork then randomly select
        # from each set and make an edge until counts are exhausted
        resolution = []
        left = set(lreads)
        right = set(rreads)
        while left and right:
            # randomly pair up reads, reducing their counts
            # the conversion to list is temporary until a better solution
            # is realized.
            lfreq, lread = rdm.choice(list(left))
            rfreq, rread = rdm.choice(list(right))

            left.remove((lfreq, lread))
            right.remove((rfreq, rread))

            minfreq = min([lfreq, rfreq])
            lfreq -= minfreq
            rfreq -= minfreq

            # Considering that the _sum_ of both sides is equal,
            # one, or both, may be exhausted of counts.
            if lfreq > 0:
                left.add((lfreq, lread))
            elif rfreq > 0:
                right.add((rfreq, rread))

            resolution.append((lread, rread, minfreq))

        return resolution

    return _general_fork_resolution(graph, _random_resolve)


def min_forest_fork_resolution(graph):
    """
    """
    try:
        import cplex
    except ImportError:
        raise ImportError(
               "min_forest_fork_resolution() requires cplex: http://cplex.com")

    if not graph:
        raise ValueError("Connected Read Graph required!")

    def _min_forest(lreads, rreads):
        resolution = []

        # w.l.o.g assume |L| <= |R|
        left_smaller = len(lreads) <= len(rreads)
        if left_smaller:
            lfreqset, lreadset = zip(*lreads)
            rfreqset, rreadset = zip(*rreads)
            lset = {lread: lfreq for lfreq, lread in lreads}
            rset = {rread: rfreq for rfreq, rread in rreads}
        else:
            lfreqset, lreadset = zip(*rreads)
            rfreqset, rreadset = zip(*lreads)
            rset = {lread: lfreq for lfreq, lread in lreads}
            lset = {rread: rfreq for rfreq, rread in rreads}

        lreadset = list(lreadset)
        rreadset = list(rreadset)

        model = cplex.Cplex()
        model.objective.set_sense(model.objective.sense.minimize)
        model.set_problem_type(model.problem_type.LP)
        # suppress outputs
        model.set_results_stream(None)
        model.set_warning_stream(None)
        model.set_error_stream(None)
        model.set_log_stream(None)

        # variables are over edges and over balance of a root
        edge_map = {str((lread, rread)): (lread, rread) for lread in lreadset \
                        for rread in rreadset}
        edge_variables = edge_map.keys()
        # add the objective (minimize residuals)
        var_types = [model.variables.type.binary] * len(edge_variables)
        model.variables.add(names=edge_variables, types=var_types)

        # add the absolute value of the total balance of a tree variables
        lower_bs = [0.0] * len(lreadset)
        var_types = [model.variables.type.continuous] * len(lreadset)
        model.variables.add(names=lreadset, lb=lower_bs, types=var_types)

        # objective is to minimize the sum of the absolute value balances
        model.objective.set_linear([(lread, 1.0) for lread in lreadset])
        model.objective.set_linear([(edge, 0.0) for edge in edge_variables])

        # add the constraint to only allow larger-side reads a single parent
        # \sum_i^L x_{ij} = 1 \forall j \in R
        for rread in rreadset:
            edge_vars = [str((lread, rread)) for lread in lreadset]
            coefficients = [1.0] * len(lreadset)
            lhs = cplex.SparsePair(edge_vars, coefficients)
            model.linear_constraints.add(lin_expr=[lhs], senses=["L"], \
                                         rhs=[2.0])

        # add the constraints to find absolute value of the balance of a root
        # \sum_j^R r_j * x_{ij} - l_i <= y_i \forall i \in L
        # l_i - \sum_j^R r_j x_{ij} <= y_i \forall i \in L
        for lread in lreadset:
            lfreq = lset[lread]
            # first way
            edge_vars = [str((lread, rread)) for rread in rreadset]
            coefficients = [rfreq for rfreq in rfreqset]
            lhs = cplex.SparsePair(edge_vars + [lread], coefficients + [-1.0])
            model.linear_constraints.add(lin_expr=[lhs], senses=["L"], \
                                         rhs=[lfreq])
            # then the other
            coefficients = [-rfreq for rfreq in rfreqset]
            lhs = cplex.SparsePair(edge_vars + [lread], coefficients + [-1.0])
            model.linear_constraints.add(lin_expr=[lhs], senses=["L"], \
                                         rhs=[-lfreq])

        model.solve()
        # the model will solve which edges to choose, but we must still
        # calculate the frequency to place over each edge. While a tree
        # solution will be unique, if balancing is not done to graph beforehand
        # we may have # negative assignments. Therefore, we will assign as a
        # ratio.
        for edge, selected in zip(edge_variables, model.solution.get_values()):
            if not selected:
                continue
            left, right = edge_map[edge]
            lfreq = lset[left]
            rfreq = rset[right]
            freq = rfreq / lfreq
            # the resolution needs to be in actual left-right order
            if left_smaller:
                resolution.append((left, right, freq))
            else:
                resolution.append((right, left, freq))

        return resolution

    return _general_fork_resolution(graph, _min_forest)


def min_unsplittable_flows_resolution(graph, flow_num, nthreads=0, timeout=300,
        threshold=1e-5):
    """ Min-k unsplittable flows method.
    This tries to find k paths in the graph that cover the reads with minimum
    amount of flow.

    Parameters
    ----------
    graph : DecliquedAmpliconReadGraph
        Amplicon read graph with fork vertices added.

    flow_num : int
        The number of paths to try.

    nthreads : int, optional default=0
        The number of threads to use.
        0 = Use maximum number of threads (i.e. CPUs)
        1 = Single Threaded
        n = Use n threads

    timeout : int, optional default=300
        The number of seconds to run cplex until timeout.

    threshold : float, optional default=1e-5
        The threshold for determining a variable being selected or not.

    Returns
    -------
    quasispecies : dict
        Quasispecies spectrum with sequences as keys and frequency as value.

    Notes
    -----
    Requires CPLEX and CPLEX Python module to be installed. http://www.cplex.com
    """
    try:
        import cplex
    except ImportError:
        raise ImportError(
               "min_unsplittable_flows_resolution() requires cplex: http://cplex.com")

    if not graph:
        raise ValueError("Connected Read Graph required!")
    if flow_num < 1:
        raise ValueError("Flow must be positive integer!")
    if nthreads < 0:
        raise ValueError("Number of threads must be at least 0" +\
                " (for default behavior)")
    if timeout < 1:
        raise ValueError("Timeout must be positive value!")


    # keep caches of variables for faster constraint building
    # helper functions to access constraints
    pred_cache = {}
    succ_cache = {}
    def pred_node_vars(flow, node, name_func):
        key = name_func((flow, node))
        if key not in pred_cache:
            edges = itools.product([flow], \
                        itools.product(graph.graph.predecessors(node), [node]))
            pred_cache[key] = map(name_func, edges)
        return pred_cache[key]

    def succ_node_vars(flow, node, name_func):
        key = name_func((flow, node))
        if key not in succ_cache:
            edges = itools.product([flow], \
                    itools.product([node], graph.graph.successors(node)))
            succ_cache[key] = map(name_func, edges)
        return succ_cache[key]

    logging.debug("Building MCF model")
    model = cplex.Cplex()
    model.set_problem_type(model.problem_type.MILP)
    # suppress outputs
    model.set_results_stream(None)
    model.set_warning_stream(None)
    model.set_error_stream(None)
    # set parameters
    model.parameters.threads.set(nthreads)
    model.parameters.timelimit.set(timeout)

    # add t-s edge to make into circulation problem
    source, sink = graph.source, graph.sink
    graph.add_edge(sink, source, 0)

    # just re-use this list
    edges = graph.graph.edges()

    # add the binary flow variables
    flow_range = range(flow_num)
    bin_var_name = str
    bvariables = map(bin_var_name, itools.product(flow_range, edges))
    var_types = [model.variables.type.binary] * len(bvariables)
    model.variables.add(names=bvariables, types=var_types)

    # add the real-valued flow variables
    frac_var_name = lambda x: "{0}*".format(x)
    variables = map(frac_var_name, itools.product(flow_range, edges))
    var_types = [model.variables.type.continuous] * len(variables)
    lbounds = [0.0] * len(variables)
    ubounds = [1.0] * len(variables)
    model.variables.add(names=variables, lb=lbounds, ub=ubounds, types=var_types)

    # objective is to minimize the sum of the flows
    obj_edge = itools.product(flow_range, [(sink, source)])
    #obj_bvars = itools.imap(lambda x: (bin_var_name(x), 0.0), obj_edge)
    obj_vars = itools.imap(lambda x: (frac_var_name(x), 1.0), obj_edge)
    model.objective.set_linear(list(itools.chain(obj_vars)))
    model.objective.set_sense(model.objective.sense.minimize)

    # constraint 1 is to cover all edges in decliqued graph
    for node, next_node in edges:
        e_variables = map(frac_var_name, itools.product(flow_range, \
                        [(node, next_node)]))
        coefficients = [1.0] * len(e_variables)
        lhs = cplex.SparsePair(e_variables, coefficients)
        freq = graph.get_edge_freq(node, next_node)
        model.linear_constraints.add(lin_expr=[lhs], senses=["G"], rhs=[freq])

    # constraint 2 is to make sure that flows conserved
    for flow, node in itools.product(flow_range, graph):
        in_variables = pred_node_vars(flow, node, bin_var_name)
        out_variables = succ_node_vars(flow, node, bin_var_name)
        in_coefficients = [1.0] * len(in_variables)
        out_coefficients = [-1.0] * len(out_variables)
        lhs = cplex.SparsePair(in_variables + out_variables, \
                in_coefficients + out_coefficients)
        model.linear_constraints.add(lin_expr=[lhs], senses=["E"], rhs=[0.0])

    for flow, node in itools.product(flow_range, graph):
        in_variables = pred_node_vars(flow, node, frac_var_name)
        out_variables = succ_node_vars(flow, node, frac_var_name)
        in_coefficients = [1.0] * len(in_variables)
        out_coefficients = [-1.0] * len(out_variables)
        lhs = cplex.SparsePair(in_variables + out_variables, \
                in_coefficients + out_coefficients)
        model.linear_constraints.add(lin_expr=[lhs], senses=["E"], rhs=[0.0])

    # constraint 3 is to select binary flows
    for flow, edge in itools.product(flow_range, edges):
        bin_var = bin_var_name((flow, edge))
        var = frac_var_name((flow, edge))
        lhs = cplex.SparsePair([bin_var, var], [1.0, -1.0])
        model.linear_constraints.add(lin_expr=[lhs], senses=["G"], rhs=[0.0])

    # constraint 4 is to make flows unsplittable
    for flow, node in itools.product(flow_range, graph):
        out_variables = succ_node_vars(flow, node, bin_var_name)
        out_coefficients = [1.0] * len(out_variables)
        lhs = cplex.SparsePair(out_variables, out_coefficients)
        model.linear_constraints.add(lin_expr=[lhs], senses=["L"], rhs=[1.0])

    con_num = model.linear_constraints.get_num()
    bin_num = model.variables.get_num_binary()
    frac_num = model.variables.get_num_semicontinuous()
    log_str = "MCF model has {} constraints".format(con_num)
    log_str += ", {} binary variables".format(bin_num)
    log_str += ", and {} semicontinuous variables".format(frac_num)
    logging.debug(log_str)

    model.solve()
    #values = dict(zip(bvariables, model.solution.get_values(bvariables)))
    fvalues = dict(zip(variables, model.solution.get_values(variables)))
    flow_paths = coll.defaultdict(list)
    flow_vals = coll.defaultdict(float)
    tflow = 0.0

    # remove dummy edge
    graph.remove_edge(sink, source)
    bfs_edges = list(netx.bfs_edges(graph.graph, graph.source))
    for flow, edge in itools.product(flow_range, bfs_edges):
        # if we've selected this edge for the kth flow AND it has actual flow value
        if fvalues[frac_var_name((flow, edge))] > threshold:
            u, v = edge
            if u == graph.source:
                tflow += fvalues[frac_var_name((flow, edge))]
                flow_vals[flow] += fvalues[frac_var_name((flow, edge))]
            flow_paths[flow].append(graph.get_node_read(v))

    final = dict([])
    for i, flow in enumerate(flow_vals):
        if flow_vals[flow] == 0.0:
            continue
        qs = bioa.reconstruct_sequence(flow_paths[flow], \
                graph.get_start_end_positions())
        final[qs] = flow_vals[flow] / tflow
        log_str = "Variant {0} has length {1} and frequency {2}"
        log_str = log_str.format(i, len(qs), final[qs])
        logging.debug(log_str)

    logging.debug("MCF found {} total variants".format(len(final)))
    return final


def least_squares_fork_balance(graph, weighted=False):
    """ Balance all forks in the graph by a least squares approach.

    Parameters
    ----------
    graph : DecliquedAmpliconReadGraph
        Amplicon read graph with fork vertices added.

    weighted : bool (optional, default=False)
        Whether or not to calculate weighted least squares or
        ordinary least squares.

    Returns
    -------
    balanced_graph : DecliquedAmpliconReadGraph
        Amplicon read graph with all forks balanced.

    Notes
    -----
    This function requires cplex to be installed in order to work.
    http://cplex.com
    """
    try:
        import cplex
    except ImportError:
        raise ImportError(
                "least_sqares_fork_balance() requires cplex: http://cplex.com")

    if not graph:
        raise ValueError("Connected Read Graph required!")

    model = cplex.Cplex()
    model.objective.set_sense(model.objective.sense.minimize)
    model.set_problem_type(model.problem_type.QP)
    # suppress outputs
    model.set_results_stream(None)
    model.set_warning_stream(None)
    model.set_error_stream(None)
    model.set_log_stream(None)

    source = graph.source
    sink = graph.sink
    reads, forks = graph.get_read_and_fork_nodes()
    forks = forks - set([source, sink])

    # variables are over reads
    variables = map(str, reads)

    # add the objective (minimize residuals)
    lower_bs = [-graph.get_node_freq(read) for read in reads]
    upper_bs = [cplex.infinity] * len(reads)
    model.variables.add(names=variables, lb=lower_bs, ub=upper_bs)

    if not weighted:
        coefficients = [(var, var, 1.0) for var in variables]
    else:
        scale_coeffics = [1.0 / graph.get_node_freq(read) for read in reads]
        coefficients = [(var, var, coef) for var, coef in \
                            zip(variables, scale_coeffics)]

    model.objective.set_quadratic_coefficients(coefficients)

    # add balance constraint
    for fork in forks:
        preds = graph.predecessors(fork)
        succs = graph.successors(fork)

        b_vars = []
        coefficients = ([1.0] * len(preds)) + ([-1.0] * len(succs))
        tally = 0.0
        for pred in preds:
            freq = graph.get_node_freq(pred)
            b_vars.append(str(pred))
            tally -= freq

        for succ in succs:
            freq = graph.get_node_freq(succ)
            b_vars.append(str(succ))
            tally += freq

        lhs = cplex.SparsePair(b_vars, coefficients)
        model.linear_constraints.add(lin_expr=[lhs], senses=["E"], rhs=[tally])

    # readjust graph
    model.solve()
    for read, offset in zip(variables, model.solution.get_values()):
        freq = graph.get_node_freq(read)
        graph.set_node_freq(read, freq + offset)

    return graph


def update_freq_matrix_from_lp_output(freq_matrix, filename, rounding=False):
    """ Updates the frequency matrix from the output of a balancing scheme.

    Parameters
    ----------
    read_matrix : Numpy matrix
        Numpy matrix or list of lists of actual reads for each amplicon.
        This will be used to construct the frequency matrix.

    filename : str
        Path to the file that contains the least squares output from a
        solver.

    rounding : bool (optional, default=False)
        Whether or not to round the results for each read frequency.

    Returns
    -------
    updated_frequency_matrix : Numpy matrix
        The frequency matrix with updated counts.

    Notes
    -----
    This should be deprecated in order to use to use a newer direct solver
    based approach.
    """
    def _parse_coord(strcoord):
        inner = strcoord[1:-1]
        split = inner.split(",")
        assert len(split) == 2, "Invalid coordinate!"
        return int(split[0]), int(split[1])

    with open(filename, "r") as file:
        for line in file:
            items = line.split("  ")
            length = len(items) - 1
            for idx in range(length):
                i, c = _parse_coord(items[idx])
                offset = float(items[idx + 1])
                freq_matrix[i][c][1] += offset

    if rounding:
        pass

    return freq_matrix


# Lets keep the internal functions here
def _general_path_resolution(graph, path_finder, factor=1.0, until_covered=False, use_em=False):
    """ This is our general algorithm to resolve paths.

    It will call the resolver function to get the pair: bandwidths and paths.
    The count of all edges in the source-sink path will be reduced by the
    bandwidth returned by the resolution function. This continues until no
    non-zero paths are left.

    Parameters
    ----------
    graph : DecliquedAmpliconReadGraph
        Amplicon read graph with fork vertices added.

    path_finder : function
        Function that takes a graph. It should find a source-sink path in
        the graph. It returns a pair of dictionaries. The first is the
        bandwidth dictionary. It should accept at least the sink node as a
        key, returning the bandwidth of the source-sink path. The second is
        the path dictionary. It should at least accept the sink node as a
        key, return a list of nodes indicating the source-sink path.

    factor : float (optional, default=1.0)
        This is a scaling factor to reduce edge weights by. By default
        it will not change the amount.

    until_covered : bool (optional, default=False)
        Setting 'until_covered' to True will only output the first set
        of quasispecies to cover all edges. Setting to False will output
        the entire set.

    use_em : bool (optional, default=False)
        Determines whether or not to use naive frequency assignment to the
        Quasispecies or to use the Expectation Maximization method.

    Returns
    -------
    quasispecies : dict
        Quasispecies spectrum with sequences as keys and frequency
        as value.
    """
    quasispecies = coll.defaultdict(float)
    path_list = []
    qsps_path = {}
    final = {}
    total = 0.0
    sink = graph.sink
    se_positions = graph.get_start_end_positions()

    func_name = path_finder.__name__
    log_str = "Running generalized path-strategy with {0} as path-finder"
    log_str = log_str.format(func_name)
    logging.info(log_str)
    # We repeatedly get an s-t path and use that as a quasispecies until there
    # are no valid paths from the source to the sink
    while True:
        costs, paths = path_finder(graph)

        # there must exist a path from source -> sink to continue
        if sink not in costs:
            break

        cost = costs[sink]
        path = paths[sink]

        reads = (graph.get_node_read(node) for node in path)

        # join the reads and add to quasispecies list
        qs = bioa.reconstruct_sequence(reads, se_positions)
        quasispecies[qs] += cost

        total += cost

        # reduce the frequency of the path after our selection
        edge_set = set([])
        for idx, v in enumerate(path[:-1]):
            nextn = path[idx + 1]
            edge_set.add((v, nextn))
            e_freq = graph.get_edge_freq(v, nextn)
            graph.set_edge_freq(v, nextn, e_freq - (cost * factor))

        qsps_path[qs] = path
        path_list.append((cost, edge_set, qs))

    # the user may only want to output the first subset of quasispecies
    # that cover all edges rather than the entire set.
    if until_covered:
        total = 0.0
        nquasispecies = coll.defaultdict(float)
        edges = set(graph.graph.edges())
        path_list.sort(key=lambda trip: trip[0])
        while edges and path_list:
            path_trip = path_list.pop()
            edges = edges - path_trip[1]
            qs = path_trip[2]
            nquasispecies[qs] += path_trip[0]
            total += path_trip[0]

        # remove the qsps we didnt use from the path dict for EM
        for path_trip in path_list:
            # if factor < 1 there may be duplicates
            if path_trip[2] in qsps_path:
                del qsps_path[path_trip[2]]

        quasispecies = nquasispecies

    # normalize the bandwidths to be frequencies
    logging.debug("{0} found {1} variants".format(func_name, len(quasispecies)))
    if use_em:
        final = frequency_em(graph, qsps_path)
    else:
        i = 0
        for qs in quasispecies:
            freq = quasispecies[qs]
            final[qs] = freq / total
            log_str = "Variant {0} has length {1} and frequency {2}"
            log_str = log_str.format(i, len(qs), final[qs])
            logging.debug(log_str)
            i += 1

    return final


def _general_fork_resolution(graph, resolver):
    """ This is our general algorithm to resolve forks. It will continually
        call the resolver function on each fork until no forks exist in the
        graph.

    Parameters
    ----------
    graph : DecliquedAmpliconReadGraph
        Amplicon read graph with fork vertices added.

    resolver : function
        Function that takes a fork predecessor read/freq pairs,
        and successor read/freq pairs. It should return the resolution in
        list form as (lread, rread, freq) tuples.

    Returns
    -------
    graph : DecliquedAmpliconReadGraph
        Modified read graph with all forks resolved.
    """
    def _get_read_pairs(graph, func):
        """ This will return a list of (freq, read) pairs depending on the
            function used
        """
        return [(graph.get_node_freq(rd), rd) for rd in func(fork)]

    while True:
        forks = graph.get_forks()
        if not forks:
            break

        for fork in forks:
            # get the precessor and successor reads of the fork
            lreads = _get_read_pairs(graph, graph.predecessors)
            rreads = _get_read_pairs(graph, graph.successors)

            edgelist = resolver(lreads, rreads)
            for lread, rread, freq in edgelist:
                graph.split_edge(fork, lread, rread, freq)

            graph.remove_node(fork)

            reads = [r for f, r in lreads] + [r for f, r in rreads]
            graph.remove_nodes_from(reads)

    return graph


def _guide_distribution_method(freq_matrix, se_positions, use_chi_sqrd):
    """
    """

    total = 0.0
    quasispecies = {}
    variants = {}
    row, col = freq_matrix.shape
    read_count = row * col
    examined = {}

    # just shortcircuit here if no columns to check.
    if col == 0:
        return {}

    while True:
        guide = _choose_guide(freq_matrix, use_chi_sqrd)

        # matching with other amplicons
        for gdx, gpair in enumerate(freq_matrix[guide]):
            gread, gfreq = gpair
            examined[(guide, gdx)] = True

            # we cannot use this read
            if gfreq == 0:
                continue

            start, end = se_positions[guide]
            if guide != 0:
                lstart, lend = se_positions[guide - 1]
                overlap = lend - start
            else:
                # doesnt matter it wont be used
                overlap = 0

            # match to the "left" of the amplicon
            lreads = _find_reads(gread, gdx, reversed(freq_matrix[:guide]), \
                        overlap, examined, swap_compare=True)
            lreads.reverse()
            lreads.append((gread, gdx))

            if guide != len(freq_matrix) - 1:
                rstart, rend = se_positions[guide + 1]
                overlap = end - rstart
            else:
                # doesnt matter it wont be used
                overlap = 0

            # match to the "right" of the amplicon
            rreads = _find_reads(gread, gdx, freq_matrix[guide + 1:], \
                        overlap, examined)
            lreads.extend(rreads)

            # we should have a read from each amplicon
            if len(lreads) == len(freq_matrix):
                # this unzips the list and gives us
                # the list of reads and list of indices
                reads, idxs = zip(*lreads)

                # create the variant, add it to the list,
                # and update the frequency matrix
                quasispecies[bioa.reconstruct_sequence(reads, se_positions)] = gfreq
                _update_freq_matrix(freq_matrix, idxs, gfreq)
                total += gfreq

        # if a column is empty, we"ve exhausted our possiblities
        # and should finish, or if all items have been examined
        # we should finish.
        if _has_empty_column(freq_matrix) or len(examined) == read_count:
            break

    for qs, freq in quasispecies.items():
        variants[qs] = freq / total

    return variants


def _has_empty_column(freq_matrix):
    """ Determines if the frequency matrix has a column of all zeros.

    Parameters
    ----------
    freq_matrix : numpy matrix
        The frequency matrix over the reads.

    Returns
    -------
    contains_empty_column : bool
            True if the matrix contains a column of all zeros. False otherwise.
    """

    func = lambda x, y: x and y
    exhausted = False
    for col in freq_matrix:
        if not reduce(func, [f for r, f in col]):
            exhausted = True
            break
    return exhausted


def _update_freq_matrix(freq_matrix, indices, freq):
    """
    This updates the frequency matrix by subtracting the supplied frequency from
    the found reads.

    Parameters
    ----------

    freq_matrix : bioa.FrequencyMatrix
        The frequency matrix over the reads.

    indices : list
        List of indices where the chosen reads were in the original matrix.

    freq : float
        The frequency to deduct from other reads.

    Returns
    -------
    None
    """

    for cdx, rdx in enumerate(indices):
        read, val = freq_matrix[cdx][rdx]
        val = max([0, val - freq])
        freq_matrix[cdx][rdx] = (read, val)

    return


def _find_reads(seed, seedx, columns, overlap, examined, swap_compare=False):
    """
    Finds all reads over the columns given
    the seed.

    Parameters
    ----------

    seed = The read to begin matching consistent
        reads with.

    seedx = The index of the initial seed.

    columns = List of columns to iterate over,
        searching for reads.

    overlap = The amount that any neighboring reads
        overlap by.

    examined = Boolean dictionary to indicate that we have
        examined a given read.

    swap_compare = Whether or not to swap the order
        of the comparing reads for consistency.

    Returns
    -------

    A list of pairs. The first element of the tuple is the read that is
    consistent with its neighbor. The second item is the index of the found
    read. An empty list is returned if none are found.
    """

    readidxpairs = []
    tmpread = seed
    tmpsdx = seedx
    for cdx, col in enumerate(columns):
        read, idx = _find_consistent_read(tmpread, tmpsdx, cdx, col, \
                        overlap, examined, swap_compare)
        if read != "":
            readidxpairs.append((read, idx))
            tmpread = read
            tmpsdx = idx

    return readidxpairs


def _find_consistent_read(seed, seedx, colidx, column, overlap, \
        examined, swap_compare):
    """ Finds a consistent read given the seed and other columns to search.

    Parameters
    ----------
    seed : str
        The read to match a consistent read with.

    seedx : int
        The index of the seed.

    colidx : int
        The index of the current column in the original frequency matrix.

    column : list
        The current column to iterate over to check for a consistent read.

    overlap : int
        The amount that any neighboring reads overlap by.

    examined : dict
        Boolean dictionary to indicate that we have examined a given read.

    swap_compare : bool
        Whether or not to swap the order of the comparing reads for consistency.

    Returns
    -------
    read_and_position : (str, int)
        The consistent read _in the current_ column, and
        its index. Empty string and -1 if not found.
    """

    read = ""
    mdx = sys.maxint
    tmpmdx = mdx
    ridx = -1
    consistent = False
    for idx, pair in enumerate(column):
        pread, pfreq = pair
        examined[(colidx, idx)] = True
        # if its an empty read, no bother checking for consistency
        if pread == "":
            continue

        # if we are going to the left in the matrix, we need
        # to swap the order in checking consistency
        if swap_compare:
            consistent = bioa.are_consistent(pread, seed, overlap)
        else:
            consistent = bioa.are_consistent(seed, pread, overlap)

        tmpmdx = abs(seedx - idx)
        if consistent and pfreq != 0 and tmpmdx < mdx:
            read = pread
            ridx = idx
            mdx = tmpmdx

    return (read, ridx)


def _choose_guide(freq_matrix, use_chi_sqrd=False):
    """
    Selects a guide amplicon from the read
    matrix. This can be selected by the
    uniform distribution or by maximum likelihood.

    Parameters:

    freq_matrix : bioa.FrequencyMatrix
        Numpy matrix where columns correspond to the absolute frequency
        (i.e. counts) distributions of distinct reads in the amplicons and rows
        correspond to distinct read-representatives with their associated
        frequencies.

    use_chi_sqrd : bool
        Whether to sample using the chi squared distribution or uniform
        distribution.

    Returns
    -------
    index : int
        A guide index.
    """
    def _pcs(ex, obs):
        return ((ex - obs) ** 2.0) / ex if ex != 0.0 else 0.0

    val = 0
    if use_chi_sqrd:
        # perform pearson chi-squared tests for all pairs use the amplicon
        # that has the least sum of all its chi-square tests
        final = numpy.zeros(len(freq_matrix))
        for idx, amp in enumerate(freq_matrix):
            chis = []
            reads, freqs = zip(*amp)
            for namp in freq_matrix:
                nreads, nfreqs = zip(*namp)
                pairs = zip(freqs, nfreqs)
                # $\chi^2 = \sum_i^n \frac{(O_i - E_i)^2}{E_i}$
                chisqr = sum([_pcs(pair[0], pair[1]) for pair in pairs])
                chis.append(chisqr)
            final[idx] = sum(chis)

        val = final.argmin()
    else:
        # just use uniform distribution to choose
        val = numpy.random.randint(0, len(freq_matrix))

    return val
