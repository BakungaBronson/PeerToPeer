import socket
import threading
import random
import sys
import uuid
from configparser import ConfigParser
from hash_table import Hashtable

LOCALHOST = '127.0.0.1'
BUFFER_SIZE = 2048

def main():
    running = 0

    class ChatListener(threading.Thread):

        def __init__(self):
            threading.Thread.__init__(self)
            self.port = None
            self.address = None

            # The Hashtable that will store the keys and values, it has a maximum of 10 
            # buckets where it can store data
            self.table = Hashtable(10)

            print("❕ Initialising ❕")
            try:
                # Read config.ini file
                config_object = ConfigParser()
                config_object.read("config.ini")

                # Get the uuid
                userinfo = config_object["USERDATA"]
                print("🔑 UUID is {} 🔑".format(userinfo["uuid"]))
                self.uuid = userinfo["uuid"]

            except:
                print("🆕 Config file doesn't exist. Creating unique user ID... 🆕")
                
                # Generate a random uuid string
                config_object["USERDATA"] = {
                    "uuid": uuid.uuid4(),
                }

                #Write the above sections to config.ini file
                with open('config.ini', 'w') as conf:
                    config_object.write(conf)
                    print("⚙️ Config Created ⚙️")
                    print("🔑 UUID is {} 🔑".format(config_object["USERDATA"]["uuid"]))

        def run(self):
            listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            listen_socket.bind((LOCALHOST, self.port))
            listen_socket.listen(5)

            while True:

                clientsock, address = listen_socket.accept()
                print("\nEstablished connection with: ", clientsock.getpeername())
                getMessages = threading.Thread(target = self.handleConnection, args=[clientsock])
                getMessages.start()

            listen_socket.close()

        def handleConnection(self, clientsock):

            while True:
                buffer = ''
                message = clientsock.recv(BUFFER_SIZE).decode()
                
                if message:
                    buffer += message
                    print(clientsock.getpeername(), "::: ", buffer)
                    if buffer == "SEARCH" or buffer == "search":
                        print("Searching for file...")
                else:
                    break

            clientsock.close()
                

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
            while True:

                message = input()

                if message.lower() == "quit":
                    
                    break
                else:
                    try:
                        send_socket.sendall(bytes(message, 'utf-8'))
                        print("🚀🔥Fire Away🔥🚀")
                    except:
                        Exception
            
            send_socket.close()
            running = 0
            return

    chat_listener = ChatListener()
    chat_listener.port = random.randint(3000, 5000)
    chat_listener.start()
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
                print("Keyboard Interrupt: Exiting")
                sys.exit()

if __name__ == "__main__":
    main()