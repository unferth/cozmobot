#!/usr/bin/env python

class ChannelManager:
    """ this module performs channel maintenance functions """
    def __init__(self, bot):
        self.bot = bot
        self.bot.register_handler("kick", self.handle_kick)
        self.bot.register_handler("join", self.handle_join)
        self.bot.register_handler("welcome", self.handle_welcome)

    def handle_welcome(self, connection, event):
        """ join channels when we connect to the server """
        for channel in self.bot.config.CHANNELS:
            connection.join(channel)

    def handle_kick(self,connection,event):
        """ rejoin on kick """
        whonick=self.bot.nm_to_n(event.source())
        userhost=self.bot.nm_to_uh(event.source())
        message=event.arguments()[0]
        channel=event.target()
        victim=event.arguments()[0]
        reason=event.arguments()[1]
        if victim == self.bot.config.NICKNAME:
            connection.join(channel)

    def handle_join(self, connection, event):
        """ perform actions when users join """
        whonick=self.bot.nm_to_n(event.source())
        try:
            print self.bot.interfaces["get_user"](whonick).__dict__
        except:
            pass
        if whonick == self.bot.config.NICKNAME:
            # self joining
            pass

