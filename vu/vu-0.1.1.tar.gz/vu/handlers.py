from tornado import web
from .helpers import resume_statuses, global_status


class MainHandler(web.RequestHandler):
    def get(self):
        statuses = resume_statuses()
        main_status = global_status(statuses)
        context = {
            "statuses": statuses,
            "main_status": main_status
        }
        self.render("index.html", **context)

