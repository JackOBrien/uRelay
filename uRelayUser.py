import socket

print "PLease print this"

class User(object):
	username = ""
	op = False
	group = None
	socket = None

	def __init__(self, sock, name):
		print "--We're in USER!!!"
		socket = sock
		username = name

	def getName():
		return username

	def __str__(self):
		return username
