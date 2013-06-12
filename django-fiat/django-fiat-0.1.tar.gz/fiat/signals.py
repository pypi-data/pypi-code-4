from django.utils.text import slugify

def slugger(sender, instance, **kwargs):
    obj = instance
    if not obj.slug:
        counter = 0
        slug = slugify(obj.title)
        while sender.objects.filter(slug=slug).exists():
            counter =+ 1
            slug = u"%s-%i" % (slugify(obj.title), counter)
        else:
            obj.slug = slug