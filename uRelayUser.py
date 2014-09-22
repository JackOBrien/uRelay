import socket

print "PLease print this"

class User(object):
	username = ""
	op = False
	group = None
	socket = None

	def __init__(self, sock, name):
		self.socket = sock
		self.username = name

	def getName(self):
		return self.username

	def addGroup(self, new_group):
		self.group = new_group

	def getGroup(self):	
		return self.group

	def inGroup(self):
		if not self.group:
			return False
		return True

	def __str__(self):
		return self.username
