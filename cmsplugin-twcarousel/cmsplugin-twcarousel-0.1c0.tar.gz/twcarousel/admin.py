from django.contrib import admin
from .models import Slide, Carousel


class SlideInline(admin.StackedInline):
    model = Slide


class CarouselAdmin(admin.ModelAdmin):
    inlines = [
        SlideInline
    ]

admin.site.register(Carousel, CarouselAdmin)
