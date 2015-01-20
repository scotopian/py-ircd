#The client_recv class is the thread that receives data from the client-side
# by: Andrew Quinn and Jared Gray

import threading

from globals import G
from modes import Modes
import message
import peer
import client 

import socket 
import sys

class Client_Recv(threading.Thread):
	
	def __init__(self, c):
		assert isinstance(c, client.Client)
		
		threading.Thread.__init__(self)
		self.client = c             #The client associated with this thread
	

	def run(self):
		pass

	