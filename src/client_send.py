#The client_recv class is the thread that receives data from the client-side
# by: Andrew Quinn and Jared Gray

import threading

import message
import client 
import socket 
import sys

class Client_Send(threading.Thread):
	
	def __init__(self, c):
		assert isinstance(c, client.Client)
		
		threading.Thread.__init__(self)
		self.client = c                  #The client associated with this thread
	
	
	'''called by other threads (or this one) to give the client_send a message to send. 
	   This has to be done in a synchronous manner, which is the reason for the locks/cv's'''
	def give(self, msg):
		assert(self.client.server is None) #can only send messages to clients with which we are connected 
		
		self.client.can_load.aquire()
		while self.client.msg_ready:
			self.client.can_load.wait()
				
		self.client.out_msg = msg
		self.client.msg_ready = True
		self.client.can_send.notify()
		self.client.can_load.release()

	def run(self):
		 
		while True:   #this may need to change
			
			'''handle the possibility that out_msg has been filed'''
			self.client.can_send.acquire()
			while not self.client.msg_ready:
				self.client.can_send.wait()
					
			self.client.sock.sendall(self.client.out_msg)
			self.client.out_msg = None
			self.client.msg_ready = False
			self.client.can_load.notify()
			self.client.can_send.release()

	
