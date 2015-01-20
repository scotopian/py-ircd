#!/usr/bin/env python2.7
# globals.py
# created by Andrew Quinn and Jared Gray

import random
import sys
import threading

class G:
	'''Data we must maintain and use frequently throughout implementation.
	   Locks must be held on variables that can change and are thus not
	   thread-safe.'''
	
	usage_str  = ""        # filled in later by main() since it has argv
	passwd     = "boobies" # plaintext password
	
	serv_name        = "cpServe: " + str(random.randint(0, 2000000000))
	seen_timestamps  = [] # timestamps we have seen before
	
	peers       = {}     # server_names -> server obj
	channels    = {}     # strings      -> channels
	clients     = {}     # nicks        -> clients
	connections = {}     # list of connections (hashing beats linear search!)
	
	peers_lock       = threading.Lock()    # peers dictionary lock
	channels_lock    = threading.Lock()    # channels dictionary lock
	clients_lock     = threading.Lock()    # clients dictionary lock
	connections_lock = threading.Lock()    # connections dictionary lock

	DEBUG = True # print debug messages to stderr
		
if __name__ == "__main__":
	print "%s should not be run directly" %sys.argv[0]
	sys.exit(1)