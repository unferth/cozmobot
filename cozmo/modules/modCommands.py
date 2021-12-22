#!/usr/bin/env python

import string

class CommandHandler:
    def __init__(self, bot):
        self.bot = bot
        self.bot.register_handler("privmsg", self.handle_privmsg)

    def handle_privmsg(self, connection, event):
        """
        interface for /msg commands.  i know the auth code is messy,
        need to fix that soon
        """
        whonick = self.bot.nm_to_n(event.source())
        userhost = self.bot.nm_to_uh(event.source())
        message = event.arguments()[0]
        if self.bot.interfaces["num_users"]() == 0 and message == "hello":
            # no users, brand new bot. 
            self.bot.interfaces['add_user'](whonick, "m", userhost)
            connection.notice(whonick, "hello, new master")
            return
        # check password
        try:
            (password, authmessage) = string.split(message, ' ', 1)
            authmessage = authmessage
        except ValueError:
            password = None
            authmessage = message
        try:
            user = self.bot.interfaces['get_user'](whonick)
        except:
            user = None
        if user is None: return
        if not user.hostmask.search(userhost): return
        # TODO : replace this with is_master and is_op
        if not (("o" in user.flags) or ("m" in user.flags)): return
        if not password == self.bot.config.PASSWORD: return
        # if we get here, we've authenticated
        try:
            (authcmd, authargs) = string.split(authmessage, ' ', 1)
        except ValueError:
            authcmd = authmessage
            authargs = None

        if authcmd == "die":
            self.bot.die("dying, ordered by %s" % whonick)
        
        if authcmd == "nick":
            if authargs:
                self.bot.config.NICKNAME = authargs
                self.bot._nickname = self.bot.config.NICKNAME
                connection.nick(self.bot.config.NICKNAME)
            else:
                connection.notice(whonick, "not enough arguments")

        if authcmd == "adduser":
            try:
                (nick, flags, hostmask) = string.split(authargs, ' ')
                self.bot.interfaces["add_user"](nick, flags, hostmask)
            except ValueError:
                connection.notice(whonick, "not enough arguments")

        if authcmd == "opme":
            if authargs:
                connection.mode(authargs, "+o %s" % whonick)
            

            
