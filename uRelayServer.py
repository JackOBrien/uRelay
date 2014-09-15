import socket, select

# Sends message to all connected users except sender
def broadcast_message(sock, message):
	for socket in connected_sockets:
		if socket != server_socket and socket != sock:
			try:
				socket.send(message)
			except:
				socket.close()
				connected_sockets.remove(socket)

				print "[%s:%s] disconected\n" % addr

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
				new_socket, addr = server_socket.accept()
				connected_sockets.append(new_socket)
				
				# Why are there two %s
				print "Client (%s, %s) connected\n" % addr

				broadcast_message(new_socket, "[%s:%s] connected\n" % addr)

			# Incoming message
			else:
				try:
					message = sock.recv(BUFFER)

					if message:
						name = "\n<" + str(sock.getpeername()) + '> '
						broadcast_message(sock, name + message)
				except:
					broadcast_message(sock, "[%s:%s] disconected" % addr)
					print "Client (%s, %s) disconected\n" % addr
					
					if sock in connected_sockets:
						sock.close()
						connected_sockets.remove(sock)

	server_socket.close()
