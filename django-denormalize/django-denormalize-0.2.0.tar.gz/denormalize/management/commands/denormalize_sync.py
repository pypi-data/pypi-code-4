from django.core.management.base import BaseCommand, CommandError

from ...backend.base import BackendBase

class Command(BaseCommand):

    args = '<backend_name> <collection_name_1> [collection_name_2] [...]'
    help = "Run sync_collection on given backend and collection"

    def handle(self, *args, **options):
        if not args:
            self.stdout.write("No backend name specified. The following ones "
                              "are currently registered by name:\n")
            names = sorted(BackendBase._registry.keys())
            for name in names:
                self.stdout.write(" - {0}\n".format(name))
            raise CommandError("Specify a backend name")

        backend_name = args[0]
        try:
            backend = BackendBase._registry[backend_name]
        except KeyError:
            raise CommandError("No backend with name '{0}' found".format(backend_name))

        collection_names = args[1:]
        valid_names = sorted(backend.collections.keys())
        invalid_passed_names = set(collection_names) - set(valid_names)

        if not collection_names or invalid_passed_names:
            self.stdout.write("No collection names specified. The following ones "
                "are currently registered to this backend:\n")
            for name in valid_names:
                self.stdout.write(" - {0}\n".format(name))
            if invalid_passed_names:
                raise CommandError("Invalid collection names: {0}".format(
                    ' '.join(sorted(invalid_passed_names))))
            else:
                raise CommandError("Specify one or more collection names")

        # Now let's do some work

        self.stdout.write("Using backend {0} ({1})\n".format(
            backend_name, backend.__class__.__name__))

        for name in collection_names:
            self.stdout.write("Syncing collection {0}\n".format(name))
            collection = backend.collections[name]
            backend.sync_collection(collection)

        self.stdout.write('Done.\n')