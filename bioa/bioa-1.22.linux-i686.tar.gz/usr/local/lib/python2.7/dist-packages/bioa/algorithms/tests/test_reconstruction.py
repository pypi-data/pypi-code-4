#!/usr/bin/env python
# -*- coding: utf-8 -*-

from nose.tools import *
import math
import bioa


class TestQuasispeciesReconstruction(object):

    def test_max_bandwidth_strategy(self):
        data = [("abac", 0), ("abac", 0),
                ("cgcg", 3),
                ("gtat", 6), ("gtat", 6)]
        se_pos = [(0, 4), (3, 7), (6, 10)]
        amplicons = bioa.Amplicons(data, se_pos, 0, 10)
        graph = bioa.SplitAmpliconReadGraph(amplicons, 0.0)
        actual = bioa.max_bandwidth_strategy(graph)
        first = "abacgcgtat"
        expected = {first: 1.0}
        eq_(len(actual), len(expected), "number of quasispcies found differ")
        eq_(actual[first], expected[first], \
                "number of quasispcies found differ")

        data = [("abac", 0), ("babg", 0), ("abac", 0),
                ("cgcg", 3), ("gtgt", 3), ("gtgt", 3),
                ("gtat", 6), ("tata", 6), ("gtat", 6)]
        se_pos = [(0, 4), (3, 7), (6, 10)]
        amplicons = bioa.Amplicons(data, se_pos, 0, 10)
        graph = bioa.SplitAmpliconReadGraph(amplicons, 0.0)
        actual = bioa.max_bandwidth_strategy(graph)
        first = "abacgcgtat"
        second = "babgtgtata"
        expected = {first: 0.5, second: 0.5}
        eq_(len(actual), len(expected), "number of quasispcies found differ")
        eq_(actual[first], expected[first], \
                "number of quasispcies found differ")
        eq_(actual[second], expected[second], \
                "number of quasispcies found differ")

        data = [("abac", 0), ("babg", 0), ("abac", 0),
                ("cgcg", 3), ("gtgt", 3), ("gtgt", 3),
                ("gtat", 6), ("tata", 6), ("gtat", 6)]
        se_pos = [(0, 4), (3, 7), (6, 10)]
        amplicons = bioa.Amplicons(data, se_pos, 0, 10)
        graph = bioa.SplitAmpliconReadGraph(amplicons, 0.0)
        actual = bioa.max_bandwidth_strategy(graph, factor=0.5, until_covered=True)
        first = "abacgcgtat"
        second = "babgtgtata"
        expected = {first: 0.5, second: 0.5}
        eq_(len(actual), len(expected), "number of quasispcies found differ")
        eq_(actual[first], expected[first], \
                "number of quasispcies found differ")
        eq_(actual[second], expected[second], \
                "number of quasispcies found differ")

        data = [("abac", 0), ("babg", 0), ("abac", 0),
                ("cgcg", 3), ("gtgt", 3), ("gtgt", 3),
                ("gtat", 6), ("tata", 6), ("gtat", 6)]
        se_pos = [(0, 4), (3, 7), (6, 10)]
        amplicons = bioa.Amplicons(data, se_pos, 0, 10)
        graph = bioa.SplitAmpliconReadGraph(amplicons, 0.0)
        actual = bioa.max_bandwidth_strategy(graph, use_em=True)
        first = "abacgcgtat"
        second = "babgtgtata"
        expected = {first: 0.5, second: 0.5}
        eq_(len(actual), len(expected), "number of quasispcies found differ")

        data = [("abac", 0), ("babg", 0), ("abac", 0),
                ("cgcg", 3), ("gtgt", 3), ("gtgt", 3),
                ("gtat", 6), ("tata", 6), ("gtat", 6)]
        se_pos = [(0, 4), (3, 7), (6, 10)]
        amplicons = bioa.Amplicons(data, se_pos, 0, 10)
        graph = bioa.DecliquedAmpliconReadGraph(amplicons, 0.0)
        actual = bioa.max_bandwidth_strategy(graph, use_em=True)
        first = "abacgcgtat"
        second = "babgtgtata"
        expected = {first: 0.5, second: 0.5}
        eq_(len(actual), len(expected), "number of quasispcies found differ")

        return

    def test_random_bandwidth_strategy(self):
        data = [("abac", 0), ("abac", 0),
                ("cgcg", 3), ("cgcg", 3),
                ("gtat", 6), ("gtat", 6)]
        se_pos = [(0, 4), (3, 7), (6, 10)]
        amplicons = bioa.Amplicons(data, se_pos, 0, 10)
        graph = bioa.SplitAmpliconReadGraph(amplicons, 0.0)
        bioa.random_bandwidth_strategy(graph)

        data = [("abac", 0), ("babg", 0), ("abac", 0),
                ("cgcg", 3), ("cgcg", 3), ("gtgt", 3),
                ("gtat", 6), ("gtat", 6), ("tata", 6)]
        se_pos = [(0, 4), (3, 7), (6, 10)]
        amplicons = bioa.Amplicons(data, se_pos, 0, 10)
        graph = bioa.SplitAmpliconReadGraph(amplicons, 0.0)
        bioa.random_bandwidth_strategy(graph)

    def test_max_frequency_strategy(self):
        data = [("abac", 0), ("abac", 0),
                ("cgcg", 3), ("cgcg", 3),
                ("gtat", 6), ("gtat", 6)]
        se_pos = [(0, 4), (3, 7), (6, 10)]
        amplicons = bioa.Amplicons(data, se_pos, 0, 10)
        graph = bioa.SplitAmpliconReadGraph(amplicons, 0.0)
        qs = bioa.max_frequency_strategy(graph)
        singleton = "abacgcgtat"
        expected = {singleton: 1.0}
        eq_(qs[singleton], expected[singleton], \
                "number of quasispcies found differ")

        data = [("abac", 0), ("babg", 0), ("abac", 0),
                ("cgcg", 3), ("cgcg", 3), ("gtgt", 3),
                ("gtat", 6), ("gtat", 6), ("tata", 6)]
        se_pos = [(0, 4), (3, 7), (6, 10)]
        amplicons = bioa.Amplicons(data, se_pos, 0, 10)
        graph = bioa.SplitAmpliconReadGraph(amplicons, 0.0)
        actual = bioa.max_frequency_strategy(graph)

        first = "abacgcgtat"
        second = "babgtgtata"
        # worry about testing frequencies later. For now coverage is more
        # important
        #expected = {first: 0.5, second: 0.5}
        expected = [first, second]
        eq_(len(actual), len(expected), "number of quasispcies found differ")
        actualqs = actual.keys()
        actualqs.sort()
        eq_(actualqs[0], expected[0], \
                "number of quasispcies found differ")
        eq_(actualqs[1], expected[1], \
                "number of quasispcies found differ")

    def test_greedy_fork_resolution(self):
        # ensure the graph structure is correct.
        data = [("abab", 0), ("aabb", 0),
                ("baaa", 3), ("baba", 3)]
        se_pos = [(0, 4), (3, 7)]
        amplicons = bioa.Amplicons(data, se_pos, 0, 7)
        graph = bioa.DecliquedAmpliconReadGraph(amplicons, 0.0)
        graph = bioa.greedy_fork_resolution(graph)

        eq_(8, len(graph), "number of nodes do not match")
        eq_(8, graph.size(), "number of edges do not match")

        data = [("abab", 0), ("aabb", 0), ("abab", 0),
                ("baaa", 3), ("baba", 3), ("baba", 3)]
        se_pos = [(0, 4), (3, 7)]
        amplicons = bioa.Amplicons(data, se_pos, 0, 7)
        graph = bioa.DecliquedAmpliconReadGraph(amplicons, 0.0)
        graph = bioa.greedy_fork_resolution(graph)
        eq_(8, len(graph), "number of nodes do not match")
        eq_(8, graph.size(), "number of edges do not match")

    def test_random_fork_resolution(self):
        """ This will be hard to test as it makes random decisions. Run a few
            examples and make sure no exeptions are thrown.
        """
        data = [("abab", 0), ("aabb", 0),
                ("baaa", 3), ("baba", 3)]
        se_pos = [(0, 4), (3, 7)]
        amplicons = bioa.Amplicons(data, se_pos, 0, 7)
        graph = bioa.DecliquedAmpliconReadGraph(amplicons, 0.0)
        bioa.random_fork_resolution(graph)

        data = [("abab", 0), ("aabb", 0), ("abab", 0),
                ("baaa", 3), ("baba", 3), ("baba", 3)]
        se_pos = [(0, 4), (3, 7)]
        amplicons = bioa.Amplicons(data, se_pos, 0, 7)
        graph = bioa.DecliquedAmpliconReadGraph(amplicons, 0.0)
        bioa.random_fork_resolution(graph)

    def test_min_forest_fork_resolution(self):
        # if we can't import cplex just skip this test
        try:
            import cplex
        except ImportError:
            print "No cplex! skipping min forest test"
            return

        data = [("abab", 0), ("aabb", 0),
                ("baaa", 3), ("baba", 3)]
        se_pos = [(0, 4), (3, 7)]
        amplicons = bioa.Amplicons(data, se_pos, 0, 7)
        graph = bioa.DecliquedAmpliconReadGraph(amplicons, 0.0)
        graph = bioa.min_forest_fork_resolution(graph)

        data = [("abab", 0), ("aabb", 0), ("abab", 0),
                ("baaa", 3), ("baba", 3), ("baba", 3)]
        se_pos = [(0, 4), (3, 7)]
        amplicons = bioa.Amplicons(data, se_pos, 0, 7)
        graph = bioa.DecliquedAmpliconReadGraph(amplicons, 0.0)
        graph = bioa.min_forest_fork_resolution(graph)

        data = [("abab", 0), ("aabb", 0), ("abab", 0),
                ("baaa", 3), ("baba", 3), ("bbba", 3)]
        se_pos = [(0, 4), (3, 7)]
        amplicons = bioa.Amplicons(data, se_pos, 0, 7)
        graph = bioa.DecliquedAmpliconReadGraph(amplicons, 0.0)
        graph = bioa.min_forest_fork_resolution(graph)

    def test_least_squares_fork_balance(self):
        # if we can't import cplex just skip this test
        try:
            import cplex
        except ImportError:
            print "No cplex! skipping least squares test"
            return

        data = [("abab", 0), ("aabb", 0), ("abab", 0), ("abab", 0),
                ("baaa", 3), ("baaa", 3), ("baba", 3),
                ("abab", 6), ("abbb", 6), ("abbb", 6), ("abab", 6)]
        se_pos = [(0, 4), (3, 7), (6, 10)]
        amplicons = bioa.Amplicons(data, se_pos, 0, 10)
        graph = bioa.DecliquedAmpliconReadGraph(amplicons, 1)
        graph = bioa.least_squares_fork_balance(graph)
        forks = graph.get_forks()
        for fork in forks:
            lsum = sum(graph.get_node_freq(pred) for pred in graph.predecessors(fork))
            rsum = sum(graph.get_node_freq(succ) for succ in graph.successors(fork))
            ok_(math.fabs(lsum - rsum) < 1e-3, "fork is not balanced!")

        data = [["abab", "aabb", "abab", "abab"],
                ["baaa", "baba", "baaa", "baba"],
                ["abbb", "abbb", "abab"]]
        data = [("abab", 0), ("aabb", 0), ("abab", 0), ("abab", 0),
                ("baaa", 3), ("baaa", 3), ("baba", 3), ("baba", 3),
                ("abbb", 6), ("abbb", 6), ("abab", 6)]
        se_pos = [(0, 4), (3, 7), (6, 10)]
        amplicons = bioa.Amplicons(data, se_pos, 0, 10)
        graph = bioa.DecliquedAmpliconReadGraph(amplicons, 1)
        graph = bioa.least_squares_fork_balance(graph)
        forks = graph.get_forks()
        for fork in forks:
            lsum = sum(graph.get_node_freq(pred) for pred in graph.predecessors(fork))
            rsum = sum(graph.get_node_freq(succ) for succ in graph.successors(fork))
            ok_(math.fabs(lsum - rsum) < 1e-3, "fork is not balanced!")

    def test_min_unsplittable_flows_resolution(self):
        # if we can't import cplex just skip this test
        try:
            import cplex
        except ImportError:
            print "No cplex! skipping least squares test"
            return

        data = [("abab", 0), ("abab", 0),
                ("baba", 3), ("baba", 3)]
        se_pos = [(0, 4), (3, 7)]
        amplicons = bioa.Amplicons(data, se_pos, 0, 7)
        graph = bioa.DecliquedAmpliconReadGraph(amplicons, 0)
        results = bioa.min_unsplittable_flows_resolution(graph, 1)
        ok_("abababa" in results, "qsps not found!")

        data = [("abab", 0), ("aabb", 0), ("abab", 0),
                ("baaa", 3), ("baba", 3), ("baba", 3)]
        se_pos = [(0, 4), (3, 7)]
        amplicons = bioa.Amplicons(data, se_pos, 0, 7)
        graph = bioa.DecliquedAmpliconReadGraph(amplicons, 0)
        results = bioa.min_unsplittable_flows_resolution(graph, 2)
        ok_(len(results) == 2, "did not find qsps!")
        for result in results:
            ok_(len(result) == 7, "did not rebuild qsps!")

        data = [("abab", 0), ("aabb", 0), ("abab", 0), ("abab", 0),
                ("baaa", 3), ("baaa", 3), ("baba", 3), ("baba", 3),
                ("abbb", 6), ("abbb", 6), ("abab", 6)]
        se_pos = [(0, 4), (3, 7), (6, 10)]
        amplicons = bioa.Amplicons(data, se_pos, 0, 10)
        graph = bioa.DecliquedAmpliconReadGraph(amplicons, 0)
        results = bioa.min_unsplittable_flows_resolution(graph, 2)
        ok_(len(results) == 2, "did not find qsps!")
        for result in results:
            ok_(len(result) == 10, "did not rebuild qsps!")

        data = [("abab", 0), ("aabc", 0), ("abab", 0), ("abab", 0),
                ("baaa", 3), ("caat", 3), ("baba", 3), ("baba", 3),
                ("abbb", 6), ("abbb", 6), ("abab", 6), ("tbab", 6)]
        se_pos = [(0, 4), (3, 7), (6, 10)]
        amplicons = bioa.Amplicons(data, se_pos, 0, 10)
        graph = bioa.DecliquedAmpliconReadGraph(amplicons, 0)
        results = bioa.min_unsplittable_flows_resolution(graph, 3)
        ok_(len(results) == 3, "did not find qsps!")
        for result in results:
            ok_(len(result) == 10, "did not rebuild qsps!")

        data = [("abab", 0),
                ("baaa", 3),
                ("abbb", 6), ("abbb", 6), ("abab", 6), ("abab", 6)]
        se_pos = [(0, 4), (3, 7), (6, 10)]
        amplicons = bioa.Amplicons(data, se_pos, 0, 10)
        graph = bioa.DecliquedAmpliconReadGraph(amplicons, 0)
        results = bioa.min_unsplittable_flows_resolution(graph, 3)
        ok_(len(results) == 2, "did not find qsps!")
        for result in results:
            ok_(len(result) == 10, "did not rebuild qsps!")


    def test_amplicon_frequency_matrix_strategy(self):
        """
            This tests the amplicon viral quasipsecies reconstruction
            strategy.
        """

        # we should have 0 quasispecies
        data = [("abab", 0), ("baba", 0), ("abab", 0),
                ("cgcg", 3), ("gtgt", 3), ("gtgt", 3),
                ("atat", 6), ("tata", 6), ("atta", 6)]
        se_pos = [(0, 4), (3, 7), (6, 10)]
        amplicons = bioa.Amplicons(data, se_pos, 0, 10)
        variants = bioa.amplicon_frequency_matrix_strategy(amplicons, 1, True)
        assert_equal(0, len(variants))

        # we should have 1 quasispecies
        data = [("abac", 0), ("babg", 0), ("abac", 0),
                ("cgcg", 3), ("gtgt", 3), ("gtgt", 3),
                ("gtat", 6), ("cata", 6), ("gtta", 6)]
        se_pos = [(0, 4), (3, 7), (6, 10)]
        amplicons = bioa.Amplicons(data, se_pos, 0, 10)
        variants = bioa.amplicon_frequency_matrix_strategy(amplicons, 1, True)
        assert_equal(1, len(variants))

        # we should have 2 quasispecies
        data = [("abac", 0), ("babg", 0), ("abac", 0),
                ("cgcg", 3), ("gtgt", 3), ("gtgt", 3),
                ("gtat", 6), ("tata", 6), ("gtta", 6)]
        se_pos = [(0, 4), (3, 7), (6, 10)]
        amplicons = bioa.Amplicons(data, se_pos, 0, 10)
        variants = bioa.amplicon_frequency_matrix_strategy(amplicons, 1, True)
        assert_equal(2, len(variants))


    def test_amplicon_frequency_matrix_strategy_from_graph(self):
        # we should have 0 quasispecies
        data = [("abab", 0), ("baba", 0), ("abab", 0),
                ("cgcg", 3), ("gtgt", 3), ("gtgt", 3),
                ("atat", 6), ("tata", 6), ("atta", 6)]
        se_pos = [(0, 4), (3, 7), (6, 10)]
        amplicons = bioa.Amplicons(data, se_pos, 0, 10)
        graph = bioa.DecliquedAmpliconReadGraph(amplicons, 0)
        variants = bioa.amplicon_frequency_matrix_strategy_from_graph(graph, True)
        assert_equal(0, len(variants))

        # we should have 1 quasispecies
        data = [("abac", 0), ("babg", 0), ("abac", 0),
                ("cgcg", 3), ("gtgt", 3), ("gtgt", 3),
                ("gtat", 6), ("cata", 6), ("gtta", 6)]
        se_pos = [(0, 4), (3, 7), (6, 10)]
        amplicons = bioa.Amplicons(data, se_pos, 0, 10)
        graph = bioa.DecliquedAmpliconReadGraph(amplicons, 0)
        variants = bioa.amplicon_frequency_matrix_strategy_from_graph(graph, True)
        assert_equal(1, len(variants))

        # we should have 2 quasispecies
        data = [("abac", 0), ("babg", 0), ("abac", 0),
                ("cgcg", 3), ("gtgt", 3), ("gtgt", 3),
                ("gtat", 6), ("tata", 6), ("gtta", 6)]
        se_pos = [(0, 4), (3, 7), (6, 10)]
        amplicons = bioa.Amplicons(data, se_pos, 0, 10)
        graph = bioa.DecliquedAmpliconReadGraph(amplicons, 1)
        variants = bioa.amplicon_frequency_matrix_strategy_from_graph(graph, True)
        assert_equal(2, len(variants))
