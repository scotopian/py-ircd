#!/usr/bin/env python2.7
# cqueue.py
# created by Andrew Quinn and Jared Gray

import message

import sys

class CQueue: 
	'''A circular queue for indexing a string. Used to buffer messages
	   read in from a socket in an efficient manner.'''

	def __init__(self, capacity):
		'''CQueue constructor: construct a CQueue with a static capacity.
		   pre: capacity is an integer >= 0.'''
		   
		assert isinstance(capacity, int)
		assert(capacity >=0)
		
		self.capacity = capacity               # length of internal string
		self.size     = 0                      # elements in the string
		self.__str    = ["\0"] * self.capacity # underlying list rep of string
		self.__cur    = 0                      # current index of string end
		
	def store(self, in_str, amt):
		'''Store the first amt characters of in_str in our circular string.
		   pre: we have enough space left for "amt" characters. 
		        in_str is a string.'''
		
		assert amt <= self.capacity - self.size
		assert isinstance(in_str, str)
		
		for i in range(amt):
			self.__str[self.__cur] = in_str[i]
			self.__cur  = (self.__cur + 1) % self.capacity
			self.size  += 1
			
		assert self.size <= self.capacity
	
	def __find(self, substr):
		'''Return the first index of the string at which substr is found,
		   -1 otherwise.
		   pre: substr is a string.'''
		   
		assert isinstance(substr, str)
		
		if len(substr) > self.size:
			return -1
		
		for i in range(0, self.size - len(substr) + 1):
			num_matched  = 0
			str_index    = (self.__cur - self.size + i) % self.capacity
			substr_index = 0
			
			while num_matched < len(substr) and \
			      self.__str[str_index] == substr[substr_index]:
				num_matched  += 1
				str_index    = (str_index + 1) % self.capacity
				substr_index += 1
				
			if num_matched == len(substr):
				return str_index - num_matched
				
		return -1
			
	
	def __substr(self, amt):
		'''Return self.__str[cur:cur+amt], accounting for circularity. The
		   substring is removed from self.__str.
		   Pre: there are "amt" characters in the current string.'''

		assert self.__cur < self.capacity
		assert amt <= self.size
		
		s = ""
		start_i = (self.__cur - self.size) % self.capacity
		if start_i + amt >= self.capacity:
			for i in range(start_i, self.capacity):
				s += self.__str[i]
				self.__str[i] = '\0'
			for i in range(0, amt - len(s)):
				s += self.__str[i]
				self.__str[i] = '\0'
		
		else:
			for i in range(start_i, start_i + amt):
				s += self.__str[i]
				self.__str[i] = '\0'
		
		self.size  -= amt
		assert self.size >= 0
		
		return s
	
	def get_msgs(self):
		'''If there are any IRC messages in the string, return a list of them.
		   We remove the contiguous message-substrings from the underlying
		   string in the class. Messages are terminated by a CR.LF. If the
		   queue is totally full, and no messages exist, we return a 1-length
		   list containing whatever was in the queue.'''
		
		assert self.size <= self.capacity
		L = []
		
		index = self.__find("\r\n")
		while index != -1:
			substr_end  = (index + 2) % self.capacity
			substr_size = (substr_end - (self.__cur - self.size)) \
			              % self.capacity
			assert substr_size >= 2 and substr_size <= self.size
			L.append(self.__substr(substr_size))
			index = self.__find("\r\n")
			
		# we need to empty the queue if it gets full, but no messages exist
		if len(L) == 0 and self.size == self.capacity:
			L.append(self.__substr(self.size))
		
		return L

if __name__ == "__main__":
	print "%s should not be run directly" %sys.argv[0]
	sys.exit(1)