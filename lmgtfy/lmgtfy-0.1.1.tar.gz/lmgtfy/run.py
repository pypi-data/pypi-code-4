from lmgtfy import Lmgtfy
import requests
import sys
import os


def google_it(query):
    lmgtfyer = Lmgtfy()
    print "Lmgtfy url:", lmgtfyer.lmgtfy_url(query)
    try:
        short_url = lmgtfyer.short_url(query)
        print "Short url :", short_url
        os.system("echo '" + short_url + "' | xclip -sel clip")
        print "Short url copied to clipboard"

    except requests.exceptions.ConnectionError:
        print "No Internet connection"


def command_line_runner():
    if len(sys.argv) == 1:
        sys.exit("Error: too few arguments")
    google_it(sys.argv[1:])


if __name__ == "__main__":
    command_line_runner()
