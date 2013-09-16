# Argument parsing/user input.
from optparse import make_option
import getpass

# Timestamp and date processing.
from datetime import datetime
import pytz

# ORM for Drupal database.
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# String utiilities.
import urllib

# Django imports.
from django.core.management.base import LabelCommand
from django.template.defaultfilters import slugify
from django.db import IntegrityError
from django.contrib.contenttypes.models import ContentType

# Django models.
from django.contrib.sites.models import Site
from django.contrib.comments import get_model as get_comment_model
Comment = get_comment_model()

# Zinnia models.
from zinnia.models import Author
from zinnia.models import Category
from zinnia.models import Entry
from zinnia.managers import PUBLISHED

# For preventing pingbacks during the import.
from zinnia.signals import disconnect_entry_signals
from zinnia.signals import disconnect_discussion_signals


#########################################
# Helper functions for argument parsing #
#########################################
def create_mappingaction(argument_name):
    """
    Wrapper function for generating a MappingAction that will store the parsed
    data under specified argument_name under parser's options.

    Arguments:
        - argument_name - Name of the argument where the parsed data will be
          stored.

    Returns:
        A mappingaction function.
    """

    def mappingaction(option, option_string, value, parser, argument_name=argument_name):
        """
        Custom optparse action for processing arguments of format:

        arg1[=maparg1]:arg2[=maparg2]:...:argN[=mapargN]

        The action can be used for adding a dictionary to the specified
        namespace where the keys are arg1, arg2, ..., argN, and values are
        maparg1, maparg2, ..., mapargN.

        Specifying the maparg mapping is optional. When not specified, the
        action will use the value of key.
        """

        if not getattr(parser.values, argument_name):
            setattr(parser.values, argument_name, dict())
        for mapping in value.split(":"):
            if "=" in mapping:
                key, value = mapping.split("=", 1)
                getattr(parser.values, argument_name)[key] = value
            else:
                getattr(parser.values, argument_name)[mapping] = mapping

    return mappingaction


class DrupalDatabase(object):
    """
    Helper class for accessing the Drupal database. This class is a small
    wrapper around the functionality provided by SQLAlchemy.

    Properties:

      session - SQLAlchemy session object that can be used for running queries
      against the Drupal database.

      Node - Drupal's 'node' table.

      NodeRevisions - Drupal's 'node_revisions' table.

      Users - Drupal's 'users' table.

      Vocabulary - Drupal's 'vocabulary' table.

      TermNode - Drupal's 'term_node' table.

      TermData - Drupal's 'term_data' table.

      TermHierarchy - Drupal's 'term_hierarchy' table.

      Comments - Drupal's 'comments' table.
    """

    def __init__(self, engine):
        """
        Initialises the SQLAlchemy ORM for Drupal tables using the provided
        engine.

        Arguments:

          engine
            Initialised SQLAlchemy engine to use when setting-up ORM.
        """

        # Store the engine and set-up a session that will be used for queries.
        self.engine = engine
        self.session = sessionmaker(bind=self.engine)()

        Base = declarative_base(self.engine)

        # Declare Drupal ORM classes.
        class Node(Base):
            """
            For accessing Drupal's "node" table. This table contains mainly metadata
            about a node.
            """

            __tablename__ = 'node'
            __table_args__ = {'autoload': True}

        class NodeRevisions(Base):
            """
            For accessing Drupal's "node_revisions" table. This table contains the
            actual content of nodes.
            """

            __tablename__ = 'node_revisions'
            __table_args__ = {'autoload': True}

        class Users(Base):
            """
            For accessing Drupal's "users" table. This table contains information about
            users.
            """

            __tablename__ = 'users'
            __table_args__ = {'autoload': True}

        class Vocabulary(Base):
            """
            For accessing Drupal's "vocabulary" table. This table contains information
            about Drupal vocabularies (tags and categories).
            """

            __tablename__ = 'vocabulary'
            __table_args__ = {'autoload': True}

        class TermNode(Base):
            """
            For accessing Drupal's "term_node" table. This table contains information about
            mapping of terms from vocabulaires to nodes.
            """

            __tablename__ = 'term_node'
            __table_args__ = {'autoload': True}

        class TermData(Base):
            """
            For accessing Drupal's "term_data" table. This table contains data about
            terms.
            """

            __tablename__ = 'term_data'
            __table_args__ = {'autoload': True}

        class TermHierarchy(Base):
            """
            For accessing Drupal's "term_hierarchy" table. This table contains data
            about term hierarchies (used for importing categories).
            """

            __tablename__ = 'term_hierarchy'
            __table_args__ = {'autoload': True}

        class Comments(Base):
            """
            For accessing Drupal's "comments" table. This table contains comment data.
            """

            __tablename__ = 'comments'
            __table_args__ = {'autoload': True}

        # Easier access to SQLAlchemy ORM.
        self.Node = Node
        self.NodeRevisions = NodeRevisions
        self.Users = Users
        self.Vocabulary = Vocabulary
        self.TermNode = TermNode
        self.TermData = TermData
        self.TermHierarchy = TermHierarchy
        self.Comments = Comments


