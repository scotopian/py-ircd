#!/usr/bin/env python2.7
# modes.py
# created by Andrew Quinn and Jared Gray

import sys

class Modes: 
	'''Convenience data class for channel and user modes.
	   For now, these are all _pure_ RFC modes.'''

	user_modes    = ('i', 's', 'w', 'o')
	user_desc     = {'i' : "invisible",
	                 's' : "receives server notices",
	                 'w' : "receives wallops",
	                 'o' : "user is an IRC operator"}
	
	# some channel modes are flags, others are associated with complex data
	chan_modes    = ('o', 's', 'p', 'n', 'm', 'i', 't', 'l', 'b', 'v', 'k')
	chan_desc     = {'o' : "channel operator (list of users)",
	                 's' : "secret channel (flag)",
	                 'p' : "private channel (flag)",
	                 'n' : "users must be in channels to msg it (flag)",
	                 'm' : "moderated: only voiced and ops can speak (flag)",
	                 'i' : "channel joining is invitation-only (flag)",
	                 't' : "only operators can change the topic (flag)",
	                 'l' : "a limit exists on # of occupants (integer)",
	                 'b' : "channel bans (list of users)",
	                 'v' : "channel voice (list of users)",
	                 'k' : "user must provide key to enter channel (string)"}

if __name__ == "__main__":
	print "%s should not be run directly" %sys.argv[0]
	sys.exit(1)