#!/usr/bin/env python2.7
# cqueue_test.py
# created by Andrew Quinn and Jared Gray

from cqueue import CQueue

def main():
	CQ = CQueue(10)
	
	s = "hi\r\n\r\n"
	CQ.store(s, len(s))
	print "in: %s, out: %s, post-size %d" %(repr(s), CQ.get_msgs(), CQ.size)
	
	s = "there\r\n"
	CQ.store(s, len(s))
	print "in: %s, out: %s, post-size %d" %(repr(s), CQ.get_msgs(), CQ.size)
	
	s = " " 
	CQ.store(s, len(s))
	print "in: %s, out: %s, post-size %d" %(repr(s), CQ.get_msgs(), CQ.size)
	
	s = "friend"
	CQ.store(s, len(s))
	print "in: %s, out: %s, post-size %d" %(repr(s), CQ.get_msgs(), CQ.size)
	
	s = "\r\n"
	CQ.store(s, len(s))
	print "in: %s, out: %s, post-size %d" %(repr(s), CQ.get_msgs(), CQ.size)
	
	s = "\r\n \r\n\r\n \r\n"
	CQ.store(s, len(s))
	print "in: %s, out: %s, post-size %d" %(repr(s), CQ.get_msgs(), CQ.size)
	
	# Empty the queue if no valid message exists...
	s = "0123456789"
	CQ.store(s, len(s))
	print "in: %s, out: %s, post-size %d" %(repr(s), CQ.get_msgs(), CQ.size)
		
	
if __name__ == "__main__":
	main()