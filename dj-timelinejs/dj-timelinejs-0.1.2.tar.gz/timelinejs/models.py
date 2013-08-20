import markdown, datetime
from django.db import models
from django.utils import simplejson as json, html
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse

from .utils import markdown_linkify

# Create your models here.

TITLE = 't'
ERA = 'e'
NORMAL = 'n'
ITEM_TYPE_CHOICES = (
        (TITLE, 'Title',),
        (ERA, 'Era',),
        (NORMAL, 'Normal',),
)
VIEW_PRIVATE_TIMELINES_PERM = 'timelinejs.view_private_timelines'

data_source_help_text = "Leave blank unless you are using a Google Spreadsheet."
class TimelineManager(models.Manager):
    def visible_to_user(self, user=None):
        filter_kwargs = {'published': True}
        if user is None or not user.has_perm(VIEW_PRIVATE_TIMELINES_PERM):
            filter_kwargs['private'] = False
        return self.filter(**filter_kwargs)

    def get_visible_to_user_or_404(self, user=None, **kwargs):
        kwargs['published'] = True
        if user is None or not user.has_perm(VIEW_PRIVATE_TIMELINES_PERM):
            kwargs['private'] = False
        return get_object_or_404(Timeline, **kwargs)

class Timeline(models.Model):
    data_source = models.URLField(max_length=255, null=True, blank=True, help_text=data_source_help_text)
    title = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True)
    private = models.BooleanField(default=False)
    published = models.BooleanField(default=True)

    objects = TimelineManager()

    class Meta:
        permissions = (
                (VIEW_PRIVATE_TIMELINES_PERM.split('.')[1], 'Can see published, private timelines.'),
        )

    def get_absolute_url(self):
        return reverse('timeline', kwargs={'slug': self.slug})

    def __unicode__(self):
        return self.title

    @property
    def source(self):
        if self.timelineitem_set.all().count():
            return self.process_to_json()
        else:
            return '"%s"' % self.data_source

    def process_to_json(self):
        parser = TimelineParser(self.timelineitem_set.all())
        parser.parse()
        return parser.get_json()

    def load_items_from_json(self, item_json):
        importer = TimelineImporter(item_json, self)
        errors = importer.import_items()
        return errors



