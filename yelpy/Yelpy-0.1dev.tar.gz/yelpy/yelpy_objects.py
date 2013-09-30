
class YelpyList(list):

    def __str__(self):
        return unicode(self).encode("utf-8")

    def __unicode__(self):
        return ",".join(self)
