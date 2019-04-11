# Python program to implement client side of chat room. 
import socket 
import select 
import sys 

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
if len(sys.argv) != 3: 
	print("Entrez : script, addresse IP, numero de port")
	exit() 
IP_address = str(sys.argv[1]) 
Port = int(sys.argv[2]) 
server.connect((IP_address, Port)) 

message=''
while message!="DisconnectNow": 

	# maintains a list of possible input streams 
	sockets_list = [sys.stdin, server] 

	""" two possible input situations : 
	user wants to give manual input to send to other people (else condition), 
	or server is sending a message to be printed on the 
	screen (if condition). Select returns from sockets_list, the stream that is reader for input."""
	read_sockets,write_socket, error_socket = select.select(sockets_list,[],[]) 

	for socks in read_sockets: 
		if socks == server: 
			message = socks.recv(2048) 
			print(message) 
		else: 
			message = sys.stdin.readline() 
			server.send(message) 
			sys.stdout.write("<You>") 
			sys.stdout.write(message) 
			sys.stdout.flush()
			
server.close() 

