import socket, select
from uRelayGroup import Group
from uRelayUser import User

users = {}
groups = []
op_pass = "1337"

welcome_message = "Welcome!"

# Sends message to all connected users except sender and users
# in seperate chat rooms
def broadcast_message(sender, message):
	for socket in connected_sockets:
		if socket != server_socket and socket != sender:
			if users[socket].inGroup(): continue
			try:
				sender_name = users[sender].getName()
				socket.send("\n<%s> %s" % (sender_name, message))
			except:
				print "--Except in boradcast"
				logout(socket)
	
# Sends message to every user except sender if true
def global_message(message, sender):
	print "Global from %s: %s" % (users[sender], message)
	for socket in connected_sockets:
		if socket != server_socket:
			if not sender or socket != sender:
				try:
					socket.send(message)
				except Exception as e:
					print e
					logout(socket)

def private_message (receiver, message):
	try:
		receiver.send("%s\n" % message)
	except:
		logout(receiver)

def login_message(new_guy):
	name = users[new_guy]
	print "[%s] Connected to Server" % name
	
	msg = "%s\n\t%s\n------------------" % (
		welcome_message, whos_online())
	private_message(new_guy, msg)

	for socket in connected_sockets:
		if socket != server_socket and socket != new_guy:
			msg = "\n--%s Connected--" % name
			private_message(socket, msg)

# Removes socket 
def logout(socket):
	usr = users[socket]
	if usr.inGroup():
		group = usr.getGroup()
		group.remove_user(socket)
	del users[socket]
	connected_sockets.remove(socket)
	socket.close()
	print "Client %s disconected" % usr

	msg = "\n--%s Disconnected--\n" % usr
	for sock in connected_sockets:
		try:
			if sock != server_socket:
				sock.send(msg)
		except:
			print "--Except in logout--"
			logout(sock)

# Checks for error sockets and logs them out
def check_users():
	r, w, err_sockets = select.select(
		connected_sockets, [], [])

	for socket in err_sockets:
		logout(socket)

# Assembles a list of connected users
def whos_online():
	msg = users.values()[0].getName()
	usr = "User"

	# Handle plurality
	if len(users.values()) > 1:
		usr += 's'
			
		# Assembles list of users
		for i in range(1, len(users.values())):
			u = users.values()[i].getName()

			# Last user in list
			if i == len(users.values()) -1:
				msg += " and " + u
			else:
				msg += ', ' + u

	return "%s: %s Online" % (usr, msg)

