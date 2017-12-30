import socket
import sys
#import cPickle
import time

# Network IPs and ports in the linear topology.
t1 = ('10.10.1.1', 30211)
gateway2t1 = ('10.10.1.2',30211)
t2 = ('10.10.3.2', 30212)
t3 = ('10.10.5.2', 30213)
# t2 = ('10.10.1.1', 30211)
# t3 = ('10.10.1.1', 30211)
# u1 = ('10.10.2.1', 30221)
# u2 = ('10.10.1.1', 30211)
# u3 = ('10.10.1.1', 30211)
# gateway = ('10.10.1.1', 30211)

# Routing table includes destination and next hop.
# routing_table = [(router_B, router_B), (router_C, router_B), (router_D, router_B), (server_E, router_B)]
# (destination, forwarding)
routingTable = [(t2,gateway2t1),(gateway2t1,gateway2t1),(t3,gateway2t1)]
# Create a TCP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
own_address = t1
server_address = gateway2t1
print >>sys.stderr, 'connecting to %s port %s' % server_address

sock.connect(server_address)

try:

    # Send data
    message = t3[0] + "*" + str(t3[1]) + "*" + own_address[0] + "*" + str(own_address[1]) + "*" + "SBK"

    print >> sys.stderr, 'sending "%s"' % message
    sock.sendall(message)

    # Look for the response
    amount_received = 0
    amount_expected = len(message)

    while amount_received < amount_expected:
        data = sock.recv(4096)
        amount_received += len(data)
        print >> sys.stderr, 'received "%s"' % data

finally:
    print >> sys.stderr, 'closing socket'
    sock.close()

