"""
Search indexes for Haystack.

"""
from haystack import indexes

from weblog.models import Post


class PostIndex(indexes.SearchIndex, indexes.Indexable):
    """Index for :class:`~weblog.models.Post`.

    """
    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField(model_attr='title')
    pub_date = indexes.DateTimeField(model_attr='pub_date')

    def get_model(self):
        return Post

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return Post.published.all()
