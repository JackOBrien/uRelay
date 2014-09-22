import socket, select
from uRelayGroup import Group
from uRelayUser import User

users = {}
groups = []

welcome_message = "Welcome!"

# Sends message to all connected users except sender and users
# in seperate chat rooms
def broadcast_message(sender, message):
	print "--Broadcasting: %s" % message
	for socket in connected_sockets:
		if socket != server_socket and socket != sender:
			if users[socket].inGroup(): continue
			try:
				sender_name = users[sender].getName()
				socket.send("\n<%s> %s" % (sender_name, message))
				print "--Sent message to %s" % users[socket].getName()
			except:
				
				print "--Except in boradcast"

				logout(socket)
	
# Sends message to every user except sender if true
def global_message(message, sender):
	for socket in connected_sockets:
		if socket != server_socket:
			if not sender or socket != sender:
				try:
					socket.send(message)
				except:
					logout(socket)

def private_message (receiver, message):
	try:
		receiver.send("%s\n" % message)
	except:
		logout(receiver)

def login_message(new_guy):
	print "--Login Message--"

	name = users[new_guy]
	print "[%s] Connected to Server" % name

	
	msg = "%s\n\t%s\n------------------" % (welcome_message, whos_online())
	private_message(new_guy, msg)

	for socket in connected_sockets:
		if socket != server_socket and socket != new_guy:
			msg = "\n--%s Connected--" % name
			private_message(socket, msg)

# Removes socket 
def logout(socket):
	print "-- Attempting to logout"
	usr = users[socket]
	print "-- Loging out <%s>" %usr 
	if usr.inGroup():
		group = usr.getGroup()
		group.remove_user(usr)
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

def check_users():
	r, w, err_sockets = select.select(
		connected_sockets, [], [])

	for socket in err_sockets:
		logout(socket)

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

def handle_commands(socket, command):
	print "--Handle_Command--"
	
	# Sets the username
	if command[:8] == "`*`*name":
		print "--Attempting to create new user--"
		username = command[9:]
		print "--Making User for %s--" % username
		x = User(socket, username)
		print "--Make it this far--"
		users[socket] = x
		print "--Created User: %s" % users[socket].getName()
		login_message(socket)
	
	# Displays a list of connected users
	elif command[1:5] == 'list':
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
		msg += "\n/kick  \t\tKicks the specified user from the server"
		msg += "\n/help  \t\tDisplays this message"

		private_message(socket, msg)

	# Logs out user
	elif command[1:7] == "logout":
		logout(socket)
	
	# Private messages names user
	elif command[1:3] == "pm":
		str_arr = command.split()
		
		if len(str_arr) < 3:
			message = "--Usage: /pm <user_name> <message>--"
			private_message(socket, message)

		username = str_arr[1]
		start_index = 4 + len(username) + 1

		p_message = "*%s says* " % users[socket]

		p_message += command[start_index:]
		
		receiver = find_key(users, username)

		if receiver is None:
			message = "--Unable to message %s--" % username
			private_message(socket, message)
		else:
			private_message(receiver, p_message)
	
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

		if to_kick is None:
			message = "--Unable to kick %s--" % username
			private_message(socket, message)
		else:
			kicker = users[socket].getName()
			message = "--%s kicked you from the server--" % kicker
			private_message(to_kick, message)
			logout(to_kick)

	# Makes a user able to perform admin commands <not implimented>
	elif command[1:3] == "op":
		username = command [4:].strip()
		to_op = find_key(users, username)

		if to_op is None:
			message = "--Unable to op %s--" % username
			private_message(socket, message)
		else:
			opped_users[socket] = username
			message = "--Opping users not yet implemented--"
			private_message(socket, message)

	else:
		c = command.strip()
		message = "--Command '%s' not recognized--" % c
		message += "\n--Use /help for a list of commands--"
		private_message(socket, message)

def create_group(socket, group_name):
	user_name = users[socket].getName()
	if len(group_name) < 1:
		message = "--Usage: /creategroup <group_name>--"
		private_message(socket, message)
	else:
		for g in groups:
			if g.getName() == group_name:
				join_group(socket, group_name)
				return
		new_group = Group(group_name)
		new_group.add_user(socket, users[socket].getName())
		users[socket].addGroup(new_group)
		groups.append(new_group)
		print "--Added user to group--"
		msg = "--Group %s created by %s--\n" % (group_name, user_name)
		global_message(msg, socket)
		msg = "~~Group %s created~~" % group_name
		private_message(socket, msg)

def join_group(socket, group_name):
	print "--Join group--"
	user_name = users[socket].getName()
	print "--%s attempting to join %s--" % (user_name, group_name)
	if len(group_name) < 1:
		message = "--Usage: /join <group_name>--"
		private_message(socket, message)
	else:
		to_join = None
		try:
			for g in groups:
				print "-- For --"
				if g.getName() == group_name:
					to_join = g
			if to_join == None:
				print "--Unable--"
				message = "--Unable to join group %s--\n" % group_name
				private_message(socket, message)
			else:
				print "-- Attempting to add user to group--"
				to_join.add_user(socket, users[socket])
				users[socket].addGroup(to_join)
				message = "~~Joined %s~~" % group_name
				private_message(socket, message)
		except Exception as e:
			print(e)

def find_key(dictionary, value):
	for key in dictionary:
		if dictionary[key].getName() == value:
			return key

	return None 

def find_group(g_name):
	for g in groups:
		if g.group_name == g_name:
			return g
	return None

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

	connected_sockets.append(server_socket)

	print "Server started on %s:%d" % (server_ip, PORT)

	while 1:
		check_users()
		read_sockets, write_sockets, err_sockets = select.select(
			connected_sockets, [], [])

		for sock in read_sockets:
			
			# New Connection
			if sock == server_socket:
				print "--New Connection"

				new_socket, addr = server_socket.accept()
			
				new_socket.setblocking(0)

				connected_sockets.append(new_socket)
					
			# Incoming message
			else:
				try: sock.getpeername()
				except:
					continue

				try:
					print "--Recieving message from: %s" % str(
						sock.getpeername())
					message = sock.recv(BUFFER)
					print "--Message says: %s" % message
					if message:
						
						# Check for command
						if message[:1] == '/' or message[:4] == '`*`*':
							handle_commands(sock, message)
						else:	
							user = users[sock]

							if user.getGroup() == None:					
								broadcast_message(sock, message)
								print "[%s] %s" % (user, message)
							else:
								print "--Tring to send a group message--"
								group = user.getGroup()
								group.group_broadcast(sock, message)
								print "{%s} %s" % (user, message)

					# Checks for disconnected users
					else:
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
					print "--Exception from %s" % str(sock.getpeername())	

					logout(sock)

	server_socket.close()
