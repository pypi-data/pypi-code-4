# -*- coding:utf-8 -*-
#!/usr/bin/env python
# Authors:
# Torsten Irlaender <torsten.irlaender@intevation.de>

import sys
import logging
import argparse

from ringo.scripts.helpers import get_package_name
from ringo.lib.helpers import get_app_location

log = logging.getLogger(name=__name__)


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Administration command for a ringo based application")
    parser.add_argument("command", type=str, help="Command to be executed",
                        choices=["syncdb", "add-modul", "del-modul"])
    parser.add_argument("--config", dest="configuration",
                        help="Configuration (ini) of the application",
                        required=True)

    args = parser.parse_args()
    package = get_package_name(args.configuration)

    print get_app_location(package)
    return sys.exit(1)

if __name__ == "__main__":
    main()
