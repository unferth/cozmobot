#!/usr/bin/env python

import string

class MiscFunctionality:
    """ this module provides miscellaneous irc helper functionality """
    def __init__(self, bot):
        self.bot = bot
        self.bot.register_handler("nicknameinuse", self.handle_nicknameinuse)
        self.bot.register_handler("ctcp", self.handle_ctcp)
        
    def handle_nicknameinuse(self, connection, event):
        """ append a '_' to the bots nick if it's in use """
        self.bot.config.NICKNAME = self.bot.config.NICKNAME + "_"
        self.bot._nickname=self.bot.config.NICKNAME
        connection.nick(self.bot.config.NICKNAME)

    def handle_ctcp(self, connection, event):
        """ handle ctcp events """
        # TODO : move this to modCTCP.py 
        whonick = self.bot.nm_to_n(event.source())
        message = string.lower(event.arguments()[0])
        if message == "version":
            connection.notice(whonick, self.bot.version)
        if message == "ping":
            connection.pong(whonick)
            
