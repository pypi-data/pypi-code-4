def pytest_addoption(parser):
    group = parser.getgroup('general')
    group.addoption('--paste-file', action='store',
                    help='Path to a paste config file used to setup the test environment')
