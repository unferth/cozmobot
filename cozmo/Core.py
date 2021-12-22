#!/usr/bin/env python

import sys
sys.path.append('./irclib-0.3.1')
import ircbot
import Config
import os
import glob
import imp
from types import ClassType
from irclib import nm_to_n, nm_to_uh

VERSION="benzo-0.3 http://www.sourceforge.net/projects/benzo"

class Benzo(ircbot.SingleServerIRCBot):
    def __init__(self):
        self.version = VERSION
        self.config = Config
        # this is hackish - find away for events to expose this themselves
        self.nm_to_n = nm_to_n
        self.nm_to_uh = nm_to_uh
        ircbot.SingleServerIRCBot.__init__(self, self.config.SERVER_LIST,
                                         self.config.NICKNAME,
                                         self.config.REALNAME)

        self.event_dict = {}    # dict of event->(priority, handler)
        self.modules = {}       # dict of handler modules
        self.interfaces = {}    # dict of module-provided interfaces
        self.init_modules()
        self.connection.add_global_handler("all_events",
                                           self.dispatcher, -10)

    def dispatcher(self, connection, event):
        """ dispatch events to handlers. """
        # TODO:  abstract away from the irclib 'event' and 'connection classes
        #        to provide a more high-level interface to modules. pubmsg
        #        and privmsg are 99% of what this bot deals with, so make those
        #        easy to work with

        # lets not doubly dispatch events
        if event.eventtype() == "all_raw_messages": return
        if self.event_dict.has_key(event.eventtype()):
            handler_list = self.event_dict[event.eventtype()]
            # sort the handler list by priority - lowest wins
            handler_list.sort()
            # print "Got %d handlers for %s" % (len(handler_list),
            #                                      event.eventtype())
            # call all the handlers until we're done or one returns "NO MORE"
            for handler in handler_list:
                # print "Applying ",
                # print handler
                pass
                if(apply(handler[1], (connection, event)) == "NO MORE"):
                    return "NO MORE"
                    
    def init_modules(self):
        """ load handler modules """
        modglob = "%s/%s" % (self.config.MODULE_DIR, 'mod*.py')
        for file in glob.glob(modglob):
            # create a module object from file
            mod = imp.load_source(file, file, open(file))
            for name in dir(mod):
                if name[:1] == "_" : continue # hidden classes begin with "_"
                object = getattr(mod, name)
                if type(object) != ClassType: continue # not a class
                print "Instantiating ",
                print object
                try:
                    # instantiate handler class with a reference to the bot
                    self.modules[file] = object(self)
                except:
                    print "Exception while instantiating ",
                    print sys.exc_info()[1]
                    print object

    def register_handler(self, eventtype, handlerfunc, priority=0):
        """ handler modules call this to register to recieve events """
        if not self.event_dict.has_key(eventtype):
            self.event_dict[eventtype] = []
        self.event_dict[eventtype].append((priority, handlerfunc))

    def provide_interface(self, name, function):
        """ handler modules call this to provide interfaces to other modules"""
        self.interfaces[name] = function

    def on_ctcp(self, connection, event):
        """ we override this to prevent irclib from answering too """
        pass
    
if __name__ == "__main__":
    x = Benzo()

