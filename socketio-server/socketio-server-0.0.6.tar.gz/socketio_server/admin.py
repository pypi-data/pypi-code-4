from django.contrib import admin
from models import AsyncTask

class AsyncTaskOptions(admin.ModelAdmin):
    pass

admin.site.register(AsyncTask, AsyncTaskOptions)
