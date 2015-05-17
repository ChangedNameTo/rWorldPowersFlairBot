#!/usr/bin/env python3

import praw
import sys
import os
from time import gmtime, strftime
try:
    from flair_list import flairs
except ImportError as e:
    print("Flairs file can't be accessed\n")
    print(e)
    sys.exit()
except SyntaxError as e:
    print("There is a syntax error in the flair list\n")
    print(e)
    sys.exit()


class FlairBot:

    # User agent that PRAW uses to identify your bot to reddit
    USER_AGENT = 'ubuntu:thealpacalypse.me:v1 (run by /u/tehalpacalypse)'
    # User name/password of the account that the bot will run through
    USER_NAME = ''
    PASSWD = ''

    # Blacklist for users abusing the flair system
    BLACKLIST = ['sampleuser', 'sampleUSER2']

    """ The SUBJECT will be the default subject of your PMs
    when you create the URLs, eg.

    reddit.com/message/compose/?to=some_user&subject=flair&message=some_message

    PMs require a subject, but it's also a simple way of identifying
    PMs that are directed towards the flairs and not just a general PM"""
    SUBJECT = 'flair'

    # TARGET_SUB is the name of the subreddit without the leading /r/
    TARGET_SUB = 'worldpowers'

    # Turn on output to log file in current directory - log.txt
    LOGGING = True

    # Class variable to hold the PRAW instance
    r = None

    # Class variable to hold the unread pms
    pms = None

    def init(self):
        if self.LOGGING:
            os.chdir(os.path.dirname(os.path.abspath(__file__)))
        self.login()

    def login(self):
        """ Log in to the account being used for the bot """
        try:
            self.r = praw.Reddit(user_agent=self.USER_AGENT)
            self.r.login(self.USER_NAME, self.PASSWD)
            self.fetch_pms()
        except:
            raise

    def fetch_pms(self):
        """ Get a listing of all unread PMs for the user account """
        self.pms = self.r.get_unread(limit=None)
        if self.pms is not None:
            self.process_pms()

    def process_pms(self):
        for pm in self.pms:
            if str(pm.subject) == self.SUBJECT:
                author = str(pm.author)  # Author of the PM
                if author.lower() in (user.lower() for user in self.BLACKLIST):
                    continue
                content = str(pm.body)  # Content of the PM
                index = content.find(":")
                if index != -1:
                    continue
                newflair = content[:index].strip()# Substrings the PM to get flair only
                subreddit = self.r.get_subreddit(self.TARGET_SUB)
                if newflair in flairs:
                    # Get the flair text that corresponds with the class name
                    flair_text = content[index + 1:].strip()
                    subreddit.set_flair(author, flair_text, newflair)
                    if self.LOGGING:
                        self.log(author, content, flair_text, newflair)
                pm.mark_as_read()  # Mark processed PM as read

    def log(self, author, content, flair_text, newflair):
        with open('log.txt', 'a', encoding="UTF-8") as logfile:
            time_now = strftime("%Y-%m-%d %H:%M:%S", gmtime())
            log_text = 'Added: ' + author + ' : ' \
                + flair_text + ' : ' \
                + newflair + ' @ ' + time_now + ' EST\n'
            logfile.write(log_text)
FlairBot().init()
