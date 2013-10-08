import sys
from utils import Message
from hub import HubController
from build import GridBuilder


def fail(message):
    Message.fail(message)
    sys.exit(1)


def ok(message):
    Message.ok(message)


def info(message):
    Message.ok(message)


def warning(message):
    Message.warning(message)


def nodes(subject, argv):

    if len(argv) == 0:
        fail("Missing node action")

    action = argv.pop(0)
    if action == 'add':
        if len(argv) == 0:
            fail("Missing browser, use phantomjs|firefox")

        browser = argv.pop(0)
        if not HubController.is_valid_browser(browser):
            fail("Invalid browser please use phantomjs|firefox")

        info("Adding node...")
        status = HubController.add(browser)
        if not status:
            fail("Failed to start node")

        ok("Node Added Successfully!")

    elif action == 'stop':
        info("Stopping nodes...")
        HubController.stop_nodes()
        ok("Nodes stopped")
    elif action == 'restart':
        info("Restarting nodes...")
        browser = None
        if len(argv) == 1 and not HubController.is_valid_browser(argv.pop(0)):
            fail('Restarting by browser requires either phantomjs or firefox')

        HubController.restart_nodes(browser)
        ok("Nodes restarted")
    elif action == 'rebuild':
        print "Rebuild Nodes optional by browser"
    else:
        fail("Unknown node action: " + action)


def rebuild(subject, argv):
    fail("TODO: Rebuild the Hub and Browsers")



def start(subject, argv):
    if HubController.is_running():
        warning("Hub already running")
        sys.exit(1)

    info("Starting up grid...")
    status = HubController.start()
    if not status:
        fail("Hub failed to start")
        sys.exit(1)
    ok("Hub is Ready!")


def shutdown(subject, argv):
    if not HubController.is_running():
        fail("Hub is not running")
        sys.exit(1)
    info("Shutting down grid...")
    HubController.shutdown()


def grid_status(subject, argv):
    if not HubController.is_running():
        ok("Grid is not running")
        sys.exit(1)
    grid = HubController.get_status()
    ok("GridIP: " + grid['Ip'] + ' Firefox Nodes: ' + str(grid['firefox_count']) + ' PhantomJS Nodes: ' + str(grid['phantomjs_count']))


def unknown(option, argv):
    Message.fail("Unknown Option: " + option)
    sys.exit(1)


def install(option, argv):
    builder = GridBuilder()
    if builder.is_installed():
        fail("Already installed")

    info("Building Selenium Grid, PhantomJS, and Firefox Containers...please be patient")
    info("Installing Selenium Hub...")
    builder.build('selenium-hub')
    ok("Selenium Hub Container Installed")
    info("Installing Firefox...")
    builder.build('firefox')
    ok("Firefox container installed")
    info("Installing PhantomJS...")
    builder.build('phantomjs')
    ok("PhantomJS container installed")
    ok("Selenium Grid is installed!")


def main():
    if len(sys.argv) < 2:
        print "dsgrid <subject> [action]"
        sys.exit(1)

    argv = sys.argv[1:]
    subject = argv.pop(0)
    {
        "nodes": nodes,
        "start": start,
        "shutdown": shutdown,
        "status": grid_status,
        "install": install

    }.get(subject, unknown)(subject, argv)


if __name__ == "__main__":
    main()
