#!/usr/bin/env python2.7
# channel.py
# created by Andrew Quinn and Jared Gray

import client
import modes
import sys

class Channel: 
	'''An individual channel on our network.'''
	
    def __init__(self, name):
        self.name  = name    # name of the channel 
        self.users = {}      # all of the users who are in the channel 
        self.modes = {}      # all of the modes belonging to the channel
        self.op    = {}      # operators of the channel

if __name__ == "__main__":
	print "%s should not be run directly" %sys.argv[0]
	sys.exit(1)