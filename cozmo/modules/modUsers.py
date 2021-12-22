#!/usr/bin/env python

import UserDict
import re
import anydbm
import os
import cPickle

class _User:
    def __init__(self, nick, flags, hostmask, attr_dict={}):
        self.nick = nick
        self.flags = flags
        self.hostmask = hostmask
        self.attr_dict = attr_dict
        
class UserManager:
    """ this module provides an interface to the DBM user database """
    def __init__(self, bot):
        self.bot = bot
        self.bot.provide_interface("get_user", self.get_user)
        self.bot.provide_interface("add_user", self.add_user)
        self.bot.provide_interface("num_users", self.num_users)
        self.db = None
        # open the database, creating it if it doesn't exist 
        if os.path.exists("benzo.users"):
            try:
                self.db = anydbm.open("benzo.users", 'w')
            except:
                os.remove("benzo.users")
                self.db = anydbm.open("benzo.users", 'c')
        else:
            self.db = anydbm.open("benzo.users", 'c')

    def add_user(self, nick, flags, hostmask):
        """ add a user with the specified flags to the userdb """
        userobj = cPickle.dumps(_User(nick, flags, re.compile(hostmask)))
        self.db[nick] = userobj
        self.db.sync()
        
    def get_user(self, username):
        """ return a User instance if one exists """
        if not self.db.has_key(username): return None
        return cPickle.loads(self.db[username])

    def num_users(self):
        return len(self.db.keys())
