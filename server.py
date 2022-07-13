# import libraries
import socket
import threading
import os

class Server():
    def __init__(self, port:int):

        abspath = os.path.abspath(__file__)
        dname = os.path.dirname(abspath)
        os.chdir(dname)
 
        # Choose a port that is free
        self.folder_location = os.environ['APPDATA'] + "/ChatApp/"

        self.PORT = port

        # An IPv4 address is obtained
        # for the server.  
        self.SERVER = socket.gethostbyname(socket.gethostname())

        # Address is stored as a tuple
        self.ADDRESS = (self.SERVER, self.PORT)

        # the format in which encoding
        # and decoding will occur
        self.FORMAT = "utf-8"

        # Lists that will contains
        # all the clients connected to
        # the server and their names.
        self.clients, self.nicknames = [], []

        # Create a new socket for
        # the server
        self.server = socket.socket(socket.AF_INET,
                            socket.SOCK_STREAM)

        # bind the address of the
        # server to the socket
        self.server.bind(self.ADDRESS)

        #create chat log
        self.chat_log = []
    
    # function to start the connection
    def startChat(self):
    
        print("server is working on " + self.SERVER)
        
        # listening for connections
        self.server.listen()
        
        while True:
        
            # accept connections and returns
            # a new connection to the client
            #  and  the address bound to it
            conn, addr = self.server.accept()
            conn.send("NICK".encode(self.FORMAT))
            
            # 1024 represents the max amount
            # of data that can be received (bytes)
            name = conn.recv(1024).decode(self.FORMAT)
            
            # append the name and client
            # to the respective list
            self.nicknames.append(name)
            self.clients.append(conn)
              
            print(f"{name} joined")

            for i in self.chat_log:
                conn.send((i).encode(self.FORMAT))
            
            # broadcast message
            self.broadcastMessage(f"{name} has joined the chat!".encode(self.FORMAT))
            
            conn.send('\nConnection successful!'.encode(self.FORMAT))
             
            # Start the handling thread
            self.handle_thread = threading.Thread(target = self.handle,
                                    args = (conn,))
            self.handle_thread.start()

    
    # method to handle the
    # incoming messages
    def handle(self, client):
    
        while True:
            try:
                message = client.recv(1024)
                self.broadcastMessage(message)
            except:
                index = self.clients.index(client)
                self.clients.remove(client)
                client.close()
                nickname = self.nicknames[index]
                self.broadcastMessage(f'{nickname} left the chat!'.encode(self.FORMAT))
                self.nicknames.remove(nickname)
                break
                    
    # method for broadcasting
    # messages to the each clients
    def broadcastMessage(self, message):
        self.chat_log.append((message).decode(self.FORMAT) + "\n")
        for client in self.clients:
            client.send(message)


    def kill(self):
        #make it disconnect them properly
        self.broadcastMessage("Server owner closed server!".encode(self.FORMAT))
        for client in self.clients:
            client.close()

        self.server.close()
        self.nicknames = []