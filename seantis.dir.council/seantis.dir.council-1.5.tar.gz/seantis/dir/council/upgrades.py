from seantis.dir.base.upgrades import reset_images, add_behavior_to_item
from seantis.dir.council.directory import ICouncilDirectory
from seantis.dir.council.item import ICouncilDirectoryItem


def upgrade_to_1000(context):

    reset_images(context, (ICouncilDirectory, ICouncilDirectoryItem))
    add_behavior_to_item(
        context, 'seantis.dir.council', ICouncilDirectoryItem
    )
