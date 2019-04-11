# *************************** -*- Serveur.py -*- ******************************
""" Python program to implement server side of multpiple chat rooms. 

Execute using Python2.7

See README.md for futher informations on how to use this code.
"""

# ********************** -*- Libraries importation -*- ************************
import socket 
import select 
import sys
import errno 
from thread import *
from collections import deque


# **************************** -*- main code -*- ******************************

# socket creation
#  -- uses AF_INET domain and TCP protocol
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)


IP_address = str(sys.argv[1]) #sets IP address
 
Port = int(sys.argv[2]) #sets port number

#The client must be aware of the IP address and port number parameters 
server.bind(('', Port)) 

#listens for "100" active connections
server.listen(100) 

# -*- Global variables -*-
""" 
    *********************************************************
 * list_of_clients : map of connections per room. 
       --- key : name of room ; 
       --- value : list of sockets
 * liste_utilisateurs : list of connected user's names. 
 * liste_commandes : list of special commands
 * list_of_conversations : map of messages per room. 
       --- key : name of room
       --- value : deque of a list of messages and size = 20
     We keep at maximum 20 messages 
    *********************************************************
"""

list_of_clients = {'Hub' : [], 'Presentation' : [], 'Blabla' : []}

liste_utilisateurs=[]

liste_commandes = ['changernom', 'changersalon', 'creersalon', 'listeutilisateurs\n', 'help\n', 'exit\n']

list_of_conversations = {'Hub' : deque([], 20), 'Presentation' : deque([], 20), 'Blabla' : deque([], 20)} 

# -*- Functions -*-


def broadcast(message, connection, chan): 
	"""Broadcast the message to all clients except the one who sent the message.

	Parameters
	----------
	message : str
		message to send.
	connection : socket
		socket of user sending message.
	chan : str
		name of room.
	"""
	for clients in list_of_clients[chan]: 
		if clients!=connection: 
			try: 
				clients.send(message) 
			except: # if the link is broken, we remove the client
				clients.close() 
				remove(clients)  


def changerchan(conn, name, ancien, nouveau) :
	"""Removes the old connection in one room and create a new one in the chosen room.
	 
	Parameters
	----------
	conne : socket
		socket of the user who wants to change room.
	name : str
		name of the user that appears on terminal.
	ancien : str
		old room.
	nouveau : str
		new room.
	"""
	remove(conn, ancien)
	list_of_clients[nouveau].append(conn)
	conn.send("Bienvenue dans "+nouveau+'\n')
	for message in list_of_conversations[nouveau]: #displays the last 20 messages
		conn.send(message+"\n")
	broadcast(name+" est entre dans le salon", conn, nouveau)


def connected_users():
	"""Returns a display of users present on server.

	Returns
	-------
	str
		A string listing all connected users.
	"""
	res =""
	for s in liste_utilisateurs:
		res = res +" - " + s + "\n"
	res=res+" sont actuellement connectes\n"
	return res


def remove(connection, chan): 
	"""Removes the user from the list of clients (in a specific room)

	Parameters
	----------
	connection : socket
		socket object of user that needs to be removed
	chan : str
		name of room
	"""  
	if connection in list_of_clients[chan]: 
		list_of_clients[chan].remove(connection) 


def remove_from_server(connection, chan, name): 
	"""Removes the client from the list of clients and the list of users --- To use for users leaving the server

	Parameters
	----------
	connection : socket
		socket object of user that needs to be removed
	chan : str
		name of room
	name : str
		name of user that needs to be removed
	"""  
	if connection in list_of_clients[chan]: 
		list_of_clients[chan].remove(connection) 
	if name in liste_utilisateurs:
		liste_utilisateurs.remove(name)


