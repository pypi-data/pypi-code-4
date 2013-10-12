# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 Branko Majic
#
# This file is part of Django Conntrackt.
#
# Django Conntrackt is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# Django Conntrackt is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# Django Conntrackt.  If not, see <http://www.gnu.org/licenses/>.
#


# Django imports.
from django.test import TestCase

# Third-party Python library imports.
import palette
import pydot

# Application imports.
from conntrackt.models import Entity, Project, Communication
from conntrackt import utils
from .factories import setup_test_data


class GenerateEntityIptablesTest(TestCase):

    def setUp(self):
        """
        Set-up some test data.
        """

        setup_test_data()

    def test_generated_iptables(self):
        """
        Tests if the entity's iptables are generated properly or not.
        """

        entity = Entity.objects.get(pk=1)
        generated = utils.generate_entity_iptables(entity)

        expected = """*filter
:INPUT DROP [0:0]
# Accept all incoming related traffic.
-A INPUT -m state --state RELATED,ESTABLISHED -j ACCEPT

# Accept all incoming traffic on loopback interface.
-A INPUT -i lo -j ACCEPT

# Communicate over ICMP:8
-A INPUT -s 192.168.1.2/255.255.255.255 -d 192.168.1.1/255.255.255.255 -p icmp -m icmp --icmp-type 8 -j ACCEPT

# Communicate over TCP:22
-A INPUT -s 192.168.1.2/255.255.255.255 -d 192.168.1.1/255.255.255.255 -p tcp -m tcp --dport 22 -j ACCEPT
-A INPUT -s 10.10.4.0/255.255.255.0 -d 192.168.1.1/255.255.255.255 -p tcp -m tcp --dport 22 -j ACCEPT

# Communicate over TCP:3306
-A INPUT -s 192.168.1.3/255.255.255.255 -d 192.168.1.1/255.255.255.255 -p tcp -m tcp --dport 3306 -j ACCEPT

:OUTPUT ACCEPT [0:0]
:FORWARD DROP [0:0]
COMMIT
*nat
:PREROUTING ACCEPT [0:0]
:INPUT ACCEPT [0:0]
:OUTPUT ACCEPT [0:0]
:POSTROUTING ACCEPT [0:0]
COMMIT
"""
        self.assertEqual(generated, expected)


class GetDistinctColorsTest(TestCase):
    """
    Tests covering the get_distinct_colors function.
    """

    def test_count(self):
        """
        Tests if correct number of distinct colours are returned.
        """

        colors = utils.get_distinct_colors(13)

        self.assertEqual(len(colors), 13)

        colors = utils.get_distinct_colors(123)

        self.assertEqual(len(colors), 123)

    def test_start(self):
        """
        Tests if the passed start colour is returned as part of generated
        colours.
        """

        start = palette.Color("#AA3311")

        colors = utils.get_distinct_colors(10, start)

        self.assertEqual(start.hex, colors[0].hex)

    def test_color_distance(self):
        """
        Tests if the generated colous all have proper distance between
        each-other.
        """

        colors = utils.get_distinct_colors(13)

        # Set allowed margin of difference to 0.1%
        delta = (1 / 13.) * 0.001

        # Calculate diffs between colours.
        diffs = [colors[i + 1].hsl["h"] - colors[i].hsl["h"] for i in range(12)]

        # Take first diff as reference point.
        reference = diffs[0]

        # Create list that contains True/False for diffs depending on whether
        # they're in delta-surrounding of reference point.
        equal = [(abs(diff - reference) < delta) for diff in diffs]

        # There should be 12 True values.
        self.assertEqual(equal.count(True), 12)

        # Check the difference between first and last colour.
        equal = abs(colors[0].hsl["h"] + 1 - colors[12].hsl["h"] - reference) < delta
        self.assertEqual(True, equal)