def import_users(drupal, users=None, custom_mapping=None):
    """
    Imports the requested users from Drupal database, taking into account any
    desired custom mappings between usernames. Generates a mapping dictionary
    between Drupal and Zinnia users.

    Users will be created only if they do not already exist.

    Arguments:

      drupal
        Drupal database from which the users should be imported. Should be an
        instance of DrupalDatabase.

      users
        List of users that should be imported. If provided, only the specified
        users will be imported from Drupal. Default (None) is to import all
        users.

      custom_mapping
        Dictionary defining desired custom mapping between Drupal users and
        Zinnia users. Keys should be usernames in Drupal, and values should be
        desired usernames in Zinnia. Default (None) is to not to apply any
        custom mapping.

    Returns:

      Tuple consisting out of two elements. The first element is dictionary with
      import statistics (keys 'drupal_total', 'zinnia_new', and
      'zinnia_existing'). The second element is a dictionary describing the
      resulting mapping between the Drupal and Zinnia users, where keys are
      Drupal user IDs, and values are Zinnia user IDs (not to be confused with
      custom_mapping).
    """

    mapping = {}

    # Fetch the users from Drupal (all or just a subset).
    if users:
        drupal_users = drupal.session.query(drupal.Users).filter(drupal.Users.name.in_(users))
    else:
        drupal_users = drupal.session.query(drupal.Users).filter(drupal.Users.name != "")

    # Set-up the statistics.
    statistics = {
        'drupal_total': drupal_users.count(),
        'zinnia_new': 0,
        'zinnia_existing': 0,
        }

    # Process each Drupal user.
    for drupal_user in drupal_users:
        # Apply mapping if it was provided.
        username = custom_mapping.get(drupal_user.name, drupal_user.name)

        # Fetch the user if it already exists, or create a new one if it
        # doesn't.
        try:
            author = Author.objects.get(username=username)
            print "User already exists: %s" % username
            statistics["zinnia_existing"] += 1
        except Author.DoesNotExist:
            author = Author.objects.create_user(username, drupal_user.mail)
            # Set the user password. "pass" is a reserved keyword in Python, so
            # we must use the getattr here.
            author.password = "md5$$%s" % getattr(drupal_user, "pass")
            author.is_staff = True
            author.save()
            print "Added user: %s" % username
            statistics["zinnia_new"] += 1

        mapping[drupal_user.uid] = author.id

    return statistics, mapping


