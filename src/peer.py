#!/usr/bin/env python2.7
# server.py
# created by Andrew Quinn and Jared Gray

import threading

import connection

class Peer(threading.Thread): 
	'''A server connected as a peer to our server.'''
	
	def __init__(self, conn):
		assert isinstance(conn, connection.Connection) 
		
		threading.Thread.__init__(self)
		
		self.nick     = ""        # nickname of the server
		self.sock     = conn.sock # socket to connect to client
		self.inMess   = ""        # incoming message from the client
		self.outMess  = ""        # message going out to the client 
		self.channels = {}        # list of channels to which the client belongs
		self.modes    = {}        # modes that the client has 