### Distributed Systems Peer to Peer File Sharing System
This project is meant to connect multiple peers across a network and enable file sharing with the ability to accommodate addition of new users to the network of peers as well as handle the movement of files from one node to another when one node leaves and return of those files to the said node when it returns to the network.

## Project Members
All credit goes to the people below for the work and effort put into making this system a reality.

# Opio Andrew         18/U/21104/PS
# Nakagwe Sharifah    18/U/21144/PS
# Bakunga Bronson     18/U/23411/EVE
# Katusiime Conrad    18/U/855

## Operation
Run peer.py
The program will attempt to assign a peer a unique ID if this is their first time connecting. If that's not the case, it will read the unique ID and print it to the screen, this ID is useful because we need to remember that a peer's IP Address can change on their return to the network so we need something more persistent, and thereofore the ID mentioned above.

After running the program it starts listening on a random port between 3000 and 5000 (Lower Ports are ususally taken by system processes). Checks ports of known services in this range will be done when refactoring.

For now the program runs on a machine's localhost (127.0.0.1) but it will be setup to connect to another host once functionality is all working.

The port that the peer is listening on is what we can use to connect another node to this one we are running and vice versa. Once a connection is established, the peer that connected can send a message to the other peer. We can use "quit" to stop a connection at any time incase we want to connect to another peer. The peer where the message is sent prints it out for now but it is supposed to perform a function on receiving a certain message and return the result to the other node.

# Illustration

## Endind Program
For now the only way to end the program is to end the terminal running the program. That will be changes as we go.

