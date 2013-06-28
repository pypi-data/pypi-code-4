# -*- coding: utf-8 -*-
"""
===================================================
Algorithms for Viral Quasispecies Mass Spec Studies
===================================================
"""

__all__ = []

__author__ = ["Nicholas Mancuso (nick.mancuso@gmail.com)",
              "Olga Glebova (glebovaov@gmail.com)",
              "Blanche Temate (charly.blanche.t@gmail.com"]

#   Copyright (C) 2011-2012 by
#   Nicholas Mancuso <nick.mancuso@gmail.com>
#   Bassam Tork <basamt@gmail.com>
#   Olga Glebova <glebovaov@gmail.com>
#   Blanche Temate <charly.blanche.t@gmail.com>
#   All rights reserved.
#   BSD license.
import networkx as netx


def peak_frequency_em(peaks, quasispecies, epsilon=0.001):
    """ Expectation Maximization algorithm for calculating quasispecies
        frequencies in mass spectrometry peaks.

        Parameters
        ----------
        peaks : dict
            Dictionary of 'peaks' and their height values.

        quasispecies : dict
            Dictionary of quasispecies and their respective set of peaks.

        epsilon : float (optional, default=0.001)
            Stopping criterion for EM algorithm.

        Returns
        -------
        quasi_freq : dict
            Dictionary of quasispecies and their respective frequencies.
    """
    # we represent the model as a bipartite graph by giving nodes 'color' we
    # can easily use bipartite functions to determine what partition the node
    # belongs to
    em_graph = netx.Graph()

    # helper functions for frequency, probability, and counts
    def _get_quasifreq(qsps):
        return em_graph.node[qsps]["freq"]

    def _set_quasifreq(qsps, freq):
        em_graph.node[qsps]["freq"] = freq

    def _get_peakheight(peak):
        return em_graph.node[peak]["height"]

    def _get_p(qsps, peak):
        return em_graph[qsps][peak]["prob"]

    def _set_p(qsps, peak, prob):
        em_graph[qsps][peak]["prob"] = prob

    # add peak nodes and observed height
    for peak in peaks:
        em_graph.add_node(peak, height=peaks[peak], color=0)

    init_f = 1.0 / len(quasispecies)
    for qsps in quasispecies:
        em_graph.add_node(qsps, color=1, freq=init_f)
        for peak in quasispecies[qsps]:
            em_graph.add_edge(qsps, peak)

    freqs = {qsps: _get_quasifreq(qsps) for qsps in quasispecies}
    while True:
        # E step
        for qsps in quasispecies:
            f_qsps = _get_quasifreq(qsps)
            for peak in em_graph.neighbors(qsps):
                total_f = sum(_get_quasifreq(nbr) \
                            for nbr in em_graph.neighbors(peak))
                _set_p(qsps, peak, f_qsps / total_f)

        # M step
        for qsps in quasispecies:
            total_p = sum(_get_p(qsps, r) * _get_peakheight(r) \
                        for r in em_graph.neighbors(qsps))
            qfreq = total_p / sum(_get_peakheight(r) \
                                for r in em_graph.neighbors(qsps))
            _set_quasifreq(qsps, qfreq)

        delta_f = sum((_get_quasifreq(qsps) - freqs[qsps]) ** 2.0 \
                    for qsps in quasispecies)
        if delta_f < epsilon:
            break

        freqs = {qsps: _get_quasifreq(qsps) for qsps in quasispecies}

    total_f = sum(freq for freq in freqs.values())
    return {qsps: freq / total_f for qsps, freq in freqs.items()}
