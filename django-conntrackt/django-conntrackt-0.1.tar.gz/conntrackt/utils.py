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


# Standard library imports.
import re
import itertools

# Third-party Python library imports.
import palette
import pydot

# Django imports.
from django.template import Context, loader

# Application imports.
import iptables
from .models import Communication


def generate_entity_iptables(entity):
    """
    Generates full iptables rules for the supplied entity. The generated rules
    can be fed directly to the iptables-restore utility.

    Arguments:

        entity - An Entity instance for which the iptables rules should be
        generated.

    Returns:

        String containing the iptables rules for entity.
    """

    # Fetch list of incoming communications.
    incoming = entity.incoming_communications()

    # Set-up the nat table.
    nat = iptables.Table("nat")
    for chain in ("PREROUTING", "INPUT", "OUTPUT", "POSTROUTING"):
        nat.add_chain(iptables.Chain(chain, "ACCEPT"))

    # Set-up the filter table INPUT chain.
    filter = iptables.Table("filter")
    input = iptables.Chain("INPUT", "DROP")

    input.add_rule(iptables.LoopbackRule())
    input.add_rule(iptables.RelatedRule())

    for communication in incoming:
        source = "%s/%s" % (communication.source.address, communication.source.netmask)
        destination = "%s/%s" % (communication.destination.address, communication.destination.netmask)
        input.add_rule(iptables.Rule(source, destination, communication.protocol, communication.port, communication.description))
    filter.add_chain(input)

    # Set-up empty chains.
    filter.add_chain(iptables.Chain("OUTPUT", "ACCEPT"))
    filter.add_chain(iptables.Chain("FORWARD", "DROP"))

    # Construct the iptables file using the two tables.
    content = "%s%s" % (filter, nat)

    return content


def get_distinct_colors(count, start=palette.Color("#AE1111")):
    """
    Generates a number of distinct colours, and returns them as a list. The
    colours are generated using the HSL (hue, saturation, lightness) model,
    where saturation and lightness is kept the same for all colours, with
    differing hue. The hue difference between each subsequent color in the list
    is kept the same.

    Arguments:

        count - Total number of colours that should be generated.

        start - First colour that should be taken as a start point. All colours
        are generated relative to this colour by increasing the hue. Should be
        an instance of palette.Color class. Defaults to RGB colour "#AE1111".

    Return:

        List of distinct palette.Color instances.
    """

    # Read the HSL from provided Color.
    hue, sat, lum = start.hsl["h"], start.hsl["s"], start.hsl["l"]

    # Calculate the step increase.
    step = 1 / float(count)

    # Initiate an empty list that will store the generated colours.
    colors = []

    # Generate new colour by increasing the hue as long as we haven't generated
    # the requested number of colours.
    while len(colors) < count:
        colors.append(palette.Color(hsl=(hue, sat, lum)))
        hue += step

    return colors


def generate_project_diagram(project):
    """
    Generates communication diagram for provided project.

    Arguments:

        project - Project for which the diagram should be generated. Instance of
        conntrackt.models.Project class.

    Returns:

        Dot diagram (digraph) representing all of the communications in a
        project.
    """

    # Set-up the graph object.
    graph = pydot.Dot(graph_name=project.name, graph_type="digraph", bgcolor="transparent", nodesep="1.5")
    # Set-up defaults for the graph nodes.
    graph.set_node_defaults(shape="record")

    # Obtain list of all entities in a project.
    entities = project.entity_set.all()

    # Set-up dictinary that will contains clusters of entities belonging to same
    # location.
    clusters = {}

    # Dictinoary for storing mapping between nodes and colours.
    node_colors = {}

    # Get distinct colours, one for each node/entity.
    colors = get_distinct_colors(entities.count())

    # Created nodes based on entities, and put them into correct cluster.
    for entity in entities:

        # Try to get the existing cluster based on location name.
        location = entity.location
        cluster_name = location.name.replace(" ", "_").lower()
        cluster = clusters.get(cluster_name, None)

        # Set-up a new cluster for location encountered for the first time.
        if cluster is None:
            cluster = pydot.Cluster(graph_name=cluster_name, label=location.name)
            clusters[cluster_name] = cluster

        # Fetch a colour that will be associated with the node/entity.
        node_color = colors.pop()
        node_colors[entity.id] = node_color.hex

        # Determine whether the node label should be black or white based on brightness of node colour.
        node_color_brightness = 1 - (node_color.rgb["r"] * 0.299 + node_color.rgb["g"] * 0.587 + node_color.rgb["b"] * 0.114)

        if node_color_brightness < 0.5:
            font_color = "black"
        else:
            font_color = "white"

        # Finally create the node, and add it to location cluster.
        node = pydot.Node(entity.name, style="filled", color=node_color.hex, fontcolor=font_color)
        cluster.add_node(node)

    # Add clusters to the graph.
    for cluster in clusters.values():
        graph.add_subgraph(cluster)

    # Get all project communications.
    communications = Communication.objects.filter(source__entity__project=project)

    # Add the edges (lines) representing communications, drawing them with same
    # colour as the source node/entity.
    for comm in communications:
        edge_color = node_colors[comm.source.entity.id]

        label = '"%s:%s"' % (comm.protocol, str(comm.port))

        edge = pydot.Edge(comm.source.entity.name, comm.destination.entity.name, label=label, color=edge_color)

        graph.add_edge(edge)

    return graph
