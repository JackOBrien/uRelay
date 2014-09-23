class Group(object):
	
	group_users = {}

	# Constructor
	def __init__(self, name):
		self.group_name = name
		self.group_users = {}

	# Adds user to group
	def add_user(self, socket, user):
		self.group_users[socket] = user
		message = "~~%s joined %s~~\n" % (user, self.group_name)
		self.group_broadcast(socket, message)
	
	# Removes user from group
	def remove_user(self, socket):
		user = self.group_users[socket]
		message = "~~%s disconnected~~\n" % user
		self.group_broadcast(socket, message)
		del self.group_users[socket]

	# Messages the entire group
	def group_broadcast(self, sender, message):
		print "~~Broadcasting to %s: %s" % (
			self.group_name, self.group_users[sender])
		for socket in self.group_users:
			if socket != sender:
				try:
					socket.send("\n{%s} %s" % (
						self.group_users[sender], message))
				except:
					self.remove_user(socket)

	# Returns the name of this group
	def getName(self):
		return self.group_name

	# Retuns the list of users in this group
	def getUsers(self):
		return self.group_users
