import socket

class User(object):
	username = ""
	op = False
	group = None
	socket = None

	# Constructor for User
	def __init__(self, sock, name):
		self.socket = sock
		self.username = name

	# Returns the name of the user
	def getName(self):
		return self.username

	# Sets the user's group
	def addGroup(self, new_group):
		self.group = new_group

	# Returns the user's group
	def getGroup(self):	
		return self.group

	# Tells if the user is in a group
	def inGroup(self):
		if not self.group:
			return False
		return True

	# Sets whether or not the user is an operator
	def setOp(self, p):
		self.op = p

	# Tells if the user is an operator
	def isOp(self):
		return self.op

	# Returns the name of the user to represent
	# the object as a string
	def __str__(self):
		return self.username
