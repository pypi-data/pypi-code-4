import datetime
import logging
import time
from operator import attrgetter

from . import base
from .storage.base import (
        StoredActivity,
        ActivityObject,
        )

log = logging.getLogger(__name__)


class NodeManager(base.NodeManagerBase):
    """Manages the network of connected nodes.

    Knows how to connect and disconnect nodes and serialize the graph.
    """

    def __init__(self, storage):
        self.storage = storage

    def follow(self, follower, following):
        """Create a directed edge from :class:`Node` ``follower`` to
        :class:`Node` ``following``.
        """
        self.storage.create_edge(follower, following)

    def unfollow(self, follower, following):
        """Destroy a directed edge from :class:`Node` ``follower`` to
        :class:`Node` ``following``.
        """
        self.storage.destroy_edge(follower, following)

    def is_following(self, follower, following):
        """Determine if there is a directed edge from :class:`Node`
        ``follower`` to :class:`Node` ``following``.
        """
        return self.storage.edge_exists(follower, following)

    def get_node(self, node_id):
        """Return the node for the given node_id."""
        return self.storage.get_node(node_id)

    def get_nodes(self, node_ids):
        """Return nodes for the given node_ids."""
        return self.storage.get_nodes(node_ids)

    def create_node(self, node_id):
        """Create a new node"""
        return self.storage.create_node(node_id)

    def save_node(self, node):
        """Save an existing node"""
        return self.storage.save_node(node)


class ActivityManager(base.ActivityManagerBase):
    """Serializes :class:`Activity` objects."""

    def __init__(self, storage, node_manager):
        self.storage = storage
        self.node_manager = node_manager

    def create(self, actor, verb, obj, target=None, related_nodes=None):
        """Create and serialize an :class:`Activity`.

        Serializing includes making a copy of the activity for any node in the
        network that is connected to any node in the activity.
        """
        # Figure out who needs a copy
        related_nodes = related_nodes or []
        owners = [
                node.node_id for node in [actor, obj, target] + related_nodes
                if hasattr(node, 'node_id')]

        for owner in owners:
            activity = StoredActivity(
                    actor=actor,
                    verb=verb,
                    obj=obj,
                    target=target,
                    published=datetime.datetime.utcnow(),
                    node_id = owner
                    )
            self.storage.save_activity(activity)
        return activity

    def get_activities(self, nodes, since=None, sort=None, limit=0, skip=0, query=None):
        """Return all activities associated with the given nodes.

        Params:
            since (datetime) - return activities that have occured since this
                               datetime
        """
        return self.storage.get_activities(nodes, since=since, sort=sort,
                limit=limit, skip=skip, query=query)

    def save_timeline(self, node_id, activities):
        """Save a list of activities to a node's timeline."""
        self.storage.save_timeline(node_id, activities)

    def get_timeline(self, node_id, sort=None, limit=0, skip=0, query=None):
        """Return the timeline for node_id.

        Timeline is the already-aggregated list of activities.
        """
        return self.storage.get_timeline(node_id, sort=sort, limit=limit,
                skip=skip, query=query)


class Aggregator(object):
    """Creates a timeline for a given node in the network graph."""

    def __init__(self, activity_manager, node_manager):
        self.node_manager = node_manager
        self.activity_manager = activity_manager

    def _unique_activities(self, activities):
        """Return a list of unique activities.

        """
        attrs = ('actor', 'obj', 'target')
        seen, unique = [], []
        for activity in activities:
            d = dict((a, ActivityObject.to_dict(getattr(activity, a)))
                    for a in attrs)
            d.update(verb=activity.verb)
            if d in seen:
                continue
            seen.append(d)
            unique.append(activity)
        return unique

    def classify_activities(self, activities):
        """Return a list of activities with classfication flags added."""
        return activities

    def create_timeline(self, node_id):
        """Create, store, and return the timeline for a given node.
        """
        node = self.node_manager.get_node(node_id)
        if not node:
            log.warning('Node not found for node_id "%s". Creating...', node_id)
            node = self.node_manager.create_node(node_id)
        last_timeline_aggregation = node.last_timeline_aggregation
        node.last_timeline_aggregation = datetime.datetime.utcnow()
        # save node to persist last_timeline_aggregation timestamp
        self.node_manager.save_node(node)
        # get a subset of the nodes be followed
        connections = self.filter_connections(
                self.node_manager.get_nodes(node.following or []))
        # retrieve the followed nodes' activities
        activities = self.activity_manager.get_activities(connections,
                since=last_timeline_aggregation)
        # filter activities for followed nodes
        activities = self.filter_activities(activities)
        # add activities for this node
        activities += self.activity_manager.get_activities([node],
                since=last_timeline_aggregation)
        # if we don't have any activities at this point, there's nothing from
        # which to generate a timeline
        if not activities:
            return self.activity_manager.get_timeline(node_id)
        # remove duplicates
        activities = self._unique_activities(activities)
        # classify and score activities
        activities = self.classify_activities(activities)
        activities = self.score_activities(activities)
        # save to this node's timeline
        self.activity_manager.save_timeline(node_id, activities)
        return self.activity_manager.get_timeline(node_id)

    def needs_aggregation(self, node):
        """Return True if it's time for this node's timeline to be
        (re)aggregated).
        """
        # For now, just do an aggregation every time a timeline is requested
        return True

        # Alternative, based on time since last aggregation:
        last = node.last_timeline_aggregation
        if not last: return True
        # TODO: put this time threshhold in config
        return (datetime.datetime.utcnow() - last).seconds > 60

    def get_timeline(self, node, page=0, limit=100, actor_only=False, filter_func=None):
        """Return a (paged and limited) timeline for `node`.

        `page` is zero-based (page 0 is the first page of results).

        If `actor_only` == True, timeline will be filtered to only include
        activities where `node` is the actor.

        Pass a callable to `filter_func` to arbitrarily filter activities out of the
        timeline. `filter_func` will be passed an activity, and should return True
        to keep the activity in the timeline, or False to filter it out.

        Total size of the returned timeline may be less than `limit` if:
            1. the timeline is exhausted (last page)
            2. activities are filtered out by filter_func
        """
        node_id = node.node_id
        node = self.node_manager.get_node(node_id)
        page, limit = int(page), int(limit or 0)
        if not node or self.needs_aggregation(node):
            self.create_timeline(node_id)
        query_filter = {'actor.node_id': node_id} if actor_only else None
        timeline = self.activity_manager.get_timeline(
                node_id, sort=[('score', -1)], skip=page*limit, limit=limit,
                query=query_filter)
        if filter_func:
            timeline = filter(filter_func, timeline)
        return timeline

    def filter_connections(self, nodes):
        """Return a subset of a node's total outbound connections (nodes he is
        following) using the algorithm of your choice.
        """
        return nodes

    def filter_activities(self, activities):
        """Return a subset of a node's activities using the algorithm of your
        choice.
        """
        return activities

    def score_activities(self, activities):
        """Return a scored list of activities. By default, newer activities
        have higher scores.
        """
        for a in activities:
            a.score = time.mktime(a.published.timetuple())
        return activities
