from django.views.generic import TemplateView
from djinn_announcements.models.announcement import Announcement
from djinn_announcements.models.serviceannouncement import ServiceAnnouncement
from djinn_announcements.settings import SHOW_N_ANNOUNCEMENTS, \
    SHOW_N_SERVICEANNOUNCEMENTS


class AnnouncementViewlet(TemplateView):

    template_name = "djinn_announcements/snippets/announcements_viewlet.html"

    def render_to_response(self, context, **response_kwargs):
        
        return super(AnnouncementViewlet, self).render_to_response(
            context,
            content_type='text/plain',
            **response_kwargs)


    def get_context_data(self, **kwargs):

        ctx = super(AnnouncementViewlet, self).get_context_data(**kwargs)

        ctx['view'] = self

        return ctx

    def announcements(self, limit=SHOW_N_ANNOUNCEMENTS):

        return Announcement.objects.filter(
            priority=0, serviceannouncement__isnull=True)[:limit]


class PriorityAnnouncementViewlet(AnnouncementViewlet):

    template_name = "djinn_announcements/snippets/priority_announcements_viewlet.html"

    def announcements(self):

        try:
            return ServiceAnnouncement.objects.filter(priority=1)[:1]
        except:
            return []


class ServiceAnnouncementViewlet(AnnouncementViewlet):

    template_name = "djinn_announcements/snippets/serviceannouncements_viewlet.html"

    def announcements(self, limit=SHOW_N_SERVICEANNOUNCEMENTS):

        try:
            priority_announcement = ServiceAnnouncement.objects.filter(priority=1)[0].pk
        except:
            priority_announcement = -1

        return ServiceAnnouncement.objects.all(). \
            exclude(pk=priority_announcement).exclude(title="")[:limit]

    @property
    def show_more(self, limit=SHOW_N_SERVICEANNOUNCEMENTS):

        return self.announcements(limit=None).count() > limit
