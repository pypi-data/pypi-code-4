'''
Copyright 2012 Research Institute eAustria

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

@author: Marian Neagul <marian@ieat.ro>
@contact: marian@ieat.ro
@copyright: 2012 Research Institute eAustria
'''

import sys
import argparse
import logging

def main():
    try:
        pos = sys.argv.index("--")
        args = sys.argv[:pos]
        command = sys.argv[pos + 1:]
    except ValueError:
        args = sys.argv
        command = []
    args = args[1:]

    parser = argparse.ArgumentParser(description = 'CLI for mOSAIC Deployer engine')
    parser.add_argument("--url", "-l", type = str, default = None, help = 'The url to the server')
    parser.add_argument('--interactive', '-i', action = "store_true", default = False, help = "Run the interactive shell")
    parser.add_argument('--verbose', '-v', action = 'count', default = 1, help = "The verbosity level. More v's means more logging")
    args = parser.parse_args(args)

    # Setup logging
    if args.verbose > 4:
        log_level = 10
    else:
        log_level = 50 - args.verbose * 10

    rootLogger = logging.getLogger('')
    del rootLogger.handlers[:] # Clean handlers
    handler = logging.StreamHandler()
    handler.setLevel(log_level)
    formatter = logging.Formatter('[ %(levelname)-8s %(filename)s:%(lineno)d (%(name)s) ] --> %(message)s')

    handler.setFormatter(formatter)
    rootLogger.addHandler(handler)

    log = logging.getLogger("cli")

    import cli as cli_ui
    cli = cli_ui.CliHandler()

    import pipes
    command = [pipes.quote(c) for c in command]
    command = " ".join(command)

    if args.url is not None:
        cli.onecmd("connect --uri %s" % args.url)
    if args.interactive:
        if not sys.stdin.isatty():
            log.warn("Warning the console is not a tty")
        cli.cmdloop()
    else:
        if len(command) == 0:
            parser.print_help()
            return 1
        else:
            cli.onecmd(command)

if __name__ == "__main__":
    main()
