#!/usr/bin/env python

import cPickle
import os
import sys
if os.path.exists("markov.state"):
    print "Theres already a brain in this directory - erase it first"
    sys.exit(1)
    
cPickle.dump({}, open("markov.state", 'w'))
cPickle.dump({}, open("markov.state.1", 'w'))
cPickle.dump({}, open("markov.state.2", 'w'))
cPickle.dump({}, open("markov.state.3", 'w'))
