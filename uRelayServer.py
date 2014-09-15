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

if __name__ == "__main__":

	connected_sockets = []
	BUFFER = 4096
	PORT = 2401

	# Creates IPv4 socket using TCP
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	server_ip = socket.gethostbyname(socket.gethostname())
	server_socket.bind((server_ip, PORT))
	server_socket.listen(10)

	while 1:
		read_sockets, write_sockets, err_sockets = select.select(
			conneded_sockets, [], [])

		for sock in read_socks:
			
			# New Connection
			if sock == server_socket:
				new_socket, addr = server_socket.accept()
				connected_sockets.append(sockfd)
				
				# Why are there two %s
				print "Client (%s, %s) connected" % addr

				broadcast_message(sockfd, "[%s:%s] connected\n" % addr)

			# Incoming message
			else:
				try:
					message = sock.recv(BUFFER)

					if data:
						name = "\n<" + str(sock.getpeername()) + '> '
						broadcast_message(sock, name + message)
				except:
					broadcast_message(sock, "[%s:%s] disconected" % addr)
					print "Client (%s, %s) disconected" % addr
					
					sock.close()
					connected_sockets.remove(sock)
	server_socket.close()
