from models import GroupStat
from vkontakte_groups.factories import GroupFactory
import factory

class GroupStatFactory(factory.DjangoModelFactory):
    FACTORY_FOR = GroupStat

    group = factory.SubFactory(GroupFactory)