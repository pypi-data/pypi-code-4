import argparse
from .app import runserver


def run():
    parser = argparse.ArgumentParser(description='Run a web server for VU.')
    parser.add_argument('--port', dest='port', default='8000',
                        help="HTTP port"),
    args = parser.parse_args()
    runserver(args)


if __name__ == "__main__":
    run()
