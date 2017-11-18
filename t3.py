import socket
import sys
#import cPickle
import time

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
# (destination, forwarding)


# Create a TCP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
own_address = t3
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
            if data:
                print >> sys.stderr, 'starting up on %s port %s' % server_address
                connection.sendall(data)
                time.sleep(0.05)
            else:
                print >> sys.stderr, 'no more data from', client_address
                break
    finally:
        connection.close()




