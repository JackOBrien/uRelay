import socket, sys, select

username = ""

def prompt() :
    sys.stdout.write('<%s> ' % username)
    sys.stdout.flush()

if __name__ == "__main__":
	
	if (len(sys.argv) !=3):

		print 'Usage: python %s <hostname> <port>' % sys.argv[0]
		sys.exit(2)

	host = sys.argv[1]
	port = int(sys.argv[2])
	BUFFER = 4096

	# Asks user for their name
	username = raw_input("Username: ")

	# Create IPv4 socket using TCP
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	
	# Attempts to connect
	try:
		sock.connect((host, port))
	except:
		print "Unable to connect to %s on port %d" % (host, port)
		
	sock.send("`*`*name %s" % username);
	
	prompt()
	
	while 1:
		socket_list = [sys.stdin, sock]
         
		# Get the list sockets which are readable
		read_sockets, w, e = select.select(socket_list , [], [])
         
		for socket in read_sockets:
			# Incoming message from server
			if socket == sock:
				message = sock.recv(4096)
				
				if not message :
					print '\nDisconnected from chat server'
					sys.exit()
				else :
					# Prints message from server
					sys.stdout.write(message)
					prompt()
             
			# User entered a message
			else :
				msg = sys.stdin.readline()
				sock.send(msg)
				prompt()
