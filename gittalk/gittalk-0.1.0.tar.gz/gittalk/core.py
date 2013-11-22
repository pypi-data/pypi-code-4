#!/usr/bin/env python
# coding: utf-8

import sys
import subprocess
import pyttsx as px

# Initializes the engine for blasting audio
engine = px.init()


def say(text='This is so cool', rate_adjust=-50, volume_adjust=0):
    '''
    Says an English text, with any adjust rate and/or volume
    '''
    # Adjusts the property
    rate = engine.getProperty('rate')
    engine.setProperty('rate', rate+rate_adjust)
    volume = engine.getProperty('volume')
    engine.setProperty('volume', volume+volume_adjust)

    # Says the text and voila!
    engine.say(text)
    engine.runAndWait()


def say_last_commit():
    '''
    Says the last commit, if there's one.
    If not, let the user knows :p
    '''
    try:
        line = subprocess.check_output(["git", "log", "-1",
                                        "HEAD", "--pretty=format:%s"])
        say(line)
    except subprocess.CalledProcessError:
        say('Not a git repository, or you have not made at\
            least one commit yet')


def say_last_push():
    '''
    Ideally, this should say what the repo's name is, the remote's
    name (origin, heroku, etc.), and which branch is pushed
    (master, gh-pages, etc.)
    '''
    raise NotImplementedError('Would a kind soul please help me with this?')


def main():
    '''
    There will be a time when more git commands are supported,
    but for now, running main will just say the last commit :(
    '''
    say_last_commit()


if __name__ == '__main__':
    sys.exit(main())
