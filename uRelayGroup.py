from random import randint

class Group(object):
	
	group_name = "Group #%d" % randint(1, 512)
	group_users = {}

	# Constructor
	def __init__(name):
		group_name = name

	def add_user(socket, user):
		group_users[socket] = user
		message = "~~%s joined %s~~" % (user.getName(), group_name)
		group_broadcast(socket, message)
	
	def remove_user(socket):
		user = group_users[socket]
		del group_users[socket]
		message = "~~%s disconnected~~" % user
		group_broadcast(socket, message)

	def group_broadcast(sender, message):
		for socket in group_users:
			if socket != sender:
				try:
					socket.send("{%s} %s" % (group_users[sender], message))
				except:
					remove_user(socket)
