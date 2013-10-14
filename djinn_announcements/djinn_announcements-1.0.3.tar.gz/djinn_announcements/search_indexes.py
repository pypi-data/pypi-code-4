from haystack import indexes
from djinn_announcements.models.announcement import Announcement
from djinn_announcements.models.serviceannouncement import ServiceAnnouncement
from pgsearch.base import ContentSearchIndex


class AnnouncementIndex(ContentSearchIndex, indexes.Indexable):

    """ Index for announcements """

    def index_queryset(self, using=None):

        return self.get_model()._default_manager.filter(serviceannouncement__isnull=True)

    def get_model(self):

        return Announcement


class ServiceAnnouncementIndex(AnnouncementIndex, indexes.Indexable):

    def index_queryset(self, using=None):

        return self.get_model()._default_manager.all()

    def get_model(self):

        return ServiceAnnouncement

