from django import forms
from django.utils.translation import ugettext as _
from radpress.models import Article, EntryImage, Page, Tag
from radpress.readers import get_reader, get_reader_initial
from radpress.settings import DEFAULT_MARKUP
from radpress.templatetags.radpress_tags import radpress_zen_mode_url


class PageForm(forms.ModelForm):
    class Meta:
        model = Page


class ZenModeForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ('content', 'markup')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(ZenModeForm, self).__init__(*args, **kwargs)

        markup = getattr(self.instance, 'markup', DEFAULT_MARKUP)
        content = self.fields['content']
        content.widget = forms.Textarea(attrs={'class': 'zen-mode-textarea'})
        content.initial = get_reader_initial(markup=markup)

        # if user doesn't add radpress urls to it's project, it will be empty
        # url.
        zen_mode_url = radpress_zen_mode_url(self.instance)
        if zen_mode_url:
            help_text = _("You can also edit with <a href='%s'>zen mode</a>.")
            content.help_text = help_text % zen_mode_url

    def clean_content(self):
        field = self.cleaned_data.get('content')
        reader = get_reader(markup=self.data.get('markup'))
        self.content_body, self.metadata = reader(field).read()
        slug = self.metadata.get('slug')

        if self.metadata.get('title') is None or slug is None:
            msg = _("Title or slug can not be empty.")
            raise forms.ValidationError(msg)

        if (self.instance.pk is None
                and Article.objects.filter(slug=slug).exists()):

            msg = _("Slug should be unique.")
            raise forms.ValidationError(msg)

        return field

    def save(self, **kwargs):
        title = self.metadata.get('title')
        slug = self.metadata.get('slug')
        content = self.cleaned_data.get('content')
        is_published = self.metadata.get('published')
        image_id = self.metadata.get('image', '')

        if self.instance.pk is not None:
            article = self.instance
        else:
            article = Article(author=self.user)

        article.title = title
        article.slug = slug
        article.content = content
        article.content_body = self.content_body
        article.is_published = is_published
        article.markup = self.data.get('markup')

        # update cover image if it specified
        try:
            image = EntryImage.objects.get(id=int(image_id))
        except (EntryImage.DoesNotExist, ValueError, TypeError):
            image = None
        article.cover_image = image

        # save article
        article.save()

        # reset tags
        article.articletag_set.all().delete()
        for tag_name in self.metadata.get('tags'):
            tag = Tag.objects.get_or_create(name=tag_name)[0]
            article.articletag_set.create(tag=tag)

        return article

    def save_m2m(self):
        # TODO: this method added for fixing admin form error. But why we need
        # to this method, i don't know. Please find better way to solve this
        # problem.
        pass
