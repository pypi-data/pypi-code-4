from django.contrib import admin

from polymorphic.admin import PolymorphicParentModelAdmin
from polymorphic.admin import PolymorphicChildModelAdmin

from csat.acquisition import get_collectors, models


class AcquisitionSessionConfigAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'started', 'completed', 'temporary',
                    'status')
admin.site.register(models.AcquisitionSessionConfig,
                    AcquisitionSessionConfigAdmin)


class DataCollectorConfigAdmin(PolymorphicChildModelAdmin):
    base_model = models.DataCollectorConfig


class GenericDataCollectorConfigAdmin(PolymorphicParentModelAdmin):
    list_display = ('id', 'name', 'session_config')
    base_model = models.DataCollectorConfig

    def get_child_models(self):
        def iter_chldren():
            for collector in get_collectors():
                yield (collector.get_model(), DataCollectorConfigAdmin)

        return tuple(iter_chldren())

admin.site.register(models.DataCollectorConfig,
                    GenericDataCollectorConfigAdmin)
