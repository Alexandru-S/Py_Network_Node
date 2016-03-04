# Alexandru Sulea
# 
# Network Ring
# Prof. Hitesh Tawari
"""
**********************************************************
*************INSTRUCTIONS FOR LAUNCHING*******************
**********************************************************
	Instructions only apply for Ubuntu as Windows proved
too unworkable and complicated, also due to unexpected 
circumstances I broke my laptop 4 days before the assignment
was due and had to make a quick repair patchwork.
----------------------------------------------------------
The software is written in python 2.7 and nodes are used to 
communicate with each other through user assigned ports.

To launch the program open the control prompt and type:
python node.py [currentport] [newport] [ID(number)]

**********************************************************
*******************THE END********************************
**********************************************************
"""
import sys
import os
import socket
import select
import time
import thread
import select
import sets
import pickle
listen = int(sys.argv[1])
send = int(sys.argv[2])
id = int(sys.argv[3])
node_num = 4
class Packet():
    source = "uninit"
    dest = "uninit"
    data = "uninit"
    token = 0
    ack = 0
    arp = 0
    
    def __init__(self, so, de, da, to, ac, ar):
        self.source = so
        self.dest = de
        self.data = da
        self.token = to
        self.ack = ac
        self.arp = ar

class Node():    
    def __init__(self):
        self.join_ring(id, listen, send)
    def token_ring_monitor(self, listenSocket, nextSocket):
    	  print "SUCCESS!!! -----> Stuff Happened<--------\n"
        print "Node %s | Designated as monitor" %id
        lastnode = [] 
        currentnode = [] 
        timer = 0            
        
        for x in range(node_num):
            lastnode.append(x)
            currentnode.append(x)

        while(1):
            time.sleep(3)
            timer = timer + 3
            userinput, w, x = select.select([sys.stdin], [], [], 0)
            if userinput:
                message = userinput[0].readline().split()
                if message[0] == 'death':
                	  print "Node looking longingly into the distance\n"
        		  time.sleep(3)
        		  print "Node tieing noose\n"
        		  print "*feet kicking \n*"
        		  time.sleep(3)
                    print "Monitor | *choking noises*\n "
                    print "#death "
                    self.death(listenSocket, nextSocket)
                if message[0] == 'q':
                    mypacket = Packet(id, 999, "monitor quitting", 0, 0, 0)
                else:
                    mypacket = Packet(id, 999, message[0], 0, 0, 0)
                to_send = pickle.dumps(mypacket)
                nextSocket.send(to_send)
            
            try:
                dataavailable, w, x = select.select([listenSocket], [], [], 0)
                if dataavailable:
                    wiredata = listenSocket.recv(512)
                    if wiredata:
                        packet = pickle.loads(wiredata)

                        print "Monitor | data: '%s' src: %s dest: %s token: %s pack: %s amessage: %s" %(packet.data, packet.source, packet.dest, packet.token, packet.ack, packet.arp)
                        if packet.token == 1:
                                to_send = pickle.dumps(packet)
                                nextSocket.send(to_send)
                        if packet.token == 0:
                            if packet.arp == 0 and packet.dest != 999:
                                if (int(packet.dest) in currentnode):
                                    to_send = pickle.dumps(packet)
                                    nextSocket.send(to_send)
                                else:
                                    print "Monitor | orphan packet found, src: %s, dest: %s, destroying, sending n-ack" %(packet.source, packet.dest)
                                    nack = Packet(packet.source, id, "Packet not delivered", 0, 2, 0)
                                    to_send = pickle.dumps(nack)
                                    nextSocket.send(to_send)
                                    
                        if packet.arp == 0 and packet.dest == 999:
                            print "Monitor | destroying broadcast" 
                        if packet.arp == 1 and packet.source == id and packet.dest != id:
                            print "Monitor | WARNING No reply from node %s WARNING" %packet.dest
                        if packet.arp == 2:
                            print "Monitor | reply from node %s" %packet.source
                            currentnode.append(packet.source)
                        if packet.arp == 1 and packet.source == id and packet.dest == id:
                            print "Monitor | Received own request"
                            currentnode.append(id)

                if timer == 30:
                    currentnode = list(set(currentnode))
                    lastnode = list(set(lastnode))
                    print "Monitor | Current nodes: %s" %currentnode
                    print "Monitor | Previous nodes: %s" %lastnode
                    if currentnode == lastnode:
                        print "---ok"
                    else:
                        s0 = sets.Set(currentnode)
                        s1 = sets.Set(lastnode)
                        error_nodes = list(s1.difference(s0))
                        print "Monitor | WARNING - changes: %s WARNING updating table" %error_nodes
                    
                    print "#Sending "
                    for x in range(len(currentnode)):
                        arp = Packet(id, currentnode[x], None, 0, 0, 1)
                        to_send = pickle.dumps(arp)
                        nextSocket.send(to_send)
                    timer = 0
                    lastnode = currentnode
                    currentnode = []

            except Exception, e:
                continue; sys.stdout.flush()
                print "While loop exception"
                time.sleep(2)
                return -1

    def token_ring_node(self, listenSocket, nextSocket):
        first_pass = 1
        wantToken = 0
        awaitAck = 0
        monitor_timer = 0
        send_buffer = []
        print 'Node %s | entering token_ring()' % id
        while(1):
            if id == 0 and first_pass == 0:
                self.token_ring_monitor(listenSocket, nextSocket)
            if first_pass == 1 and id == 0:
                first_pass = 0
                token = Packet(None, None, None, 1, 0, 0)
                print "Node %s | creating first token" % id
                to_send = pickle.dumps(token)
                nextSocket.send(to_send)           
            userinput, w, x = select.select([sys.stdin], [], [], 0)
            if userinput:
                message = userinput[0].readline().split()
                wantToken = 1
                if message[0] == 'death':
                	  print "NOOOOOooooooooooooo\n"
                	  time.sleep(3)
                    print "Node %s | *choking noises* " %id
                    self.death(listenSocket, nextSocket)
                print "Node %s | Wish to send, awaiting token" % id
                if message[0] == 'q':
                	  print("Dont give up on me man !!!")
                	  time.sleep(3)
                    mypacket = Packet(id, 999, "quitting", 0, 0, 0)
                else:

                    mypacket = Packet(id, message[0], message[1], 0, 0, 0)
                to_send = pickle.dumps(mypacket)
                send_buffer.append(to_send)
            
            try:

                dataavailable, w, x = select.select([listenSocket], [], [], 0)
                if dataavailable:
                    wiredata = listenSocket.recv(512)
                    if wiredata:
                        packet = pickle.loads(wiredata)

                        if packet.token == 1:
                            if wantToken == 0:
                                print "Node %s | got token - dont want - passing token to the next node...somewhere out there" % id
                                resend = pickle.dumps(packet)
                                nextSocket.send(resend)

                            if wantToken == 1:
                                print "Node %s | got token - wish to send - sending my packet" %id
                                to_send = send_buffer.pop()
                                nextSocket.send(to_send)
                                print "Node %s | Packet sent - Awaiting pack - Buffer size: %s" %(id, len(send_buffer))
                                awaitAck = 1
                                if len(send_buffer) == 0:
                                    wantToken = 0

                        if packet.token == 0:
                            if packet.ack == 0 and packet.arp == 0:
                                if packet.source != None:
                                    if int(packet.dest) != id and int(packet.dest) != 999:
                                        print "Node %s | Have someone else's packet - passing on" %id
                                        resend = pickle.dumps(packet)
                                        nextSocket.send(resend)
                                
                                    if int(packet.dest) == id:
                                        print "Node %s | Received a packet for me. It says '%s'" %(id, packet.data)
                                        print "Node %s | Sending pack" %id
                                        ack = Packet(packet.source, id, None, 0, 1, 0)
                                        to_send = pickle.dumps(ack)
                                        nextSocket.send(to_send)
                                    
                                    if int(packet.dest) == 999:
                                        print "Node %s | Received a broadcast - It says '%s'" %(id, packet.data)
                                        to_send = pickle.dumps(packet)
                                        nextSocket.send(to_send)

                            if packet.ack == 1:
                                if packet.source == id:
                                    print "Node %s | received my ack, placing free token back on wire" % id
                                    token = Packet(None, None, None, 1, 0, 0)
                                    to_send = pickle.dumps(token)
                                    awaitAck = 0
                                    nextSocket.send(to_send)
                                
                                if packet.source != id:
                                    print "Node %s | received someone else's pack, passing on" %id
                                    to_send = pickle.dumps(packet)
                                    nextSocket.send(to_send)
                            
                            if packet.ack == 2:
                                if packet.source == id:
                                    print "Node %s | Received pack. It says %s" %(id, packet.data)
                                    token = Packet(None, None, None, 1, 0, 0)
                                    to_send = pickle.dumps(token)
                                    awaitAck = 0
                                    nextSocket.send(to_send)
                                
                                if packet.source != id:
                                    print "Node %s | received someone else's pack....whoops, passing on" %id
                                    to_send = pickle.dumps(packet)
                                    nextSocket.send(to_send)

                        if packet.arp == 1:
                            if packet.dest == id:
                                print "Node %s | received  - mine - replying" %id
                                arp_reply = Packet(id, packet.source, "Still Alive", 0, 0, 2)
                                to_send = pickle.dumps(arp_reply)
                                nextSocket.send(to_send)
                                monitor_timer = 0
                            else:
                                print "Node %s | received for node %s - passing" %(id, packet.dest)
                                arp = Packet(packet.source, packet.dest, packet.data, 0, 0, 1)
                                to_send = pickle.dumps(arp)
                                nextSocket.send(to_send)

                        if packet.arp == 2:
                            print "Node %s | received reply from node %s - passing" %(id, packet.source)
                            arp = Packet(packet.source, packet.dest, packet.data, 0, 0, 2)
                            to_send = pickle.dumps(arp)
                            nextSocket.send(to_send)

                        if packet.arp == 9 and packet.token == 9:
                            print "Node %s | Node %s says monitor is down. Monitor election time" %(id, packet.source)
                            print "Node %s | VOTE BEGINS - sending vote packet" %id
                            vote = Packet(id, 999, "vote", 8, 8, 8)
                            to_send = pickle.dumps(vote)
                            nextSocket.send(to_send)

                        if packet.arp == 8 and packet.token == 8:
                            if packet.source > id:
                                print "Node %s | VOTE: Higher ID found. Conceeding and passing" %id
                                to_send = pickle.dumps(packet)
                                nextSocket.send(to_send)
                            if packet.source < id:
                                print "Node %s | VOTE: Lesser ID found, discarding" %id
                            if packet.source == id:
                            	  print "Fistfight ensues*"
                            	  print "KPOOOW"
                            	  time.sleep(3)
                                print "Node %s | VOTE: Own ID found. WINENR!" %id
                                self.token_ring_monitor(listenSocket, nextSocket)  
            except Exception, e:
                continue; sys.stdout.flush()
                print "While loop exception"
                time.sleep(2)
            
            time.sleep(3)
            monitor_timer = monitor_timer + 3

            if monitor_timer == 20:
                print "Node %s | No messagein 20 seconds monitor may be down" %id
            if monitor_timer == 40:
                print "Node %s | No message in 40 seconds. Monitor probably down. Asking other nodes " %id
                monitor_request = Packet(id, 999, "Monitor down for me", 9, 9, 9)
                to_send = pickle.dumps(monitor_request)
                nextSocket.send(to_send)

    def join_ring(self, id, listen, send):
        print "listen = %s | send = %s | id = %s" %(listen,send,id) 
        listenSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        nextSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            listenSocket.bind(('localhost', listen))
        except Exception, e:
            print 'Failed on initial listener bind'
            return -1
        time.sleep(5)
        print 'Attempting to connect to next node on port %s' % send
        try:
            nextSocket.connect(('localhost', send))
        except Exception, e:
            print 'Failed on initial sender bind'
            return -1
        self.token_ring_node(listenSocket, nextSocket)
    def death(self, listenSocket, nextSocket):
        while 1:
            try:
                dataavailable, w, x = select.select([listenSocket], [], [], 0)
                if dataavailable:
                    wiredata = listenSocket.recv(512)
                    if wiredata:
                        nextSocket.send(wiredata)
            except Exception, e:
                print "loop fail"
                print "THE END"
                return -1
def main():
    node = Node()
if __name__ == "__main__":
    main()

