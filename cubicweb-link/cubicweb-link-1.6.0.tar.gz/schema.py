from yams.buildobjs import EntityType, RelationType, String, Boolean, RichString
_ = unicode

class Link(EntityType):
    """a link to an external internet resource"""
    title = String(required=True, fulltextindexed=True, maxsize=256)
    url = String(required=True, fulltextindexed=True, maxsize=512,
                 description=_("link's url"))
    embed = Boolean(default=False,
                    description=_("generate links to embed the page by default?"))
    description = RichString(fulltextindexed=True,
                         description=_("description of the linked page's content"))

class embed(RelationType):
    __permissions__ = {'read': ('managers', 'users', 'guests'),
                       'update': ('managers',),
                       }
