import os


def make_package(name, directory, templates):

    with open(os.path.join(templates, '__init__.tpl'), 'r') as f:
        package_text = f.read()

    with open(os.path.join(directory, '__init__.py'), 'w') as f:
        f.write(package_text)


def make_models(name, directory, templates):

    with open(os.path.join(templates, 'models.tpl'), 'r') as f:
            models_text = (f.read().
                           replace('{{TEMPLATE_NAME}}', name).
                           replace('{{TEMPLATE_MODEL}}', name.title()))

    with open(os.path.join(directory, 'models.py'), 'w') as f:
            f.write(models_text)


def make_endpoints(name, directory, templates):

    with open(os.path.join(templates, 'endpoints.tpl'), 'r') as f:
            endpoints_text = (f.read().
                              replace('{{TEMPLATE_MODEL}}', name.title()))

    with open(os.path.join(directory, 'endpoints.py'), 'w') as f:
        f.write(endpoints_text)


def make_schema(name, directory, templates):

    with open(os.path.join(templates, 'schema.tpl'), 'r') as f:
        schema_text = f.read().replace('{{TEMPLATE_NAME}}', name)

    with open(os.path.join(directory, 'schema.py'), 'w') as f:
        f.write(schema_text)


def make_urls(name, directory, templates):

    with open(os.path.join(templates, 'urls.tpl'), 'r') as f:
        urls_text = f.read().replace('{{TEMPLATE_NAME}}', name)

    with open(os.path.join(directory, 'urls.py'), 'w') as f:
        f.write(urls_text)


def make_service(args):

    templates = os.path.join(os.path.dirname(__file__), 'templates')
    directory = os.path.join('services', args.name)

    if not os.path.isdir('services'):

        raise Exception("The services directory was not found.\n"
                        "Run this command again from a project directory.")

    os.mkdir(directory)

    make_package(args.name, directory, templates)
    make_models(args.name, directory, templates)
    make_endpoints(args.name, directory, templates)
    make_schema(args.name, directory, templates)
    make_urls(args.name, directory, templates)
