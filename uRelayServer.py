import socket, select

Users = []

# Sends message to all connected users except sender
def broadcast_message(sender, message):
	for socket in connected_sockets:
		if socket != server_socket and socket != sender:
			try:
				socket.send(message)
			except:
				
				# Removes sockets which cannot recieve a message
				if socket in connected_sockets:
					socket.close()
					connected_sockets.remove(socket)

					print "Client (%s:%s) disconected" % addr
	
def private_message (reciever, message):
	try:
		reciever.send(message)
	except:
		reciever.close()
		connected_sockets.remove(reciever)
		
#def login(socket):
	#message = "Username: "
	#private_message(socket, message)

# Main Method
if __name__ == "__main__":

	connected_sockets = []
	BUFFER = 4096
	PORT = 2401

	# Creates IPv4 socket using TCP
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

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
				new_socket, addr = server_socket.accept()
				
				connected_sockets.append(new_socket)
				
				#result = login (new_socket)
					
				print "Client (%s, %s) connected" % addr
				broadcast_message(new_socket, "[%s:%s] connected" % addr)
				
				
			# Incoming message
			else:
				try:
					message = sock.recv(BUFFER)

					if message:
					
						# Check for command
						if message[:1] == '/':
							if message[:5] == "/name":
								continue
							continue
					
						name = "\n<" + str(sock.getpeername()) + '> '
						broadcast_message(sock, name + message)
						
						print "%s %s" % (str(sock.getpeername()), message)
				except:
					broadcast_message(sock, "[%s:%s] disconected" % addr)
					print "Client (%s, %s) disconected" % addr
					
					# Removes socket attempting to send a message
					sock.close()
					connected_sockets.remove(sock)

	server_socket.close()
