#!/usr/bin/env python2.7
# message.py
# created by Andrew Quinn and Jared Gray 

import sys

class Message: 
	'''A protocol-complaint message from a client or peered server.'''
	
	def __init__(self):
		self.prefix     = ""
		self.cmd        = ""
		self.params     = {}
        
	def parse_input(self,in_msg):
		assert isinstance(in_msg,str)
		
		words = in_msg.spit()    # words from the message
		i = 0                    # current index in words
		
		#if the first word begins with a ':', then we have a prefix
		if words[0][0] == ":" :
			i += 1
			self.prefix = words[0]
			
if __name__ == "__main__":
	print "%s should not be run directly" %sys.argv[0]
	sys.exit(1)