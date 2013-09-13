from django.contrib import admin

from .models import Artist, Genre


class ArtistAdmin(admin.ModelAdmin):
    search_fields = ('^name', '^genre__name')

admin.site.register(Artist, ArtistAdmin)


class GenreAdmin(admin.ModelAdmin):
    search_fields = ('^name',)

admin.site.register(Genre, GenreAdmin)
