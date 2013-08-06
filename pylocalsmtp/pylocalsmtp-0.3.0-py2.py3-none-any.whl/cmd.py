import argparse
from .app import runserver


def run():
    parser = argparse.ArgumentParser(description='Run a web server and a local SMTP server.')
    parser.add_argument('--bind', dest='http_bind', default='127.0.0.1:8888',
                        help="default HTTP binding"),
    parser.add_argument('--smtp', dest='smtp_bind', default='127.0.0.1:1025',
                        help="default SMTP binding"),
    args = parser.parse_args()
    runserver(args)


if __name__ == "__main__":
    run()
