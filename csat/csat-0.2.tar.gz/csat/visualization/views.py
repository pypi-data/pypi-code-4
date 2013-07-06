from django.views.generic import base


class StandaloneRenderingView(base.TemplateView):
    template_name = 'csat/visualization/viewer.html'

standalone_viewer = StandaloneRenderingView.as_view()
