from BeautifulSoup import BeautifulSoup
from babel.numbers import get_currency_symbol
import formencode
from hnc.forms import formfields
from hnc.forms.formfields import StringField, TextareaField, IntField, HtmlAttrs
from hnc_forms_ext.media_helpers import getSlideshareMeta, getYoutubeMeta, getVimeoMeta


class CurrencyIntField(IntField):
    template = "hnc_forms_ext:templates/currencyint.html"
    def getCurrency(self, request):
        return request.context.company.currency

    def getCurrencySymbol(self, request):
        return get_currency_symbol(self.getCurrency(request), locale='en_US')

class PictureUploadField(formfields.StringField):
    template = "hnc_forms_ext:templates/pictureupload.html"
    group_classes='file-upload-control'
    mime_types = ['image/*']
    picWidth = 100
    picHeight = 100

    def getInputAttrs(self, request):
        attrs = self.attrs.getInputAttrs(request)
        #attrs += 'data-pic-width="{0.picWidth}" data-pic-height="{0.picHeight}"'.format(self)
        return attrs

class FileUploadField(PictureUploadField):
    template = "hnc_forms_ext:templates/fileupload.html"

class PictureGalleryUploadField(formfields.StringField):
    template = "hnc_forms_ext:templates/multifileupload.html"
    group_classes='multi-file-upload-control'
    def getValidator(self, request):
        return {self.name: formencode.ForEach(url = formencode.validators.String(required=True))}

class HTMLString(formencode.validators.String):
  messages = {"invalid_format":'There was some error in your HTML!'}
  valid_tags = ['a','strong', 'em', 'p', 'ul', 'ol', 'li', 'br', 'b', 'i', 'u', 's', 'strike', 'font', 'pre', 'blockquote', 'div', 'span', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']
  valid_attrs = ['size', 'color', 'face', 'title', 'align', "style"]

  def sanitize_html(self, html):
      soup = BeautifulSoup(html)
      for tag in soup.findAll(True):
          if tag.name.lower() not in self.valid_tags:
              tag.extract()
          elif tag.name.lower() != "a":
              tag.attrs = [attr for attr in tag.attrs if attr[0].lower() in self.valid_attrs]
          else:
              attrs = dict(tag.attrs)
              tag.attrs = self.linkAttrs(attrs)
      val = soup.renderContents()
      return val.decode("utf-8")

class RemoveHtmlString(formencode.validators.String):
  def sanitize_html(self, html):
      soup = BeautifulSoup(html)
      result = ''
      for tag in soup.findAll(True):
          if tag.name.lower() not in self.valid_tags:
              result+=tag.extract()
      return result

class SanitizedHtmlField(TextareaField):
    _validator = HTMLString

class CleanHtmlField(StringField):
    _validator = RemoveHtmlString

class SlideShareUrl(formencode.validators.String):
    messages = dict(
        tooLong='Enter a value not more than %(max)i characters long',
        tooShort='Enter a value %(min)i characters long or more',
        notSlideshareUrl = "Please add a valid slideshare url. You can find it in the sharing options of the presentation."
    )
    def _to_python(self, value, state):
        result = super(SlideShareUrl, self)._to_python(value, state)

        if not getSlideshareMeta(state, value):
            raise formencode.api.Invalid(
                self.message('notSlideshareUrl', state, max=self.max), value, state)
        else: return result

class SlideshareField(StringField):
    _validator = SlideShareUrl



class VideoUrl(formencode.validators.String):
    messages = dict(
        tooLong='Enter a value not more than %(max)i characters long',
        tooShort='Enter a value %(min)i characters long or more',
        notVideoUrl = "Please add a valid youtube or vimeo url. You can find it in the browser address bar when watching the video."
    )
    def _to_python(self, value, state):
        result = super(VideoUrl, self)._to_python(value, state)

        meta  = getYoutubeMeta(state, value) or getVimeoMeta(state, value)
        if not meta:
            raise formencode.api.Invalid(
                self.message('notVideoUrl', state, max=self.max), value, state)
        else: return result

class VideoUrlField(StringField):
    _validator = VideoUrl





class UniqueNameField(StringField):
    group_classes = "username-input-group"
    template = "hnc_forms_ext:templates/uniquename.html"
    def get_domain(self, request):
        return request.context.settings.site_root_url

    def __init__(self, name, label=None, thing_name="name", data_rule_remote="/signup/isavailable", **kwargs):
        attrs = HtmlAttrs(required = True, data_rule_remote=data_rule_remote, data_msg_required="Please enter a {} to proceed".format(thing_name), placeholder="Enter {} here".format(thing_name))
        super(UniqueNameField, self).__init__(name, label, attrs, **kwargs)