def import_categories(drupal):
    """
    Imports categories from Drupal into Zinnia. Categories are created only if
    they do not exist. In addition, the Drupal vocabulary is treated as a
    (top-level) category on its own when moved into Zinnia.

    LIMITATION: The implementation assumes that all categories (terms in non-tag
    vocabularies) in Drupal have _unique_ names. This in return simplifies the
    import code (for determining whether the category needs to be created, or
    existing one should be used).

    Arguments:

      drupal
        Drupal database from which the categories should be imported. Should be
        an instance of DrupalDatabase.

    Returns:

      Tuple consisting out of two elements. The first element is dictionary with
      import statistics (keys 'drupal_total', 'zinnia_new', and
      'zinnia_existing'). The second is a dictionary describing mapping between
      the Drupal and Zinnia categories, where keys are Drupal category IDs, and
      values are Zinnia category IDs.
    """

    mapping = {}

    # Dictinoary representing hierarchy of Drupal categories. Key corresponds to
    # child, value corresponds to child's parent. If parent is set to "0", the
    # category is supposed to be top-level.
    hierarchy = {}

    # Set-up the statistics.
    statistics = {
        "drupal_total": 0,
        "zinnia_new": 0,
        "zinnia_existing": 0,
        }

    # Drupal stores categories within a number of vocabularies. Extract all
    # vocabularies that are not defining tags (that is, extract all category
    # vocabularies).
    vocabularies = drupal.session.query(drupal.Vocabulary).filter(drupal.Vocabulary.tags != 1)

    # Import the categories from each vocabulary.
    for vocabulary in vocabularies:

        # Treat vocabulary itself as a category (top-level one).
        statistics["drupal_total"] += 1

        # Try to fetch existing, or create new category in Zinnia.
        category, created = Category.objects.get_or_create(title=vocabulary.name, slug=slugify(vocabulary.name), description=vocabulary.description)

        if created:
            statistics["zinnia_new"] += 1
        else:
            statistics["zinnia_existing"] += 1

        # Since vocabularies are not categories, use the vocabulary _name_ as
        # identifier instead of primary key (in order to avoid collision with
        # categories).
        mapping[vocabulary.name] = category.pk

        # Vocabulary "category" has no parents.
        hierarchy[vocabulary.name] = 0

        # Look-up the terms that belong to the vocabulary.
        term_query = drupal.session.query(drupal.TermData).filter(drupal.TermData.vid == vocabulary.vid)
        statistics["drupal_total"] += term_query.count()

        # Process each term item.
        for term in term_query:
            term_parent = drupal.session.query(drupal.TermHierarchy).filter(drupal.TermHierarchy.tid == term.tid).first().parent

            # If this is a top-level category in vocabulary, mark the vocabulary
            # pseudo-category itself as its parent instead (refer to vocabulary
            # "category" by its name).
            if term_parent == 0:
                term_parent = vocabulary.name

            # Set-up hierarchy information for this category.
            hierarchy[term.tid] = term_parent

            # Try to fetch existing, or create new category in Zinnia.
            category, created = Category.objects.get_or_create(title=term.name, slug=slugify(term.name), description=term.description)

            if created:
                statistics["zinnia_new"] += 1
            else:
                statistics["zinnia_existing"] += 1

            # Map the Drupal category to Zinnia category.
            mapping[term.tid] = category.pk

    # Update parent information for Zinnia categories (if they're not
    # top-level ones).
    for tid, tid_parent in hierarchy.iteritems():
        if tid_parent != 0:
            category = Category.objects.get(pk=mapping[tid])
            category.parent = Category.objects.get(pk=mapping[tid_parent])
            category.save()

    return statistics, mapping


def extract_tags(drupal):
    """
    Extracts tags from Drupal database. While being extracted the tags will be
    stripped of forward slashes ('/'), replacing them with hyphens ('-').

    Tags do not exist in Zinnia as objects of their own, so no creation of tags
    needs to take place there. This function will mainly allow us to reduce
    database workload (of traversing Drupal database) by having (id, tag) pairs
    in a dictionary.

    Arguments:

      drupal
        Drupal database from which the tags should be extracted. Should be an
        instance of DrupalDatabase.

    Returns:

      Dictionary mapping the Drupal tag term ID into tag string.
    """

    tag_mapping = {}

    # Process all vocabularies that are marked to contains tags.
    for vocabulary in drupal.session.query(drupal.Vocabulary).filter(drupal.Vocabulary.tags == 1).all():
        # Fetch all terms of a tag vocabulary.
        terms = drupal.session.query(drupal.TermData).filter(drupal.TermData.vid == vocabulary.vid).all()
        # Set-up mapping for all terms in a vocabulary.
        for term in terms:
            # The tags in Zinnia are not allowed to contain slashes.
            tag_mapping[term.tid] = term.name.replace("/", "-")

    return tag_mapping


