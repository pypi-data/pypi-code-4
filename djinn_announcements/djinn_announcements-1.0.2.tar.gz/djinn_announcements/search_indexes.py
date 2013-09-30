from haystack import indexes
from djinn_announcements.models.announcement import Announcement
from djinn_announcements.models.serviceannouncement import ServiceAnnouncement
from pgsearch.base import ContentSearchIndex


class AnnouncementIndex(ContentSearchIndex):

    """ Index for announcements """

    def index_queryset(self):

        return self.model.objects.filter(serviceannouncement__isnull=True)

    def get_model(self):

        return Announcement


class ServiceAnnouncementIndex(AnnouncementIndex):

    def index_queryset(self):

        return self.model.objects.all()

    def get_model(self):

        return ServiceAnnouncement

