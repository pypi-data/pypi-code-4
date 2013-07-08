from haystack import site, indexes
from djinn_announcements.models.announcement import Announcement
from djinn_announcements.models.serviceannouncement import ServiceAnnouncement
from pgsearch.base import ContentRealTimeSearchIndex


class AnnouncementIndex(ContentRealTimeSearchIndex):

    """ Index for announcements """

    def index_queryset(self):

        return self.model.objects.filter(serviceannouncement__isnull=True)


class ServiceAnnouncementIndex(AnnouncementIndex):

    def index_queryset(self):

        return self.model.objects.all()


site.register(Announcement, AnnouncementIndex)
site.register(ServiceAnnouncement, ServiceAnnouncementIndex)