def import_comments(drupal, drupal_node, zinnia_entry, threaded_comments):
    """
    Imports comments from Drupal node into Zinnia entry. Comments are created
    only if they do not exist already.

    Arguments:

      drupal
        Drupal database from which the comments should be extracted. Should be an
        instance of DrupalDatabase.

      drupal_node
        Drupal node object from which the comments should be imported.

      zinnia_entry
        Zinna entry to which the comments should be attached.

      threaded_comments
        Specify whether the comments should be imported as threaded or not. If
        set to True, zinnia-threaded-comments application must be installed as
        well.

    Returns:

      Dictionary with import statistics (keys 'drupal_total', 'zinnia_new', and
      'zinnia_existing')
    """

    # Fetch the current Django site.
    site = Site.objects.get_current()

    # Holds mapping between comment IDs in Drupal and Comment IDs in
    # Zinnia. This is used later on if setting-up threaded comment parents.
    comment_mapping = {}

    # Holds information about parent/child relatinships of Drupal comments. Keys
    # are comment IDs of children, while values are comment IDs of parents.
    hierarchy = {}

    # Fetch all comments for a specific node, ordering them by creation
    # timestamps.
    drupal_comments = drupal.session.query(drupal.Comments).filter(drupal.Comments.nid == drupal_node.nid).order_by(drupal.Comments.timestamp)

    # Set-up some statistics.
    statistics = {
        "drupal_total": drupal_comments.count(),
        "zinnia_new": 0,
        "zinnia_existing": 0,
        }

    # Process all comments from relevant Drupal node.
    for drupal_comment in drupal_comments:
        # Try to fetch existing, or create new comment in Zinnia.
        comment, created = Comment.objects.get_or_create(comment=drupal_comment.comment,
                                                         ip_address=drupal_comment.hostname,
                                                         submit_date=datetime.fromtimestamp(drupal_comment.timestamp, pytz.UTC),
                                                         is_public=True if drupal_comment.status == 0 else False,
                                                         user_name=drupal_comment.name,
                                                         user_email=drupal_comment.mail,
                                                         user_url=drupal_comment.homepage,
                                                         object_pk=zinnia_entry.pk,
                                                         site_id=site.pk,
                                                         content_type=ContentType.objects.get_for_model(Entry),)

        if created:
            statistics["zinnia_new"] += 1
        else:
            statistics["zinnia_existing"] += 1

        # Store mapping information between Drupal and Zinnia comments (used
        # later on if setting-up hierarchy for threaded comments).
        comment_mapping[drupal_comment.cid] = comment.pk
        # Store parent/child information for threaded comments.
        hierarchy[drupal_comment.cid] = drupal_comment.pid

    # Update comment parent/child relationships if threaded comments were
    # enabled.
    if threaded_comments:
        for cid, cid_parent in hierarchy.iteritems():
            if cid_parent != 0:
                comment = Comment.objects.get(pk=comment_mapping[cid])
                comment.parent = Comment.objects.get(pk=comment_mapping[cid_parent])
                comment.save()

    # Fix counters.
    zinnia_entry.comment_count = zinnia_entry.comments.count()
    zinnia_entry.pingback_count = zinnia_entry.pingbacks.count()
    zinnia_entry.trackback_count = zinnia_entry.trackbacks.count()
    zinnia_entry.save(force_update=True)

    return statistics


def import_content(drupal, user_mapping, category_mapping, tag_mapping, node_type, threaded_comments):
    """
    Imports content from Drupal into Zinnia. Content is created only if it does
    not exist already.

    Arguments:

      drupal
        Drupal database from which the content should be imported. Should be an
        instance of DrupalDatabase.

      user_mapping
        Mapping between Drupal user ID's and Zinnia user ID's. Generated by
        import_users() function.

      category_mapping
        Mapping between Drupal category ID's and Zinnia category ID's. Generated
        by import_categories() function.

      tag_mapping
        Mapping between Drupal tag ID's and Zinnia tag strings. Generated by
        extract_tags() function.

      node_type
        Drupal node type that should be processed. Only the nodes belonging to
        the specified node type will be processed.

      threaded_comments
        Specify whethere the comments should be imported as threaded or not. If
        set to True, zinnia-threaded-comments application must be installed as
        well.

    Returns:

      Dictionary with import statistics (keys 'drupal_total', 'zinnia_new', and
      'zinnia_existing').
    """

    # Get a list of all nodes of specific type, sorting them by date of
    # creation.
    nodes = drupal.session.query(drupal.Node).filter(drupal.Node.type == node_type,
                                                     drupal.Node.uid.in_(user_mapping.keys())).order_by(drupal.Node.created)

    # Set-up statistics dictionary.
    statistics = {
        "drupal_total": nodes.count(),
        "zinnia_new": 0,
        "zinnia_existing": 0,
        }

    # Process each node.
    for node in nodes:
        # Extract the last revision of the node.
        revisions = drupal.session.query(drupal.NodeRevisions).filter(drupal.NodeRevisions.nid == node.nid)

        # Extract node data.
        last = revisions.order_by(drupal.NodeRevisions.vid.desc()).first()
        body = last.body
        title = last.title
        modified = datetime.fromtimestamp(last.timestamp, pytz.UTC)
        created = datetime.fromtimestamp(node.created, pytz.UTC)
        user = user_mapping[node.uid]

        # Create the entry if it doesn't exist already.
        zinnia_entry, created = Entry.objects.get_or_create(content=body, creation_date=created,
                                                            last_update=modified, title=title,
                                                            status=PUBLISHED, slug=slugify(title))

        if created:
            # Add relations (authors etc).
            zinnia_entry.authors.add(user)
            zinnia_entry.sites.add(Site.objects.get_current())
            zinnia_entry.save()

            # Import tags.
            version_tags = drupal.session.query(drupal.TermNode).filter(drupal.TermNode.nid == last.nid, drupal.TermNode.vid == last.vid).all()
            zinnia_entry.tags = ",".join([tag_mapping[t.tid] for t in version_tags if t.tid in tag_mapping])
            zinnia_entry.save()

            # Set-up categories for entry.
            categories_query = drupal.session.query(drupal.TermNode).filter(drupal.TermNode.nid == last.nid, drupal.TermNode.vid == last.vid)
            categories = [category_mapping[v.tid] for v in categories_query if v.tid in category_mapping]
            zinnia_entry.categories.add(*[c for c in categories])
            zinnia_entry.save()

            # Import comments for an entry.
            import_comments(drupal, node, zinnia_entry, threaded_comments)

            statistics["zinnia_new"] += 1
            print "Imported entry '%s'" % title
        else:
            statistics["zinnia_existing"] += 1
            print "Skipping existing entry '%s'" % title

    return statistics