def clientthread(conn, addr): 
	"""Manages the connection of a specific user
	Parameters
	----------
	conn : socket
		socket object of the new connected user
	addr : str
		IP address of the new connected user
	"""  
	name=addr[0]
	conn.send("Choissisez un nom :\n") # First, a user should choose a name
	name=conn.recv(2048)[:-1]
	while name in liste_utilisateurs : # Cannot choose an already chosen name 
		conn.send("Nom deja utilise\n")
		conn.send("Choissisez un nom :\n")
		name=conn.recv(2048)[:-1]
		
	liste_utilisateurs.append(name) # add the new user to the list of users
	liste_utilisateurs.sort() 


	# Then, informations on the state of the server are sent
	# sends a message to the client whose user object is connected
	# The user must choose a room
	conn.send("Bienvenue dans le Hub !\nIl y a actuellement " + str(len(liste_utilisateurs)) + " utilisateurs connecte(s) : \n"+ connected_users() + "\nChoissisez un salon : \n")
	liste_chan=''
	for s in list_of_clients.keys() :
		liste_chan+=s+';'
	conn.send(liste_chan)

	chan=conn.recv(2048)[:-1]
	while chan not in list_of_clients.keys() : # Only exisiting room can be chosen
		conn.send("Salon inexistant\nChoisissez un salon : \n")
		conn.send(liste_chan)
		chan=conn.recv(2048)[:-1]

	changerchan(conn, name, 'Hub', chan) # See l.278 : a user is first placed automatically in hub

	while True: 
		try: 
			message = conn.recv(2048) # In case a user send a message
			if message: 
			#prints on the terminal :  message and name of the user
				print("<" + name + "> " + message) 
				if message.startswith('/') : # In case the message is a special command
					comm=message.split(' ')
					if comm[0][1:] not in liste_commandes :
						conn.send("Commande inconnue ou incomplete\n")
					else :
						if comm[0][1:]=='changernom' :  #change name command
						# parcoure la liste des utilsateurs
							nv=comm[1].rstrip("\n")
							if nv not in liste_utilisateurs :
								liste_utilisateurs.remove(name) #remove the old name of the list of users
								liste_utilisateurs.append(nv)  #add the new name to the list of users
								broadcast(name+" a change son nom en "+nv, conn, chan)
								name=nv
							else :
								conn.send("Nom deja utilise\n")
						elif comm[0][1:]=='changersalon' : #change room command
							if comm[1].rstrip("\n") in list_of_clients.keys() :
								changerchan(conn, name, chan, comm[1].rstrip("\n"))
								chan=comm[1].rstrip("\n")
						elif comm[0][1:]=='creersalon' : #create room command
							if comm[1][:-1] not in list_of_clients.keys() :
								list_of_clients[comm[1][:-1]]=[]
								list_of_conversations[comm[1][:-1]]=deque([],20)
								changerchan(conn,name,chan,comm[1][:-1])
								chan=comm[1][:-1]
							else:
								conn.send("Ce salon existe deja")
						elif comm[0][1:]=='listeutilisateurs\n' : #list of users command
							conn.send(connected_users())
						elif comm[0][1:]=='help\n' : #help command
							conn.send("Bienvenue dans l'aide du chat. Ici, tu peux naviguer dans plusieurs salons et discuter avec les personnes connectees a ce serveur.\n\nListe des commandes disponibles :\n-/changernom <nom> : permet de changer de nom dans le serveur\n-/changersalon <nom_du_salon> : permet de se deplacer dans le salon choisi\n-/creersalon <name_of_new_room> : cree un nouveau salon dans lequel tu est place directement. Si ce salon existe deja, tu seras place automatiquement dans le salon portant ce nom.\n-listeutilisateurs : permet d'obtenir les noms des utilisateurs connectes\n-help\n\nPour plus de details sur l'utilisation, veuillez vous referer au README.md\n")
						elif comm[0][1:]=='exit\n' : #exit command
						  conn.send("Etes vous surs de vouloir quitter ? [y/n]")
						  resp = conn.recv(2048)
						  while resp!='y\n' and resp!='n\n':
						    conn.send("Etes vous surs de vouloir quitter ? [y/n]")
						    resp = conn.recv(2048)
						  if resp == 'y\n':
						    conn.send("DisconnectNow")
						    #conn.close()
						    remove_from_server(conn, chan, name)
						  else:
						    continue
				else :
				# Calls broadcast function to send message to all and saves the message in the list
					message_to_send = "<" + name + "> " + message 
					broadcast(message_to_send, conn, chan) 
					if(len(list_of_conversations[chan])==20):
						list_of_conversations[chan].popleft()
					msg = "<" + name + "> " + message
					list_of_conversations[chan].append(msg)

			else: 
				#remove connection when it's broken
				remove_from_server(conn, chan, name) 
				broadcast(name+" a quitte le salon", conn, chan)
				break
		except (socket.error, e):
			if isinstance(e.args, tuple):
				print ("errno is %d" %e[0])
				if e[0] == errno.EPIPE:
			  #remote peer disconnected
					print ("Detected connection disconnect")
				else:
					pass
			else:
				print ("socket error", e)
			conn.close()
			break

# ***************************** end functions *********************************

if __name__ == "__main__":
	# checks whether IP address and port number have been provided 
	""" 
	****************************
	sys.argv[0] = file name
	sys.argv[1] = IP address
	sys.argv[2] = port number
	****************************
	"""
	if len(sys.argv) != 3: 
		print("Entrez : script, addresse IP, numero de port")
		exit() 

	#Sends a message when the server is in place
	print("Your server is up.")


	while True:

		"""Accepts a connection request and stores two parameters, 
		socket object for that user, and IP address of the client"""
		conn, addr = server.accept()

		#Maintains a list of clients in the chatroom
		list_of_clients['Hub'].append(conn)

		# prints the address of the user that just connected 
		print(addr[0] + " connected")

		# creates and individual thread for every user that connects 
		start_new_thread(clientthread,(conn,addr))	 

	conn.close() 
	server.close()
