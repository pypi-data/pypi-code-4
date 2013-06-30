import os


def make_package(name, templates):

    with open(os.path.join(templates, '__init__.tpl'), 'r') as f:
        package_text = f.read()

    with open(os.path.join(name, '__init__.py'), 'w') as f:
        f.write(package_text)


def make_application(name, templates):

    with open(os.path.join(templates, 'application.tpl'), 'r') as f:
        application_text = f.read()

    with open(os.path.join(name, 'application.py'), 'w') as f:
        f.write(application_text)


def make_config(name, templates):

    current_user = os.getlogin()

    with open(os.path.join(templates, 'config.tpl'), 'r') as f:
        config_text = (f.read().
                       replace('{{TEMPLATE_USER}}', current_user).
                       replace('{{TEMPLATE_NAME}}', name))

    with open(os.path.join(name, 'config.py'), 'w') as f:
        f.write(config_text)


def make_endpoints(name, templates):

    with open(os.path.join(templates, 'endpoints.tpl'), 'r') as f:
        endpoints_text = (f.read().
                          replace('{{TEMPLATE_ENDPOINT}}',
                                  name.title()
                                  )
                          )

    with open(os.path.join(name, 'endpoints.py'), 'w') as f:
        f.write(endpoints_text)


def make_urls(name, templates):

    with open(os.path.join(templates, 'urls.tpl'), 'r') as f:
        urls_text = (f.read().
                     replace('{{TEMPLATE_ENDPOINT}}', name.title())
                     )

    with open(os.path.join(name, 'urls.py'), 'w') as f:
        f.write(urls_text)


def make_run(name, templates):

    with open(os.path.join(templates, 'run.tpl'), 'r') as f:
        run_text = f.read()

    with open(os.path.join(name, 'run.py'), 'w') as f:
        f.write(run_text)


def make_service_package(name, templates):

    with open(os.path.join(templates, '__init__.tpl'), 'r') as f:
        package_text = f.read()

    with open(os.path.join(name, 'services', '__init__.py'), 'w') as f:
        f.write(package_text)


def make_service_connection(name, templates):

    with open(os.path.join(templates, 'connection.tpl'), 'r') as f:
        connection_text = f.read()

    with open(os.path.join(name, 'services', 'connection.py'), 'w') as f:
        f.write(connection_text)


def make_project(args):

    # Create the project name.
    os.mkdir(args.name)

    # Create the name where services will be installed.
    os.mkdir(os.path.join(args.name, 'services'))

    templates = os.path.join(os.path.dirname(__file__), 'templates')

    make_package(args.name, templates)
    make_application(args.name, templates)
    make_config(args.name, templates)
    make_endpoints(args.name, templates)
    make_urls(args.name, templates)
    make_run(args.name, templates)
    make_service_package(args.name, templates)
    make_service_connection(args.name, templates)
