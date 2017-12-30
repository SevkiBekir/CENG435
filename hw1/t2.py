import socket
import sys
#import cPickle
#import time

# Network IPs and ports in the linear topology.
t1 = ('10.10.1.1', 30211)
gateway2t1 = ('10.10.1.2',30211)
gateway2t2 = ('10.10.3.1',30212)
t2 = ('10.10.3.2', 30212)
t3 = ('10.10.5.2', 30213)

# t3 = ('10.10.1.1', 30211)
# u1 = ('10.10.2.1', 30221)
# u2 = ('10.10.1.1', 30211)
# u3 = ('10.10.1.1', 30211)
# gateway = ('10.10.1.1', 30211)

# Routing table includes destination and next hop.
# routing_table = [(router_B, router_B), (router_C, router_B), (router_D, router_B), (server_E, router_B)]
# (destination, forwarding)

routingTable = [(t2,t2),(t1,gateway2t1),(t3,t3)]

# Create a TCP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
own_address = t2
server_address = own_address

print >>sys.stderr, 'starting up on %s port %s' % server_address
sock.bind(server_address)
# Listen for incoming connections
sock.listen(1)

while True:
    # Wait for a connection
    print >>sys.stderr, 'waiting for a connection'
    connection, client_address = sock.accept()

    try:
        print >> sys.stderr, 'connection from', client_address

        # Receive the data in small chunks and retransmit it
        while True:
            data = connection.recv(4096)


            print >> sys.stderr, 'received "%s"' % data
            forwarding_address = ()
            if data:
                destination_ip = data.split('*')[0]
                destination_port = data.split('*')[1]
                msg = data.split('*')[4]
                print(destination_ip)
                print(destination_port)
                dest = (destination_ip,int(destination_port))
                print(dest)
                print("Dest finito")
                #forwarding_address = ()
                for ip_address in routingTable:
                    print("for in")
                    print(ip_address[0])
                    print("ip address 0")

                    if dest == ip_address[0]:
                        print("Founded!!!")
                        forwarding_address = ip_address[1]
                        break
                    else:
                        print("Not Found!")


                #print >> sys.stderr, 'sending data to %s' % forwarding_address
                sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock2.connect(forwarding_address)
                try:
                    sock2.sendall(data)
                    print >> sys.stderr, 'starting up on %s port %s' % server_address
                    connection.sendall(data)
                finally:
                    sock2.close()
            else:
                print >> sys.stderr, 'no more data from', client_address
                break

    finally:
        # Clean up the connection
        connection.close()
