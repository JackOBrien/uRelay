import socket, select

users = {}

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
		receiver.close()
		connected_sockets.remove(receiver)
		
def login_message(new_guy):
	name = users[new_guy]
	print "[%s] Connected to Server" % name
	for socket in connected_sockets:
		if socket == server_socket: continue
		if socket == new_guy:
			msg = "%s\n\t%d %s\n" % (welcome_message, len(users),'Online')
			private_message(socket, msg)
		else:
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
	for socket in connected_sockets:
		try:
			if socket == server_socket: continue
			socket.send(msg)
		except:
			print "--Except in logout--"

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
		read_sockets, write_sockets, err_sockets = select.select(
			connected_sockets, [], [])

		for sock in read_sockets:
			
			# New Connection
			if sock == server_socket:
				print "--New Connection"

				new_socket, addr = server_socket.accept()
				
				connected_sockets.append(new_socket)
				
				#result = login (new_socket)
					
				
				
			# Incoming message
			else:
				try: sock.getpeername()
				except:
					continue

				try:
					print "--Recieving message from: %s" % str(sock.getpeername())
					message = sock.recv(BUFFER)
					print "--Message says: %s" % message
					if message:
						
						# Check for command
						if message[:1] == '/' or message[:4] == '`*`*':
							if message[:8] == "`*`*name":
								username = message[9:]
								users[sock] = username
								login_message(sock)
						else:	
							name = users[sock]
							broadcast_message(sock, message)

							print "[%s] %s" % (name, message)
				except:
					print "--Except in recieving"
					print "--Exception from %s" % str(sock.getpeername())				
					logout(sock)

	server_socket.close()