item_type_help_text = "You must have one and only one title slide. You may use multiple era slides."
class TimelineItem(models.Model):
    timeline = models.ForeignKey(Timeline, blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    item_type = models.CharField(max_length=1, choices=ITEM_TYPE_CHOICES, default=NORMAL, help_text=item_type_help_text)
    headline = models.TextField(default="", blank=True)
    _headline = models.TextField(default="", blank=True, help_text="Processed headline")
    text = models.TextField(default="", blank=True, help_text="Feel free to use Markdown syntax. Your title slide **must** have text in order to show up.")
    _text = models.TextField(default="", blank=True, help_text="Processesed text.")
    tag = models.CharField(max_length=255, null=True, blank=True, help_text="You may use up to six tags per timeline.")
    _tag = models.CharField(max_length=255, null=True, blank=True, help_text="Processed tag.")
    media = models.CharField(max_length=255, null=True, blank=True, help_text="Enter an external link. If you are using the Media Upload field this will be filled in automatically.")
    _media = models.CharField(max_length=255, null=True, blank=True, help_text="Processed media.")
    media_upload = models.FileField(upload_to="timelinemedia", max_length=250, blank=True, null=True)
    media_caption = models.CharField(max_length=255, null=True, blank=True)
    _media_caption = models.CharField(max_length=255, null=True, blank=True, help_text="Processed caption.")
    media_credit = models.CharField(max_length=255, null=True, blank=True)
    _media_credit = models.CharField(max_length=255, null=True, blank=True, help_text="Processed credit.")
    media_thumbnail = models.CharField(max_length=255, null=True, blank=True, help_text="Must be a link to an image no bigger than 32x32 pixels.")
    _media_thumbnail = models.CharField(max_length=255, null=True, blank=True, help_text="Processed thumbnail.")

    def _process_date(self, d):
        return "%d,%d,%d" % (d.year, d.month, d.day)

    def process_to_json_dict(self):
        json_dict = {'startDate': self._process_date(self.start_date),}
        if self.end_date:
            json_dict['endDate'] = self._process_date(self.end_date)
        if self.headline:
            json_dict['headline'] = self._headline
        if self.text:
            json_dict['text'] = self._text
        if self.text:
            json_dict['tag'] = self._tag
        if self.media:
            asset = {'media': self._media}
            if self.media_caption:
                asset['caption'] = self._media_caption
            if self.media_credit:
                asset['credit'] = self._media_credit
            if self.media_thumbnail:
                asset['thumbnail'] = self._media_thumbnail
            json_dict['asset'] = asset
        return json_dict

    def save(self, *args, **kwargs):
        # process text attributes
        self.process_fields()
        # need to super first so we generate the real filename to get the true
        # url for the media
        super(TimelineItem, self).save(*args, **kwargs)
        self._set_media_from_media_upload(*args, **kwargs)

    def process_fields(self):
        # process the text attributes
        escaped_attrs = ['headline', 'text', 'tag', 'media', 'media_caption', 'media_credit', 'media_thumbnail']
        for attr in escaped_attrs:
            attr_val = getattr(self, attr, None)
            if attr_val:
                setattr(self, '_' + attr, html.escape(attr_val))
        if self._text:
            self._text = markdown.markdown(markdown_linkify(self._text))

    def _set_media_from_media_upload(self, *args, **kwargs):
        if self.media_upload and self._media != html.escape(self.media_upload.url):
            self.media = "%s%s" % (settings.FULLY_QUALIFIED_DOMAIN, self.media_upload.url)
            self._media = html.escape(self.media)
            super(TimelineItem, self).save(*args, **kwargs)

    def load_from_object(self, obj):
        obj.load_into_timeline_item(self)
        self.process_fields()


class TimelineParser(object):
    """
    Takes an iterable of TimelineItems and returns parsed json.
    """
    def __init__(self, items):
        self.items = items
        self.processed_items = None
        self.timeline = None
        self.has_title_item = False

    def parse(self):
        # set up root
        self.timeline = {'timeline': 
                {
                    'type': 'default',
                    'date': [],
                    'era': [],
                },
        }
        for item in self.items:
            self.add_item(item)

    def add_item(self, item):
        root = self.timeline['timeline']
        processed = item.process_to_json_dict()
        if item.item_type == TITLE:
            # skip extra title items
            if self.has_title_item:
                root['date'].append(processed)
            else:
                root.update(processed)
                self.has_title_item = True
        elif item.item_type == ERA:
            root['era'].append(processed)
        elif item.item_type == NORMAL:
            root['date'].append(processed)

    def get_json(self):
        if self.timeline is None:
            self.parse()
        return json.dumps(self.timeline)

class TimelineImporter(object):

    def __init__(self, item_json, timeline=None):
        self.item_json = item_json
        self.timeline = timeline


    def _parse_timeline_date(self, d):
        try:
            split = [int(i) for i in d.split()[0].split('/')]
            if len(split) != 3:
                return None
            return datetime.date(int(split[2]), int(split[0]), int(split[1]))
        except:
            pass

    def import_items(self):
        errors = []
        items = json.loads(self.item_json)
        root = items['timeline']
        # create title slide
        title_props = {'item_type': TITLE, 'timeline': self.timeline}
        title_props.update(self._get_basic_props(root))
        title_props.update(self._get_media_props(root))
        TimelineItem.objects.create(**title_props)

        # create era slides
        for era_slide in root.get('era', []):
            try:
                era_props =  {'item_type': ERA, 'timeline': self.timeline}
                era_props.update(self._get_basic_props(era_slide))
                TimelineItem.objects.create(**era_props)
            except Exception, e:
                errors.append('Failed to parse Era entry with headline "%s" so it was omitted. Error was %s.' % (era_slide.get('headline', '<No Headline>'), e))

        # create normal slides
        for normal_slide in root.get('date', []):
            try:
                normal_props =  {'item_type': NORMAL, 'timeline': self.timeline}
                normal_props.update(self._get_basic_props(normal_slide))
                normal_props.update(self._get_media_props(normal_slide))
                TimelineItem.objects.create(**normal_props)
            except Exception, e:
                errors.append('Failed to parse entry with headline "%s" so it was omitted. Error was %s.' % (normal_slide.get('headline', '<No Headline>'), e))
        return errors

    def _get_basic_props(self, obj):
        props = {
                'start_date': self._parse_timeline_date(obj['startDate']),
        }
        props['end_date'] = self._parse_timeline_date(obj.get('endDate', None))
        props['headline'] = obj.get('headline', '')
        props['text'] = obj.get('text', '')
        props['tag'] = obj.get('tag', None)
        return props

    def _get_media_props(self, obj):
        props = {}
        if obj.has_key('asset'):
            asset = obj['asset']
            # should throw an error if we don't have a media value
            props['media'] = asset['media']
            props['media_caption'] = asset.get('caption', None)
            props['media_credit'] = asset.get('credit', None)
            props['media_thumbnail'] = asset.get('thumbnail', None)
        return props