class GenerateProjectDiagramTest(TestCase):
    """
    Tests the generate_project_diagram function.
    """

    def setUp(self):
        """
        Set-up some test data.
        """

        setup_test_data()

    def test_unique_entity_colors(self):
        """
        Tests if each node/entity in the graph will have a unique colour.
        """

        # Get diagram for project
        project = Project.objects.get(pk=1)
        diagram = utils.generate_project_diagram(project)

        # Extract all nodes
        clusters = diagram.get_subgraphs()
        nodes = []
        for cluster in clusters:
            nodes.extend(cluster.get_nodes())

        # Get the node colours.
        colors = [n.get_color() for n in nodes]

        # Verify they're all unique colours.
        self.assertEqual(len(colors), len(set(colors)))

    def test_edge_colours(self):
        """
        Tests if the edge colours match with source node/entity colour.
        """

        # Get diagram for project
        project = Project.objects.get(pk=1)
        diagram = utils.generate_project_diagram(project)

        # Extract all nodes and edges.
        clusters = diagram.get_subgraphs()
        nodes = {}
        for cluster in clusters:
            for node in cluster.get_nodes():
                nodes[node.get_name()] = node
        edges = diagram.get_edges()

        # Validate that edges have same colour as the source nodes.
        for edge in edges:
            self.assertEqual(nodes[edge.get_source()].get_color(), edge.get_color())

    def test_entities_present(self):
        """
        Tests if all (and only) specific project entities are in the graph.
        """

        # Get diagram for project
        project = Project.objects.get(pk=1)
        diagram = utils.generate_project_diagram(project)

        # Set-up expected node names.
        expected_node_names = [u"Test Entity 1", u"Test Entity 2", u"Test Entity 3", u"Test Subnet 4"]

        # Get all nodes from diagram.
        clusters = diagram.get_subgraphs()
        nodes = []
        for cluster in clusters:
            nodes.extend(cluster.get_nodes())

        # Get the node names, strip the quotes from them.
        node_names = [n.get_name().replace('"', '') for n in nodes]

        # Validate that the two lists contain same elements.
        self.assertEqual(sorted(expected_node_names), sorted(node_names))

    def test_communications_present(self):
        """
        Tests if all (and only) specific project communications are in the
        graph.
        """

        # Get diagram for project
        project = Project.objects.get(pk=1)
        diagram = utils.generate_project_diagram(project)

        # Get all edges from the diagram.
        edges = diagram.get_edges()

        # Create list of edge labels.
        edge_labels = ["%s -> %s (%s)" % (e.get_source().replace('"', ''),
                                           e.get_destination().replace('"', ''),
                                           e.get_label().replace('"', '')) for e in edges]

        # Create list of expected edge labels
        expected_edge_labels = [u'Test Entity 1 -> Test Entity 2 (UDP:123)',
                                u'Test Entity 1 -> Test Entity 3 (UDP:53)',
                                u'Test Entity 2 -> Test Entity 1 (ICMP:8)',
                                u'Test Entity 2 -> Test Entity 1 (TCP:22)',
                                u'Test Entity 3 -> Test Entity 1 (TCP:3306)',
                                u'Test Subnet 4 -> Test Entity 1 (TCP:22)']

        self.assertEqual(sorted(expected_edge_labels), sorted(edge_labels))

    def test_locations_present(self):
        """
        Tests if all (and only) specific project locations are in the graph (as
        clusters).
        """

        # Get diagram for project.
        project = Project.objects.get(pk=1)
        diagram = utils.generate_project_diagram(project)

        # Set-up expected cluster names (based on locations).
        expected_cluster_names = ["cluster_test_location_1", "cluster_test_location_2"]

        # Get cluster names.
        cluster_names = [s.get_name() for s in diagram.get_subgraphs()]

        self.assertEqual(sorted(expected_cluster_names), sorted(cluster_names))

    def test_return_type(self):
        """
        Tests if a correct object type is returned.
        """

        # Get diagram for project.
        project = Project.objects.get(pk=1)
        diagram = utils.generate_project_diagram(project)

        self.assertEqual(type(diagram), pydot.Dot)

    def test_graph_properties(self):
        """
        Tests if graph properties have been set-up properly.
        """

        # Get diagram for project.
        project = Project.objects.get(pk=1)
        diagram = utils.generate_project_diagram(project)

        self.assertEqual("digraph", diagram.get_graph_type())
        self.assertEqual("transparent", diagram.get_bgcolor())
        self.assertEqual("1.5", diagram.get_nodesep())
        self.assertEqual([{"shape": "record"}], diagram.get_node_defaults())
