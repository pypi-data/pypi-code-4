# encoding: utf-8

class BaseModel(object):
    """
    The base model for all the clien models.
    Has a __getattr__ method for dynamic methods
    """
    def __init__(self, client, data, *args, **kwargs):
        self.client = client
        self.data = data

    def __getattr__(self, method_name):
        if method_name in self.data:
            return self.data[method_name]

        raise AttributeError("'%s' object has no attribute '%s'" % (self.__class__.__name__, method_name))

class Site(BaseModel):
    """
    """
    def __init__(self, client, data, *args, **kwargs):
        self.data = data
        self.client = client

class Section(BaseModel):
    """
    Section model.
    Has the same structure of the API.
    See here: http://cms.pull4up.com.br/api/v1/docs/

    Use:
        my_section = section(<id>)

        my_section.<property>
    """
    @property
    def banners(self):
        banners = []
        for banner_url in self.data['banners']:
            banners.append(self.client.call_from_url(Banner, banner_url))

        return banners

    @property
    def forms(self):
        forms = []
        for form_url in self.data['forms']:
            forms.append(self.client.call_from_url(Form, form_url))

        return forms

    @property
    def contents(self):
        contents = []
        for content_url in self.data['contents']:
            contents.append(self.client.call_from_url(Content, content_url))

        return contents

    @property
    def seo(self):
        if self.data['seo']:
            return Seo(self.data['seo'])

        return []

    @property
    def childrens(self):
        childrens = []
        for children in self.data['childrens']:
            childrens.append(self.client.call_from_url(Section, children['url']))

        return childrens


class Content(BaseModel):
    """
    Model for the contents
    Has the same structure of the API.
    See here: http://cms.pull4up.com.br/api/v1/docs/
    """
    @property
    def author(self):
        if self.data['author']:
            return Author(self.data['author'])

    @property
    def content_type(self):
        if self.data['content_type']:
            return ContentType(self.data['content_type'])

    @property
    def images(self):
        images = []
        for image in self.data['images']:
            images.append(Image(image))

        return images

    @property
    def seo(self):
        if self.data['seo']:
            return Seo(self.data['seo'])

        return []

class Form(BaseModel):
    """
    Model for the Forms
    Has the same structure of the API.
    See here: http://cms.pull4up.com.br/api/v1/docs/
    """
    @property
    def fields(self):
        fields_list = []
        for field in self.data['fields']:
            fields_list.append(Field(field))

        return fields_list

    @property
    def post_url(self):
        return self.data['actions_urls']['post_url']

    @property
    def validate_url(self):
        return self.data['actions_urls']['validate_url']


class Field(BaseModel):
    """
    Model for the form fields.
    """
    def __init__(self, data, *args, **kwargs):
        self.data = data

class Author(BaseModel):
    """
    Model for the content author
    """
    def __init__(self, data, *args, **kwargs):
        self.data = data

class ContentType(BaseModel):
    """
    Model for the content content_type
    """
    def __init__(self, data, *args, **kwargs):
        self.data = data

class Seo(BaseModel):
    """
    Model for the content, section and site SEO
    """
    def __init__(self, data, *args, **kwargs):
        self.data = data

class Image(BaseModel):
    """
    Model for the content images
    """
    def __init__(self, data, *args, **kwargs):
        self.data = data

class Banner(BaseModel):
    """
    Model for the Banners
    """
    @property
    def section(self):
        return self.client.call_from_url(Section, self.data['section'])

    def thumbnail(self, width = None, height = None, crop = None):
        url = '%s?width=%d&height=%d&crop=%s' % (self.data['url'], width, height, crop)

        return self.client.call_from_url(Banner, url)

    @property
    def crop(self):
        try:
            return self.data['image']['crop']
        except:
            raise TypeError('You must generate thumbnail first')

    @property
    def width(self):
        try:
            return self.data['image']['width']
        except TypeError:
            raise TypeError('You must generate thumbnail first')

    @property
    def height(self):
        try:
            return self.data['image']['height']
        except TypeError:
            raise TypeError('You must generate thumbnail first')

    @property
    def image(self):
        try:
            return self.data['image']['image']
        except TypeError:
            return self.data['image']

ALLOWED_MODELS = {
''          : Site,
'section'   : Section,
'sections'  : Section,
'banner'    : Banner,
'banners'   : Banner,
'content'   : Content,
'contents'  : Content,
'form'      : Form,
'forms'     : Form,
}