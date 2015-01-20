#!/usr/bin/env python2.7
# client.py
# created by Andrew Quinn and Jared Gray 

import threading

from globals import G
from modes import Modes
import connection
import message
import peer
import socket 
import sys

import client_recv
import client_send

# it would be awesome to get this to inherit the Connection's actual thread!
class Client(): 
	'''An individual connected client (not a peered server).'''
	
	'''This should really be thought of as a sort-of shared data between the 
	   Client_recv and the Client_send classes. These two classes implement 
	   the two different threads we need to run. We need to decide where we 
	   should put some of the fields. i.e. do we want to assign fields such
	   as in_msg or out_msg to this class, or should those two be defined in
	   the two thread client classes where they seem more relevent... I choose
	   here because it will make the code more readable for later things. '''
	
	# static/class variables
	MSG_MAX = 512
	
	def __init__(self, conn, peer):
		assert isinstance(conn, connection.Connection)
		if peer is not None: # a None peer means the client is locally connected
			assert isinstance(peer, peer.Peer)
		
		self.nick     = conn.nick # nickname of the client
		self.server   = peer      # server the client is connected to
		self.sock     = conn.sock # socket we use to connect locally to client
		self.in_msg   = ""        # incoming message from the client
		self.channels = {}        # list of channels to which the client belongs
		self.modes    = {}        # modes that the client has
		
		self.out_msg  = ""        # message going out to the client 
		self.msg_ready = False    #A bool for msg_out filled 
		
		#the two threads associated with this client: 
		self.send_thread = client_send.Client_Send(self)
		self.recv_thread = client_recv.Client_Recv(self)
		
		#locks and condition variables for the outgoing message. 
		
		self.msg_lock = threading.Lock()       #A lock for out_msg
		self.can_send = threading.Condition(self.msg_lock)  #A cv for ready to send
		self.can_load = threading.Condition(self.msg_lock)  #A cv for ready to load
		
		
		for ch in conn.modes: # we need to authenticate ops...
			if ch in Modes.user_modes:
				self.modes[ch] = None
		
		if G.DEBUG: sys.stderr.write("Welcome client %s!\n" %self.nick)
		
		# that's all for now~

if __name__ == "__main__":
	print "%s should not be run directly" %sys.argv[0]
	sys.exit(1)
