from random import randint

class Group(object):
	
	group_name = "Group #%d" % randint(1, 512)
	group_users = {}

	# Constructor
	def __init__(self, name):
		self.group_name = name

	def add_user(self, socket, user):
		print "--Group add user--"
		self.group_users[socket] = user
		message = "~~%s joined %s~~\n" % (user, self.group_name)
		self.group_broadcast(socket, message)
	
	def remove_user(self, socket):
		user = self.group_users[socket]
		message = "~~%s disconnected~~\n" % user
		self.group_broadcast(socket, message)
		del self.group_users[socket]

	def group_broadcast(self, sender, message):
		print "--Group Broadcast--"
		for socket in self.group_users:
			if socket != sender:
				try:
					print "--Trying to send message--"
					socket.send("\n{%s} %s" % (
						self.group_users[sender], message))
				except:
					print "--Trying to remove user--"
					self.remove_user(socket)
	def getName(self):
		return self.group_name
