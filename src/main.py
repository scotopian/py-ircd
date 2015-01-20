#!/usr/bin/env python2.7
# main.py 
# created by Andrew Quinn and Jared Gray

import hashlib
import os
import signal
import socket
import sys
import time
import threading

# note: "from <lib> import *" syntax is deprecated
from globals import G
import client
import connection
import peer
	
def main():
	'''Main loop for this IRC server.'''
	
	G.usage_str = "Usage: %s <listen_port> [<peer_ip> <peer_port>]" %sys.argv[0]
	H = hashlib.sha512()  # New, empty crypto constructor for SHA512 hash
	peer_ip = ""          # ipv4 address of the peer server to connect with
	timestamp = time.mktime(time.gmtime()) # seconds since epoch
	
	# check to see that argument list is correct length 
	if len(sys.argv) not in (2, 4):
		print G.usage_str
		return 1
	
	# attempt to read port number
	try:
		port = int(sys.argv[1])
	except ValueError:
		print "Invalid listen port number; expected an integer"
		return 1
	
	# connect to the specified peer IRC server
	if len(sys.argv) == 4: 
		# resolve the peer's IP address
		peer_name    = sys.argv[2]
		try:
			peer_ip = socket.gethostbyname(peer_name)
		except:
			print "Error: unable to resolve hostname %s" %peer_name
		
		# get other peer information
		try:
			peer_port   = int(sys.argv[3])
		except ValueError:
			print "Invalid peer port number; expected an integer"
			return 1
		peer_sock   = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		peer_passwd = raw_input("If the peer has a password, enter it here: ")
		
		# store the SHA512 hash of peer_passwd + timestamp
		if peer_passwd != "": 
			H.update(peer_passwd + str(int(timestamp)))
			peer_passwd = H.hexdigest().upper() # only store ciphertext
		
		# not verifying peer_passwd atm, just printing out
		if G.DEBUG: sys.stderr.write(G.passwd_str + ' ' + \
		                             C.hexdigest().upper() + '\n')
		
		C = connection.Connection(peer_sock)
		# attempt a connection
		try:
			if G.DEBUG: sys.stderr.write("Attempting to connect to " + \
			            str(peer_ip) + " " + str(peer_port) + "\n")
			peer_sock.settimeout(60);
			peer_sock.connect((peer_ip, peer_port))
			
			# need to send PASS and SERVER cmds
			# for security, we need to break with RFC and send the timestamp
			# along with the PASS cmd
			peer_sock.sendall("PASS %s %s\r\n" %\
			                 (peer_passwd, str(int(timestamp))))
			peer_sock.sendall("SERVER %s\r\n" %G.serv_name)
			
		except socket.error, e: 
			print "Error: could not connect to: " + str(peer_ip) + \
			       ':' + str(peer_port)
			return 1
		
		print "Connected to: " + str(peer_ip) + ':' + str(peer_port) 
	
	# create listen socket, bind to port number
	try: 
		listen_sock  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		listen_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		listen_sock.bind(('', port))
	except socket.error, e:
		print "Cannot create a socket on port " + str(port) + " : " + str(e)
		return 1
	
	if G.DEBUG: sys.stderr.write(str(listen_sock.getsockname()) + '\n')
	listen_sock.listen(10)
	
	if G.DEBUG: 
		sys.stderr.write("PID: [%d], Listening on port [%s]\n" \
		                %(os.getpid(), str(port)))
	
	# main loop
	while True:
		try:
			conn_sock, conn_addr = listen_sock.accept()
			conn_sock.settimeout(10)
		except socket.error, e:
			if G.DEBUG: sys.stderr.write("warn: aborting a connection accept\n")
			continue
		
		if G.DEBUG: sys.stderr.write("New unknown connection with %s\n" \
		            %str(conn_sock.getsockname()))
		
		c = connection.Connection(conn_sock)
		with G.connections_lock:
			G.connections[c] = None # why do we need this list again?
		c.start()
		
	listen_socket.close()

def shutdown(signal, frame):
	print "Got signal: " + str(signal) + ", exiting"
	sys.exit(0)

# install signal handlers
signal.signal(signal.SIGQUIT, shutdown)
signal.signal(signal.SIGINT, shutdown)

if __name__ == "__main__":
	main()
