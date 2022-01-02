import socket
import threading
import random
import time
import sys
import uuid
from configparser import ConfigParser
from hash_table import Hashtable

LOCALHOST = '127.0.0.1'
BUFFER_SIZE = 2048
MAX_PEERS = 5
BROADCAST_PORT = 54600

def main():
    running = 0
    global unique_id
    unique_id = None
    global peer_table
    peer_table = Hashtable(MAX_PEERS)
    global files
    files = Hashtable(10)
    global IPAddr
    IPAddr = None
    global MYPORT

    class BroadcastSender(threading.Thread):

        def __init__(self, message):
            threading.Thread.__init__(self)
            self.message = bytes(message, 'utf-8')

        def run(self):
            sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            sender.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sender.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            
            sender.sendto(self.message, ('<broadcast>', BROADCAST_PORT))

    class BroadcastListener(threading.Thread):

        def __init__(self):
            threading.Thread.__init__(self)

        def run(self):
            global IPAddr
            global files   
            listener = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            listener.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            listener.bind(('', BROADCAST_PORT))
            global unique_id

            while True:
                data = ''

                try:
                    buffer, addr = listener.recvfrom(2048)
                    data += str(buffer, "utf-8")
                except:
                    pass

                if data:
                    print("BROADCAST::: %s" % data)
                    response = data.split()
                    
                    if len(response) > 1:
                        if response[0].lower() == "check":
                            resp, index = peer_table._search(response[1])
                            print(resp, index)
                            if resp:
                                
                                print("✔️ MATCH FOUND ✔️")

                                send_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                send_socket.connect((response[2], int(response[3])))
                                message = "❕ Sending files ❕"
                                try:
                                    send_socket.sendall(bytes(message, 'utf-8'))
                                    print("🚀🔥Fire Away🔥🚀")
                                    data = ''
                                except:
                                    Exception
                        elif response[0].lower() == "search":
                            resp, index = files._search(response[1])
                            print(resp, index)
                            if resp:
                                
                                print("✔️ FILE RECORD FOUND ✔️")

                                send_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                send_socket.connect((response[2], int(response[3])))
                                message = "❕ Sending files ❕"
                                try:
                                    send_socket.sendall(bytes(message, 'utf-8'))
                                    print("🚀🔥Fire Away🔥🚀")
                                    data = ''
                                except:
                                    Exception
            listener.close()
                                

    class ChatListener(threading.Thread):

        def __init__(self):
            threading.Thread.__init__(self)
            self.port = None

            # The Hashtable that will store the keys and values, it has a maximum of 10 
            # buckets where it can store data
            global unique_id

            print("❕ Initialising ❕")
            try:
                # Read config.ini file
                config_object = ConfigParser()
                config_object.read("config.ini")

                # Get the uuid
                userinfo = config_object["USERDATA"]
                print("🔑 UUID is {} 🔑".format(userinfo["uuid"]))
                unique_id = userinfo["uuid"]
                print("❕ Maximum peers: {} ❕".format(MAX_PEERS))

            except:
                print("🆕 Config file doesn't exist. Creating unique user ID... 🆕")
                
                # Generate a random uuid string
                config_object["USERDATA"] = {
                    "uuid": uuid.uuid4(),
                }

                # Assign UUID to self
                unique_id = config_object["USERDATA"]["uuid"]

                #Write the above sections to config.ini file
                with open('config.ini', 'w') as conf:
                    config_object.write(conf)
                    print("⚙️ Config Created ⚙️")
                    print("🔑 UUID is {} 🔑".format(config_object["USERDATA"]["uuid"]))
                    print("❕ Maximum peers: {} ❕".format(MAX_PEERS))
                    

        def run(self):
            global IPAddr
            listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # Set the ip and port
            listen_socket.bind(('', self.port))
            hostname = socket.gethostname()   
            IPAddr = socket.gethostbyname(hostname) 
            listen_socket.listen(5)

            welcome_note = BroadcastSender("CHECK {} {} {}".format(unique_id, IPAddr ,self.port))
            welcome_note.start()
            
            while True:

                clientsock, address = listen_socket.accept()
                print("\n❕ Established connection with: {} ❕".format(clientsock.getpeername()))
                
                getMessages = threading.Thread(target = self.handleConnection, args=[clientsock])
                getMessages.start()

            listen_socket.close()

        def handleConnection(self, clientsock):
            global IPAddr
            
            while True:
                buffer = ''
                try:
                    message = clientsock.recv(BUFFER_SIZE).decode()
                except:
                    print("❕ Connection closed by peer ❕")
                    break
                
                if message:

                    buffer += message
                    tokens = buffer.lower().split()
                
                    if tokens[0] == "uuid":
                        if len(tokens) == 4:
                            print("❕ Adding to peer table ❕")
                            # Add client to peer table
                            self.addpeer(tokens[1])
                    else:
                        print(clientsock.getpeername(), "::: ", buffer)
                else:
                    break

            clientsock.close()

        def addpeer(self, uuid):
            resp, index = peer_table._search(uuid)
            if index == -1:
                print("❕ Peer Table Full ❕")
            else:
                if resp:
                    # print("❕ Peer Already Exists ❕")
                    # Send files back
                    pass
                else:
                    peer_table.insert(uuid, "No files")
                    print("✔️ Peer added ✔️")
                

    class ChatSender(threading.Thread):

        def __init__(self):
            threading.Thread.__init__(self)
            self.address = None
            self.port = None
            running = 1

        def run(self):
            send_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            send_socket.connect((self.address, self.port))

            print("✔️ Connected. Enter Command Below or Enter quit to exit and connect to another node ✔️")
            message = "UUID {} {} {}".format(unique_id, IPAddr , MYPORT)
            send_socket.sendall(bytes(message, 'utf-8'))
            while True:

                message = input()
                if message != "":
                    tokens = message.lower().split()
                    if message.lower() == "quit":
                        
                        break
                    elif tokens[0] == "search":
                        if len(tokens) == 2:
                            welcome_note = BroadcastSender("SEARCH {} {} {}".format(tokens[1], IPAddr , MYPORT))
                            welcome_note.start()
                    elif tokens[0] == "add":
                        if len(tokens) == 3:
                            self.addfile(tokens[1], tokens[2])
                    else:
                        try:
                            send_socket.sendall(bytes(message, 'utf-8'))
                            print("🚀🔥Fire Away🔥🚀")
                        except:
                            Exception
            
            send_socket.close()
            running = 0
            return

        def addfile(self, filename, filepath):
            resp, index = files._search(filename)
            if index == -1:
                print("❕ Table Full ❕")
            else:
                if resp:
                    print("❕ File Already Exists ❕")
                else:
                    files.insert(filename, filepath)
                    print("✔️ File added ✔️")
    

    chat_listener = ChatListener()
    chat_listener.port = random.randint(3000, 5000)
    MYPORT = chat_listener.port
    chat_listener.start()

    udp_broadcast = BroadcastListener()
    udp_broadcast.start()

    print("Started listening on port: ", chat_listener.port)

    while True:
        if running == 0:
            try:
                ip = input("\nPlease enter the address you would like to connect on: ")
                port = int(input("\nPlease enter the port you would like to connect on: "))

                chat_sender = ChatSender()
                chat_sender.address = ip
                chat_sender.port = port
                chat_sender.start()
                chat_sender.join()
            except KeyboardInterrupt:
                print("❕ Keyboard Interrupt: Exiting ❕")
                sys.exit()

if __name__ == "__main__":
    main()