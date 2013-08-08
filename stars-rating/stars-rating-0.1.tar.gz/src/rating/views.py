### -*- coding: utf-8 -*- ####################################################

from djangoratings.views import AddRatingView

class RatingView(AddRatingView):
    
    def __call__(self, request, score, **kwargs):
        return super(RatingView, self).__call__(request, score=request.REQUEST.get(score), **kwargs)

rating_view = RatingView()
