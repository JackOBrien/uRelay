import socket, select

users = {}
opped_users = {}
OP_PASSWORD = "1337hax"

welcome_message = "Welcome!"

# Sends message to all connected users except sender
def broadcast_message(sender, message):
	print "--Broadcasting: %s" % message
	for socket in connected_sockets:
		if socket != server_socket and socket != sender:
			try:
				sender_name = users[sender]
				socket.send("\n<%s> %s" % (sender_name, message))
				print "--Sent message to %s" % users[socket]
			except:
				
				print "--Except in boradcast"

				logout(socket)

	
def private_message (receiver, message):
	try:
		receiver.send("%s\n" % message)
	except:
		logout(receiver)

def login_message(new_guy):
	print "--Login Message--"
	#check_users()

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
	name = users[socket]
	print "-- Loging out <%s>" % name
	del users[socket]
	connected_sockets.remove(socket)
	socket.close()
	print "Client %s disconected" % name

	msg = "\n--%s Disconnected--\n" % name
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
	msg = users.values()[0]
	usr = "User"

	# Handle plurality
	if len(users.values()) > 1:
		usr += 's'
			
		# Assembles list of users
		for i in range(1, len(users.values())):
			u = users.values()[i]

			# Last user in list
			if i == len(users.values()) -1:
				msg += " and " + u
			else:
				msg += ', ' + u
	return "%s: %s Online" % (usr, msg)

def handle_commands(socket, command):
	print "--Handle_Command--"
	if command[:8] == "`*`*name":
		username = command[9:]
		users[sock] = username
		login_message(sock)
	elif command[1:5] == 'list':
		msg = whos_online()							
		private_message(sock, msg)
	elif command[1:7] == "logout":
		logout(socket)
	elif command[1:5] == "kick":
		username = command[6:].strip()
		to_kick = None
		for key in users:
			if users[key].strip() == username.strip():
				to_kick = key
		if to_kick is None:
			message = "--Unable to kick %s--" % username
			private_message(socket, message)
		else:
			logout(to_kick)
	elif command[1:3] == "op":
		username = command [4:].strip()
		to_op = None
		for key in users:
			if users[key].strip() == username.strip():
				to_op = key
		if to_op is None:
			message = "--Unable to op %s--" % username
			private_message(socket, message)
		else:
			opped_users[socket] = username


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
							name = users[sock]
							broadcast_message(sock, message)

							print "[%s] %s" % (name, message)

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
				except:
					print "--Except in recieving"
					print "--Exception from %s" % str(sock.getpeername())	

					logout(sock)

	server_socket.close()
