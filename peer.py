import socket
import threading
import random
import time
import sys
import os
import json
import tqdm
import uuid
from configparser import ConfigParser

LOCALHOST = '127.0.0.1'
BUFFER_SIZE = 2048
MAX_PEERS = 5
BROADCAST_PORT = 64700

def main():
    running = 0
    global unique_id
    unique_id = None
    global peer_table
    peer_table = []
    global files
    files = {}
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
                    buffer, addr = listener.recvfrom(BUFFER_SIZE)
                    data += str(buffer, "utf-8")
                except:
                    pass

                if data:

                    response = data.split()
                    if response[0].lower() == "check" or response[0].lower() == "search":
                        pass
                    else:
                        print("BROADCAST::: %s" % data)
                    
                    if len(response) > 1:
                        if response[0].lower() == "check":
                            if response[1] in peer_table:
                                resp = True
                            else:
                                resp = False

                            if resp:
                                
                                print("✔️ MATCH FOUND ✔️")

                                if response[1] in files.keys():
                                    for piece in files[response[1]]:
                                        # Create socket to send the files
                                        send_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                        send_socket.connect((response[2], int(response[3])))                              
                                        # Send file details
                                        filesize = os.path.getsize(piece)
                                        message = "FILE {} {} {}".format(piece, filesize, response[1])
                                        try:
                                            send_socket.sendall(bytes(message, 'utf-8'))
                                            print("🚀🔥Fire Away🔥🚀")

                                            # Send file data
                                            # sendfile(filesize, piece, send_socket)
                                            progress = tqdm.tqdm(range(filesize), f"Sending {piece}", unit="B", unit_scale=True, unit_divisor=1024)
                                            with open (piece, 'rb') as source:
                                                while(True):
                                                    # read the bytes from the file
                                                    bytes_read = source.read(BUFFER_SIZE)
                                                    if not bytes_read:
                                                        # file transmitting is done
                                                        break
                                                    # we use sendall to assure transimission in 
                                                    # busy networks
                                                    send_socket.sendall(bytes_read)
                                                    # update the progress bar
                                                    progress.update(len(bytes_read))
                                            send_socket.close()

                                            data = ''
                                        except:
                                            Exception
                                else:
                                    print("❕ Peer Has No Files Stored ❕")

                        elif response[0].lower() == "appear":
                            if response[1] == unique_id:
                                send_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                send_socket.connect((response[2], int(response[3]))) 
                                message = "HERE {} {} {}".format(unique_id, IPAddr, MYPORT)
                                try:
                                    send_socket.sendall(bytes(message, 'utf-8'))
                                    print("🚀🔥Fire Away🔥🚀")
                                    
                                    send_socket.close()
                                    data = ''
                                except:
                                    Exception

                        elif response[0].lower() == "search":
                            for folder in files.values():
                                if response[1] in folder:
                                    resp = True
                                    break
                                else:
                                    resp = False

                            if resp:
                                
                                print("✔️ FILE RECORD FOUND ✔️")
                                # Create socket to send the files
                                send_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                send_socket.connect((response[2], int(response[3])))

                                # Send file details
                                filesize = os.path.getsize(response[1])
                                message = "FILE {} {} {}".format(response[1], filesize, unique_id)

                                try:
                                    send_socket.sendall(bytes(message, 'utf-8'))
                                    print("🚀🔥Fire Away🔥🚀")
                                    
                                    # Send file data
                                    # sendfile(filesize, response[1], send_socket)

                                    progress = tqdm.tqdm(range(filesize), f"Sending {response[1]}", unit="B", unit_scale=True, unit_divisor=1024)
                                    with open (response[1], 'rb') as source:
                                        while(True):
                                            # read the bytes from the file
                                            bytes_read = source.read(BUFFER_SIZE)
                                            if not bytes_read:
                                                # file transmitting is done
                                                break
                                            # we use sendall to assure transimission in 
                                            # busy networks
                                            send_socket.sendall(bytes_read)
                                            # update the progress bar
                                            progress.update(len(bytes_read))
                                    send_socket.close()


                                    data = ''
                                except:
                                    Exception
                        else:
                            pass
            listener.close()

        def sendfile(self, filesize, filename, sending_socket):
            progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
            with open (filename, 'rb') as source:
                while(True):
                    # read the bytes from the file
                    bytes_read = source.read(BUFFER_SIZE)
                    if not bytes_read:
                        # file transmitting is done
                        break
                    # we use sendall to assure transimission in 
                    # busy networks
                    sending_socket.sendall(bytes_read)
                    # update the progress bar
                    progress.update(len(bytes_read))
            sending_socket.close()

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
            welcome_note = BroadcastSender("CHECK {} {} {}".format(unique_id, IPAddr ,self.port))
            welcome_note.start() 
            listen_socket.listen(5)
            
            
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
                    elif tokens[0] == "here":
                        if len(tokens) == 4:
                            print("❕ Sending all files to {} ❕".format(tokens[1]))

                            for piece in files[unique_id]:
                                # Create socket to send the files
                                send_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                send_socket.connect((tokens[2], int(tokens[3])))                              
                                # Send file details
                                filesize = os.path.getsize(piece)
                                message = "FILE {} {} {}".format(piece, filesize, unique_id)
                                try:
                                    send_socket.sendall(bytes(message, 'utf-8'))
                                    print("🚀🔥Fire Away🔥🚀")

                                    # Send file data
                                    # sendfile(filesize, piece, send_socket)

                                    progress = tqdm.tqdm(range(filesize), f"Sending {piece}", unit="B", unit_scale=True, unit_divisor=1024)
                                    with open (piece, 'rb') as source:
                                        while(True):
                                            # read the bytes from the file
                                            bytes_read = source.read(BUFFER_SIZE)
                                            if not bytes_read:
                                                # file transmitting is done
                                                break
                                            # we use sendall to assure transimission in 
                                            # busy networks
                                            send_socket.sendall(bytes_read)
                                            # update the progress bar
                                            progress.update(len(bytes_read))
                                    send_socket.close()

                                    data = ''
                                except:
                                    Exception

                    elif tokens[0] == "file":
                        if len(tokens) == 4:
                            progress = tqdm.tqdm(range(int(tokens[2])), f"Receiving {tokens[1]}", unit="B", unit_scale=True, unit_divisor=1024)
                            with open(tokens[1], "wb") as dest:
                                while True:
                                    # read 1024 bytes from the socket (receive)
                                    bytes_read = clientsock.recv(BUFFER_SIZE)
                                    if not bytes_read:    
                                        # nothing is received
                                        # file transmitting is done
                                        break
                                    # write to the file the bytes we just received
                                    dest.write(bytes_read)
                                    # update the progress bar
                                    progress.update(len(bytes_read))
                            
                            self.addfile(tokens[3], tokens[1])

                    else:
                        print(clientsock.getpeername(), "::: ", buffer)
                else:
                    break

            clientsock.close()

        def addpeer(self, uuid):
            if uuid in peer_table:
                resp = True
            else:
                resp = False

            if len(peer_table) == MAX_PEERS:
                print("❕ Peer Table Full ❕")
            else:
                if resp:
                    print("❕ Peer Already Exists ❕")
                    # Send files back
                    pass
                else:
                    if uuid != unique_id:
                        peer_table.append(uuid)
                        print("✔️ Peer added ✔️")

        def addfile(self, uuid, filename):
            if filename in files.values():
                resp = True
            else:
                resp = False

            if resp:
                print("❕ File Already Exists ❕")
            else:
                if uuid in files.keys():
                    files[uuid].append(filename)
                    print("✔️ File added ✔️")
                else:
                    files[uuid] = []
                    files[uuid].append(filename)
                    print("✔️ File added ✔️")
                

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
                        if not peer_table:
                            print("❕ No successor to connect to ❕")
                        else:
                            if unique_id in files.keys():
                                welcome_note = BroadcastSender("APPEAR {} {} {}".format(peer_table[0], IPAddr , MYPORT))
                                welcome_note.start()
                            else:
                                print("❕ No files to send to successor ❕")

                        break
                    elif message.lower() == "show files":
                        pretty = json.dumps(files, indent=4, sort_keys=True)
                        print(pretty)

                    elif message.lower() == "show peers":
                        print(peer_table)

                    elif tokens[0] == "search":
                        if len(tokens) == 2:
                            welcome_note = BroadcastSender("SEARCH {} {} {}".format(tokens[1], IPAddr , MYPORT))
                            welcome_note.start()
                    elif tokens[0] == "add":
                        if len(tokens) == 2:
                            self.addfile(unique_id, tokens[1])
                    else:
                        try:
                            send_socket.sendall(bytes(message, 'utf-8'))
                            print("🚀🔥Fire Away🔥🚀")
                        except:
                            Exception
            
            send_socket.close()
            running = 0
            return

        def addfile(self, uuid, filename):
            if filename in files.values():
                resp = True
            else:
                resp = False

            if resp:
                print("❕ File Already Exists ❕")
            else:
                if uuid in files.keys():
                    files[uuid].append(filename)
                    print("✔️ File added ✔️")
                else:
                    files[uuid] = []
                    files[uuid].append(filename)
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