# Handles messages starting with '/' or '`*`*'
def handle_commands(socket, command):

	# Sets the username
	if command[:8] == "`*`*name":
		username = command[9:]
		x = User(socket, username)
		users[socket] = x
		login_message(socket)
		return

	print "--Command %s from %s--" % (command[:-1], users[socket])	

	# Displays a list of connected users
	if command[1:5] == 'list':
		msg = whos_online()							
		private_message(sock, msg)

	# Displays a list of commands
	elif command[1:5] == 'help':
		msg = "Commands able to be used on this server are:"
		msg += "\n/list  \t\tDisplays list of users connected to the server"
		msg += "\n/logout\t\tLogs you off of the server"
		msg += "\n/pm    \t\tAllows you to send a private message to a"
		msg += " specified user"
		msg += "\n/creategroup\tAllows you to create and join a user group"
		msg += " with a specified name"
		msg += "\n/cg    \t\tSee /creategroup"
		msg += "\n/join  \t\tAllows you to join a specified group"
		msg += "\n/leave \t\tAllows you to leave your group"
		msg += "\n/groups\t\tDisplays list of groups and their users"
		msg += "\n/global\t\tAllows you to send a message to ALL users"
		
		if users[socket].isOp():
			msg += "\n/kick  \t\tKicks the specified user from the server"
			msg += "\n/op    \t\tPromotes the specified user to"
			msg += " operator user privileges"

		msg += "\n/help  \t\tDisplays this message"

		private_message(socket, msg)

	# Logs out user
	elif command[1:7] == "logout":
		logout(socket)
	
	# Private messages named user
	elif command[1:3] == "pm":
		str_arr = command.split()

		if len(str_arr) < 3:
			message = "--Usage: /pm <user_name> <message>--"
			private_message(socket, message)
			return

		username = str_arr[1]
		start_index = 4 + len(username) + 1

		head = "*%s says* " % users[socket]
		p_message = command[start_index:-1]
		receiver = find_key(users, username)

		if receiver is None:
			message = "--Unable to message %s--" % username
			private_message(socket, message)
		else:
			print "[%s -> %s] %s" % (users[socket], 
				username, p_message)
			private_message(receiver, head + p_message)
	
	# Creates a user group
	elif command[1:12] == "creategroup":
		group_name = command[13:].strip()
		create_group(socket, group_name)

	# Create a user group macro
	elif command[1:3] == "cg":
		group_name = command[4:].strip()
		create_group(socket, group_name)

	# Adds a user to a group
	elif command[1:5] == "join":
		group_name = ""
		group_name = command[6:].strip()
		join_group(socket, group_name)

	# Leaves group
	elif command[1:6] == "leave":
		if not users[socket].inGroup():
			message = "--You're not in a group--"
			private_message(socket, message)
		else:
			group = users[socket].getGroup()
			group.remove_user(socket)
			users[socket].addGroup(None)
			message = "--You've left %s--" % group.getName()
			private_message(socket, message)

	# Kicks names user from server
	elif command[1:5] == "kick":
		username = command[6:].strip()
		to_kick = find_key(users, username)

		if not users[socket].isOp():
			message = "--You must be an Op to use /kick--"
			private_message(socket, message)
			return

		if to_kick is None:
			message = "--Unable to kick %s--" % username
			private_message(socket, message)
		else:
			kicker = users[socket].getName()
			message = "--%s kicked you from the server--" % kicker
			private_message(to_kick, message)
			logout(to_kick)

	# Makes a user able to perform admin commands
	elif command[1:3] == "op":
		str_arr = command.split()
	
		if users[socket].isOp():
			if len(str_arr) < 2:
				message = "--Usage: /op <user_name>"
				private_message(socket, message)
		else:
			if len(str_arr) < 3:
				message = "--Usage: /op <user_name> <password>--"
				private_message(socket, message)

		username = str_arr[1]
		start_index = 4 + len(username) + 1
		to_op = find_key(users, username)

		attempt = command[start_index:].strip()
		if to_op is None:
			message = "--Unable to op %s--" % username
			private_message(socket, message)
		else:
			if not users[socket].isOp():
				if attempt != op_pass:
					message = "--Password incorrect--"
					private_message(socket, message)
					return
			op_user(to_op, socket)

	# Displays a list of user groups
	elif command[1:7] == "groups":
		num_groups = len(groups)

		if num_groups < 1:
			message = "--There are no groups on the server--"
			private_message(socket, message)
			return

		if num_groups == 1:
			message = "There is 1 group on the server:"
		else:
			message = "There are %d groups on the server:" % num_groups

		for g in groups:
			message += "\n%s:\t" % g.getName()
			message += ", ".join(str(users[u]) for u in g.getUsers())

		private_message(socket, message)

	# Send message to all users
	elif command[1:7] == "global":
		if len(command.strip()) < 9:
			message = "--Usage /global <message>--"
			private_message(socket, message)
			return

		message = "\n[%s] %s\n" % (users[socket], command[8:].strip())
		global_message(message, socket)
		
	else:
		c = command.strip()
		message = "--Command '%s' not recognized--" % c
		message += "\n--Use /help for a list of commands--"
		private_message(socket, message)

# Creates group unless the group already exsists or the user
# is already in a group
def create_group(socket, group_name):
	user_name = users[socket].getName()
	if len(group_name) < 1:
		message = "--Usage: /creategroup <group_name>--"
		private_message(socket, message)
	else:
		if users[socket].inGroup():
			message = "--You're already in group %s!--" % (
				users[socket].getGroup().getName())
			private_message(socket, message)
			return

		# Checks if a groups with that name already exsists
		for g in groups:
			if g.getName() == group_name:
				join_group(socket, group_name)
				return

		new_group = Group(group_name)
		new_group.add_user(socket, users[socket].getName())
		users[socket].addGroup(new_group)
		groups.append(new_group)
		
		msg = "--Group %s created by %s--\n" % (group_name, user_name)
		global_message(msg, socket)
		print msg[:-1]

		msg = "~~Group %s created~~" % group_name
		private_message(socket, msg)

