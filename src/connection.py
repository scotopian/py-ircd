#!/usr/bin/env python2.7
# connection.py
# created by Andrew Quinn and Jared Gray

from globals import G
from cqueue import CQueue
import client
import peer

import errno
import socket
import sys
import threading
import time

# To-Do's:
# 1. Ensure that client nicks contain valid characters only.
# 2. Reset timeout and num_missed for each cmd received.
# 3. Verify that the server-server stuff is OK.
# 4. Buffer client msgs so can process multiple cmds per call to socket.recv().

class Connection(threading.Thread):
	'''A generic connection object. This is created when the TCP connection 
	   is first set-up, and eventually will generate either a Client or a 
	   Peer, depending on what sits behind the connection.'''
	
	# static (class) variables
	conn_type   = {"INVALID" : 0, "PEER" : 1, "CLIENT" : 2}
	conn_cmds   = {"PASS" : 0, "NICK" : 1, "QUIT" : 2, "SERVER" : 3, "USER" : 4}
	MSG_MAX     = 512 # IRC-defined max message length
	BUFF_MAX    = 10  # maximum number of messages to buffer
	HEARTBEAT   = 60  # number of seconds to wait between PINGs
	MISSED_MAX  = 3   # maximum number of "missed" heartbeats
	
	def __init__(self, sock):
		assert isinstance(sock, socket.socket)
		threading.Thread.__init__(self)
		
		self.sock       = sock                       # socket w/ connection
		self.type       = self.conn_type["INVALID"]  # type of connection
 		self.timeout    = self.HEARTBEAT             # seconds left in heartbeat
 		self.num_missed = 0                          # consecutive heartbeats
 		
		# server fields
		self.peername   = ""   # name of connecting server (must be unique)
		self.passwd     = ""   # password field from PASS
		
		# client fields (RFC 2812)
		self.nick       = ""  # nickname of the client (unique)
		self.realname   = ""
		self.modes      = ""
		
		self.verified   = False # stop main loop once we are done connecting

	def cmd_nick(self, msg):
		'''Implements IRC NICK command.'''
		
		command = msg.split()
		if len(command) < 2:
			if G.DEBUG: sys.stderr.write("Invalid NICK command length\n")
		
		if self.type == self.conn_type["PEER"]:
			if G.DEBUG: sys.stderr.write("A peer tried to use NICK\n")
		
		else:
			self.nick = command[1]
			self.type = self.conn_type["CLIENT"]				
			
			self.verify_client()

	def cmd_pass(self, msg):
		'''Implements IRC PASS command. '''
		
		command = msg.split()
		if len(command) < 2:
			if G.DEBUG: sys.stderr.write("Invalid PASS command length\n")
		
		if self.type != self.conn_type["INVALID"]:
			if G.DEBUG: sys.stderr.write("PASS should come before anything\n")
		
		else:
			self.passwd = command[1]
			self.type   = self.conn_type["PEER"]

	def cmd_pong(self, msg):
		'''Implements IRC PONG command.'''
		self.timeout    = self.HEARTBEAT
		self.num_missed = 0
		
	def cmd_user(self, msg):
		'''Implements IRC USER command. (RFC 2812)'''
		
		command = msg.split()
		if len(command) < 5:
			if G.DEBUG: sys.stderr.write("Invalid USER command length\n")
			return
		
		if command[4][0] != ':' or len(command[4]) < 2:
			if G.DEBUG: sys.stderr.write("Realname formatted incorrectly':'\n")
			return
			
		if self.type == self.conn_type["PEER"]:
			if G.DEBUG: sys.stderr.write("Server peer tried to USER\n")
			return
		
		else:
			self.nick     = command[1]
			self.modes    = command[2]
			# words[3] is apparently unused
			self.realname = command[4][1:]
			for i in range(5, len(command)):
				self.realname += command[i]
			self.type     = self.conn_type["CLIENT"]
			
			self.verify_client()

	def cmd_server(self, msg):
		'''Implements IRC SERVER command.'''
		
		command = msg.split()
		if len(command) < 2:
			if G.DEBUG: sys.stderr.write("Invalid SERVER command length\n")
			return
		
		if self.type != self.conn_type["PEER"]:
			if G.DEBUG: sys.stderr.write("SERVER command used too early\n")
			return
		
		else:
			self.peername = msg.split()[1]
			self.verify_peer()
	
	def cmd_quit(self):
		'''Implements IRC QUIT command.'''
		self.conn_type = self.conn_type["INVALID"]
		self.terminate()

	def process_cmd(self, msg):
		msg = self.strip_prefix(msg)
		
		command = msg.split()[0]
		if len(command) == 0:
			if G.DEBUG: sys.stderr.write("No commands to process!\n")
			return
		if G.DEBUG: sys.stderr.write("Got command: [%s]\n" %str(command))
		
		if command.upper() in self.conn_cmds:
			if command.upper() == "USER":
				self.cmd_user(msg)
			elif command.upper() == "NICK":
				self.cmd_nick(msg)
			elif command.upper() == "QUIT":
				self.cmd_quit(msg)
			elif command.upper() == "SERVER":
				self.cmd_server(msg)
			elif command.upper() == "PONG":
				self.cmd_pong(msg)
			else:
				if G.DEBUG: sys.stderr.write("This shouldn't happen.\n")
				sys.exit(1)
				
		else:
			if G.DEBUG: 
				sys.stderr.write("Got invalid command [%s]\n" %repr(msg))
				
	def run(self):
		'''Process commands from the client.'''
		
		CQ = CQueue(self.MSG_MAX * self.BUFF_MAX)
		temp = ""
		
		while self.verified == False:
			try:
				temp = self.sock.recv(CQ.capacity - CQ.size)
			except socket.error, e:
				if G.DEBUG: 
					sys.stderr.write("Socket [%s] experienced error [%s]\n"\
					                %(str(self.sock.getsockname()), str(e)))
				if (e[0] == errno.ETIMEDOUT):
					self.timeout -= self.sock.gettimeout()
				else:
					self.type = self.conn_type["INVALID"]
					self.terminate()
				continue
			
			CQ.store(temp, len(temp))
			
			for msg in CQ.get_msgs():
				self.process_cmd(msg)
			
			time.sleep(1) # thread might run < once/sec, so we're generous here
			self.timeout -= 1
			if (self.timeout <= 0):
				try:
					self.sock.sendall("PING\r\n")
				except socket.error, e:
					if G.DEBUG: 
						sys.stderr.write("Socket [%s] experienced error [%s]\n"\
										%(str(self.sock.getsockname()), str(e)))
					if (e[0] == errno.ETIMEDOUT):
						self.timeout -= self.sock.gettimeout()
					else:
						self.type = self.conn_type["INVALID"]
						self.terminate()
					continue
				
				self.timeout = 60
				self.num_missed += 1
				if (self.num_missed >= self.MISSED_MAX):
					self.type = self.conn_type["INVALID"]
					self.terminate()
	
	def strip_prefix(self, msg):
		command = msg.split()
		if len(command) > 1 and command[0][0] == ':':
			msg = ""
			for i in range(1, len(command)):
				msg += command[i]
		
		return msg
	
	def terminate(self):
		self.verified = True
		
		with G.connections_lock:
			del G.connections[self]
		
		# can I rely on garbage collection to clean this up on timeout?
		
	def verify_client(self):
		if G.DEBUG: sys.stderr.write("Verifing client %s\n" %self.nick)
		assert self.type == self.conn_type["CLIENT"]
		if self.nick == "" or self.realname == "":
			return False	
		with G.clients_lock:
			if self.nick in G.clients:
				return False
			G.clients[self.nick] = client.Client(self, None)
		
			G.clients[self.nick].send_thread.start()
			G.clients[self.nick].recv_thread.start()
		self.terminate()
	
	def verify_peer(self):
		if G.DEBUG: sys.stderr.write("Verifing peer %s\n" %self.peername)
		assert self.type == self.conn_type["PEER"]
		with G.peers_lock:
			if self.peername in G.peers:
				return False
			if self.passwd != G.passwd_str:
				return False
			G.peers[self.peername] = peer.Peer(self, None)
			G.peers[self.peername].start()
		self.terminate()
	
if __name__ == "__main__":
	print "%s should not be run directly" %sys.argv[0]
	sys.exit(1)
		