###########
# Command #
###########
class Command(LabelCommand):
    """
    Implements a custom Django management command used for importing Drupal blog
    into Zinnia.
    """

    help = """
Imports Drupal content into Zinnia.

The command will import the following:

    - User information (username and mail only).
    - Categories.
    - Node content.
    - Node comments (threaded, if using zinnia_threaded_comments).

Currently the script has the following limitations:

    - No conversion of additional user information is performed.
    - No conversion of formatting is performed. Content is copied as-is.
    - Supports only MySQL-compatible database.
    - Revision history is not preserved (Django Blog Zinnia does not support
      revision history). Only the latest/current revision will be imported.
    - Comment _titles_ are not preserved (Django Blog Zinnia does not support
      comment titles)
"""

    option_list = LabelCommand.option_list + (
        make_option("-H", "--database-hostname", type="string", default="localhost",
                    help="Hostname of database server providing the Drupal database. Default is 'localhost'."),
        make_option("-p", "--database-port", type="int", default=3306,
                    help="TCP port at which the database server is listening. Default is '3306'."),
        make_option("-u", "--database-username", type="string", default="root",
                    help="Username that should be used for connecting to database server. Default is 'root'."),
        make_option("-P", "--database-password", type="string", default=None,
                    dest="database_password_file",
                    help="Path to file containing the password for specified database username. If not set (default), the password will be read interactively."),
        make_option("-n", "--node-type", type="string", default="blog",
                    help="Drupal Node type that should be processed. Default is 'blog'."),
        make_option("-m", "--user-mapping", type="string", action="callback",
                    callback=create_mappingaction("user_mapping"), default=dict(),
                    help="Mapping of Drupal usernames to Zinnia usernames. Format is 'duser1=zuser1:duser2=zuser2:...:dusern=zusern'. Default is to use same username as in Drupal."),
        make_option("-U", "--users", type="string", default=None,
                    help="Comma-separated list of Drupal users that should be imported, including user-created content. Default is to import content from all users."),
        make_option("-t", "--threaded-comments", action="store_true",
                    default=False, dest="threaded_comments",
                    help="Import comments while preserving threading information. Requires zinnia-threaded-comments application. Default is not to use threaded comments."),
        )

    def handle_label(self, database_name, **options):
        # Read the password for Drupal database if it wasn't provided within a file.
        if options['database_password_file']:
            options['database_password'] = open(options['database_password_file'], "r").read().rstrip().lstrip()
        else:
            options['database_password'] = getpass.getpass("Database password for '%s'@'%s': " % (options['database_username'], database_name))

        # Set-up SQLAlchemy ORM.
        database_connection_url = "mysql://%s:%s@%s/%s" % (urllib.quote(options['database_username']),
                                                           urllib.quote(options['database_password']),
                                                           urllib.quote(options['database_hostname']),
                                                           urllib.quote(database_name))
        engine = create_engine(database_connection_url)
        drupal = DrupalDatabase(engine)

        # Create list of users that should be imported.
        users = options["users"]
        if users:
            users = users.split(",")

        # Disconnect Zinnia signals.
        disconnect_discussion_signals()
        disconnect_entry_signals()

        # Import the users.
        user_stats, user_mapping = import_users(drupal, users=users, custom_mapping=options["user_mapping"])
        # Import the categories.
        category_stats, category_mapping = import_categories(drupal)
        # Extract the tag mapping.
        tag_mapping = extract_tags(drupal)
        # Finally, import the actual content.
        content_stats = import_content(drupal, user_mapping, category_mapping, tag_mapping, options['node_type'], options["threaded_comments"])

        # Output a summary.
        print
        print "User import summary"
        print "==================="
        for key, value in user_stats.iteritems():
            print "%s: %s" % (key, value)

        print
        print "Category import summary"
        print "======================="
        for key, value in category_stats.iteritems():
            print "%s: %s" % (key, value)

        print
        print "Content import summary"
        print "======================"
        for key, value in content_stats.iteritems():
            print "%s: %s" % (key, value)
