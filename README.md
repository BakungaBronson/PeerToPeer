### Distributed Systems Peer to Peer File Sharing System
This project is meant to connect multiple peers across a network and enable file sharing with the ability to accommodate addition of new users to the network of peers as well as handle the movement of files from one node to another when one node leaves and return of those files to the said node when it returns to the network.

## Project Members
All credit goes to the people below for the work and effort put into making this system a reality.

+ Opio Andrew         18/U/21104/PS
+ Nakagwe Sharifah    18/U/21144/PS
+ Bakunga Bronson     18/U/23411/EVE
+ Katusiime Conrad    18/U/855

## Operation
Run peer.py
The program will attempt to assign a peer a unique ID if this is their first time connecting. If that's not the case, it will read the unique ID and print it to the screen, this ID is useful because we need to remember that a peer's IP Address can change on their return to the network so we need something more persistent, and thereofore the ID mentioned above.

After running the program it starts listening on a random port between 3000 and 5000 (Lower Ports are ususally taken by system processes). Checks for ports of known services in this range will be done when refactoring.

The program can now run on two nodes (computers) on the same LAN. The IP address of the host on the LAN on needs to be known since it is what is used instead of localhost. However it can also be tested on a the localhost by cloning this folder multiple times so that they do not share the same config file. The address in that case would be 127.0.0.1 for both peers.

# Features
+ Can notice the return of a peer even if they connect to another node in the network. The node which has the peer in their peer table then connects to them and sends them their files.
+ Can search for files across the peer network. The node with the file then connects to the peer and sends the file to them which they add to their files table.
+ Can add a peer to the peer table when it connects.
+ Has a maximum number of peers listed on starting the program and will notify the user once the table is full.
+ Resources are shared 1:1 and there is no connections in between to other nodes.
+ Can scale and have a node connect to any other node as long as their peer table is not full.

# Missing features
+ File sending
+ Node sending files to it's successor when leaving the network (It notices when a node has left the network though)
+ Handling all exceptions, most have been caught though

The port that the peer is listening on is what we can use to connect another node to this one we are running and vice versa. Once a connection is established, the peer that connected can send a message to the other peer. We can use "quit" to stop a connection at any time incase we want to connect to another peer. The peer where the message is sent prints it out for now but it is supposed to perform a function on receiving a certain message and return the result to the other node.

# Illustration
![image](https://user-images.githubusercontent.com/51344005/147847562-2f01f116-c160-465e-b69d-61a99441b7c3.png)
*Red Arrow* The listening port we have on the other peer is what we connect to on the second peer.

*Blue Arrow* The user can still enter the host and port on the other machine even when someone connects to them.

## Ending Program
For now the only way to end the program is to end the terminal running the program. That will be changes as we go.

