from django.utils.datastructures import SortedDict
import csv


class CsvImportTool(object):
    model = None
    fields = []
    aliases = {}

    def register_aliases(self, name, aliases):
        for alias in aliases:
            self.aliases[alias] = name

    def get_or_create(self, values):
        return self.model.objects.create()

    def save_model(self, instance, values):
        instance.save()

    def finished(self, instance, values):
        pass

    def import_from_file(self, file_object):
        self.errors = []
        for idx, row in enumerate(csv.reader(file_object)):
            if idx == 0:
                headers = []
                for header in row:
                    header = header.strip().replace(" ", "_")
                    headers.append(self.aliases.get(header, header))
            else:
                for idx, value in enumerate(row):
                    row[idx] = value.strip()
                values = dict(zip(headers, row))

                instance = self.get_or_create(values)

                # before save
                for header in headers:
                    if header in self.fields:
                        func = self._import_property
                    else:
                        func = getattr(self, "import_%s" % header, None)

                    if func:
                        func(instance, values, header)

                self.save_model(instance, values)

                for header in headers:
                    func = getattr(self, "import_%s_after" % header, None)

                    if func:
                        func(instance, values, header)

                self.finished(instance, values)

    # import functions
    def _import_property(self, instance, values, name):
        setattr(instance, name, values[name])


class CsvExportTool(object):
    fields = ["id", "__unicode__"]

    def export(self, queryset):
        self.errors = []

        rows = []

        # add headers
        headers = []
        for field in self.fields:
            if "." in field:
                headers.append(field.rsplit(".", 1)[-1])
            else:
                headers.append(field)
        rows.append(headers)

        # add records
        for instance in queryset:
            row = []
            self.cache = {}
            for field in self.fields:
                attr = getattr(self, "export_%s" % field, None)
                if not attr:
                    attr = instance
                    for bit in field.split("."):
                        attr = getattr(attr, bit, None)
                        if not attr:
                            break

                if callable(attr):
                    attr = attr()

                row.append(attr)
            rows.append(row)

        return rows

    def export_file(self, queryset, file):
        writer = csv.writer(fileh)
        writer.writerows(self.export(queryset))
