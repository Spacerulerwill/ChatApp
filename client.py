# import all the required  modules
from concurrent.futures import thread
import socket
import sys
import threading
from tkinter import *
from tkinter import font
from tkinter import ttk
from tkinter.messagebox import askokcancel, showwarning
from tkinter.simpledialog import askstring
import os
import pickle

import server
 
# import all functions /
#  everything from chat.py file
 
PORT = 50000

FORMAT = "utf-8"
 
# Create a new client socket
# and connect to the server
client = None

 
# GUI class for the chat
class GUI:
    # constructor method
    def __init__(self):

        abspath = os.path.abspath(__file__)
        dname = os.path.dirname(abspath)
        os.chdir(dname)
        #create folder in appdata
        if not os.path.exists(os.environ['APPDATA'] + "/ChatApp"):
            os.makedirs(os.environ['APPDATA'] + "/ChatApp")

        # chat window which is currently hidden
        self.Window = Tk()
        self.Window.withdraw()
    
        name = askstring("Enter name", "Please enter your name:")
        while name == "":
            name = askstring("Enter name", "Please enter your name:")
        
        if name == None:
            os._exit(0)
        
        self.name = name
        
        self.is_joined = False
        self.is_hosting = False

        self.SERVER = ""
        self.PORT = 50000

        self.layout()
        
        self.Window.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.Window.mainloop()  

    # The main layout of the chat
    def layout(self):
              
        self.Window.deiconify()
        self.update_title()
        self.Window.resizable(width = False,
                              height = False)
        self.Window.configure(width = 470,
                              height = 550,
                              )

        self.Window.grid_columnconfigure(0, weight=1)
        self.Window.grid_rowconfigure(0, weight=1)

        self.master_frame = ttk.Frame(self.Window, relief=SUNKEN)
        self.master_frame.grid(row=0, column=0, sticky="NSEW")
        
        self.master_frame.grid_columnconfigure(0, weight=1)
        self.master_frame.grid_rowconfigure(0, weight=6)
        self.master_frame.grid_rowconfigure(1, weight=1)

        self.top_frame = ttk.Frame(self.master_frame, relief=SUNKEN)
        self.top_frame.grid(row=0, column=0, sticky="NSEW")

        self.top_frame.grid_rowconfigure(0, weight=1)
        self.top_frame.grid_columnconfigure(0, weight=1)

        self.bottom_frame = ttk.Frame(self.master_frame, relief=SUNKEN)
        self.bottom_frame.grid(row=1, column=0, sticky="NSEW")

        self.bottom_frame.grid_columnconfigure(0, weight=1)
        self.bottom_frame.grid_columnconfigure(1, weight=6)
        self.bottom_frame.grid_columnconfigure(2, weight=1)
        self.bottom_frame.grid_rowconfigure(0, weight=1)
        self.bottom_frame.grid_rowconfigure(1, weight=1)
        
        self.textCons = Text(self.top_frame)
        self.textCons.grid(row=0, column=0, sticky="NSEW")
        self.textCons.config(state=DISABLED)

        self.entryMsg = ttk.Entry(self.bottom_frame)
        self.entryMsg.grid(row=0, column=1, rowspan=2, sticky="NSEW")
        self.entryMsg.focus()

        self.join_disconnect_button = ttk.Button(self.bottom_frame, text="Join", command=lambda:self.join_disconnect())
        self.join_disconnect_button.grid(row=0, column=0, sticky="NSEW")

        self.host_button = ttk.Button(self.bottom_frame, text="Host", command=lambda:self.host())
        self.host_button.grid(row=1, column=0, sticky="NSEW")

        self.buttonMsg = ttk.Button(self.bottom_frame,
                                text = "Send",
                               
                                command = lambda : self.sendButton(self.entryMsg.get()))
        self.buttonMsg.grid(row=0, column=2, rowspan=2, sticky="NSEW")

        #bind enter to send message
        self.Window.bind("<Return>", lambda event: self.sendButton(self.entryMsg.get()))

    

    def sendButton(self, msg):
        self.textCons.config(state = DISABLED)
        self.msg=msg
        self.entryMsg.delete(0, END)
        snd= threading.Thread(target = self.sendMessage)
        snd.start()

    def join_disconnect(self):
        global client
        self.is_joined = not self.is_joined
        if self.is_joined:

            if self.is_hosting:
                showwarning("Warning!", "You must close your current hosted server before joining another")
            else:

                client = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
                adr = askstring("IP ADDRESS", "Enter IP: ")

                try:
                    client.connect((adr, PORT))
                    self.SERVER = adr
                except:
                    showwarning("Couldn't connect", "Couldn't connect to IP specified!")
                    self.is_joined = False
                    return False


                receive_thread = threading.Thread(target=self.receive)
                receive_thread.start()
                self.join_disconnect_button.configure(text="Leave")
                self.update_title()

        else:
            #leave
            if self.is_hosting:
                leave = askokcancel("Warning!", "You are the host, leaving the chat will close it. Continue?")
                if leave:
                    self.is_hosting = False
                    kill_thread = threading.Thread(target=self.server.kill)
                    kill_thread.run()
                    self.join_disconnect_button.configure(text="Join")
                    self.host_button.configure(text="Host")

                else:
                    self.is_joined = True
                    self.join_disconnect_button.configure(text="Leave")

            else:
                self.join_disconnect_button.configure(text="Join")
                #close socket
                client.close()
                self.textCons.configure(state='normal')
                self.textCons.delete('0.0', END)
                self.textCons.configure(state='disabled')
                self.SERVER = ""
            self.update_title()

    def host(self):
        global client
        self.is_hosting = not self.is_hosting

        if self.is_hosting:
            if self.is_joined:
                self.write_to_box("Leave current server before starting a new server")
                self.is_hosting = False
            else:
                try:
                    #create server
                    self.server = server.Server()
                    server_thread = threading.Thread(target=self.server.startChat)
                    server_thread.start()
                    self.textCons.configure(state='normal')
                    self.textCons.delete('0.0', END)
                    self.textCons.configure(state='disabled')
                    self.write_to_box("Started hosting server...")
                    self.host_button.configure(text="Close")

                    #join server you just hosted
                    client = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
                    client.connect((socket.gethostbyname(socket.gethostname()), PORT))
                    self.SERVER = socket.gethostbyname(socket.gethostname())
                    receive_thread = threading.Thread(target=self.receive)
                    receive_thread.start()
                    self.is_joined = True
                    self.join_disconnect_button.configure(text="Leave") 
                                      
                except:

                    self.write_to_box(f"Server already hosted on this port ({self.PORT})")
                    self.is_hosting = False    
        else:
            
            self.is_hosting = False
            self.is_joined = False
            kill_thread = threading.Thread(target=self.server.kill)
            kill_thread.run()
            self.join_disconnect_button.configure(text="Join")
            self.host_button.configure(text="Host")
            

        self.update_title()

    def write_to_box(self, message):
        # insert messages to text box
        self.textCons.config(state = NORMAL)
        self.textCons.insert(END,
                                 message+"\n")
            
        self.textCons.config(state = DISABLED)
        self.textCons.see(END)

    # function to receive messages
    def receive(self):
        while True:
            try:
                message = client.recv(1024).decode(FORMAT)
                 
                # if the messages from the server is NAME send the client's name
                if message == 'NICK':
                    client.send(self.name.encode(FORMAT))
                elif message == "PICKLERECV":
                    self.write_to_box("PICKLE RECIEVED")     
                else:
                    # insert messages to text box
                    self.write_to_box(message)
            except:
                # an error will be printed on the command line or console if there's an error
                print("An error occured!")
                self.is_joined= False
                self.join_disconnect_button.configure(text="Join")
                client.close()
                self.update_title()
                break
         
    # function to send messages
    def sendMessage(self):
        self.textCons.config(state=DISABLED)
        while True:
            message = (f"{self.name}: {self.msg}")
            client.send(message.encode(FORMAT))   
            break 

    def on_closing(self):
        if self.is_joined:
            client.close()
        try:
            self.server.kill()
        except:
            pass
        os._exit(0)

    def update_title(self):
        title = self.name
        if self.is_hosting:
            title += " - hosting on " + self.server.SERVER
        else:
            title += " - not hosting"
        if self.is_joined:
            title += " - connected to " + self.SERVER
        else:
            title += " - not connected"

        self.Window.title(title + f" - PORT {self.PORT}")
            
# create a GUI class object
g = GUI()