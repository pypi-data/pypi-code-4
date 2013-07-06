from django_assets import env


def layout_workers(request):
    workers = []
    for name, bundle in env.get_env()._named_bundles.iteritems():
        if name.startswith('worker_'):
            name = name.split('_', 1)[1].rsplit('_', 1)[0]
            workers.append((name, bundle.urls()[0]))
    return {
        'layout_workers': workers
    }
