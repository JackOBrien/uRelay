import socket, sys, select

username = ""

def prompt() :
    sys.stdout.write('<You> ')
    sys.stdout.flush()

if __name__ == "__main__":
	
	if (len(sys.argv) !=3):
		print 'Usage: python %s <hostname> <port>" % argv[0]
	
	username = input("Username: ")
	
	# Create IPv4 socket using TCP
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