# Joins the named group if it exsists and the user is not already
# in a group.
def join_group(socket, group_name):
	user_name = users[socket].getName()

	if len(group_name) < 1:
		message = "--Usage: /join <group_name>--"
		private_message(socket, message)
	else:
		if users[socket].inGroup():
			message = "--You're already in group %s" % (
				users[socket].getGroup().getName())
			private_message(socket, message)
			return
		to_join = None
		try:
			for g in groups:
				if g.getName() == group_name:
					to_join = g
					break
			if to_join == None:
				message = "--Unable to join group %s--\n" % group_name
				private_message(socket, message)
			else:
				to_join.add_user(socket, users[socket])
				users[socket].addGroup(to_join)
				message = "~~Joined %s~~" % group_name
				private_message(socket, message)
				print "--%s joined %s--" % (user_name, group_name)
		except Exception as e:
			print(e)

# Gives the named user opperator privileges if the person 
# sending the command is an Op, or has the right password
def op_user(to_op, socket):
	username = users[to_op].getName()
	if users[to_op].isOp():
		message = "--User %s is already an Op--" % username
		private_message(socket, message)
	else:
		message = "--User %s is now an Op--" % username
		private_message(socket, message)
		message = "--You are now an Op--"
		private_message(to_op, message)
		users[to_op].setOp(True)

# Searches dictionary by value
def find_key(dictionary, value):
	for key in dictionary:
		if dictionary[key].getName() == value:
			return key

	return None 

# Finds a group by name
def find_group(g_name):
	for g in groups:
		if g.group_name == g_name:
			return g
	return None

# Used to check for logged out users
count_blanks = ()
TOLERANCE = 20

# Main Method
if __name__ == "__main__":

	connected_sockets = []
	BUFFER = 4096
	PORT = 2401

	# Creates IPv4 socket using TCP
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

	server_ip = socket.gethostbyname(socket.gethostname())
	server_socket.bind(("0.0.0.0", PORT))
	server_socket.listen(10)

	# Adds server to list of connected sockets
	connected_sockets.append(server_socket)

	print "Server started on %s:%d" % (server_ip, PORT)

	# Continually looks for messages and new users
	while 1:
		check_users()
		
		read_sockets, write_sockets, err_sockets = select.select(
			connected_sockets, [], [])

		# Loops through all readable sockets
		for sock in read_sockets:
			
			# New Connection
			if sock == server_socket:

				# Connection is added, but user object is not
				# created until a username is received from
				# this socket
				new_socket, addr = server_socket.accept()
				new_socket.setblocking(0)
				connected_sockets.append(new_socket)
					
			# Incoming message
			else:
				try:
					message = sock.recv(BUFFER)

					if message:
						
						# Check for command
						if message[:1] == '/' or message[:4] == '`*`*':
							handle_commands(sock, message)
						else:	
							user = users[sock]

							# Checks if user is in a group
							if user.getGroup() == None:					
								broadcast_message(sock, message)
								print "[%s] %s" % (user, message)
							else:
								group = user.getGroup()
								group.group_broadcast(sock, message)
								print "{%s} %s" % (user, message)

					# Checks for disconnected users
					else:
						
						# When a socket disconects, the server
						# recevies blank messages from that socket
						# until there is a new action on the server.
						# This block check for this case to detect
						# a newly disconnected user.
						peer = sock.getpeername()
						if count_blanks[0] == peer:
							count_blanks[1] += 1
							if count_blanks[1] > TOLERANCE:
								logout(sock)
						else:
							count_blanks[0] = peer
							count_blanks[1] = 1
				except Exception as e:
					print "--Except in recieving: %s" % e

					logout(sock)

	server_socket.close()
