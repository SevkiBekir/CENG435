from socket import timeout
from sys import argv
import threading
import hashlib
import cPickle
import sys
import socket
import time

## GLOBAL VARIABLES
MAX_SEGMENT_SIZE = 900  ## Message Segment size is calculated by 1000 - sizeof(messageHeader)
WINDOW_SIZE = 5
uniqueCheckSum = 314159
inputFile = '';
threads = []
threadNum = 0
clientAddr = [("10.10.1.1", 50000), ("10.10.3.1", 50001)]
destinationAddr = [("10.10.2.2", 50000), ("10.10.4.2", 50001)]


# tstart = []
# tstart.append(time.time())


## We define a transmission function to provide multithreading. It takes 2 argument.
## One of them is messageLenth for a specific port and the other is a startingOffSetm
def senderFunc(messageLen, messageOffset):
    messageLength = messageLen  ## Message length

    ## Closure flag is used to tell the server for closure.
    ## It is like a FIN flag of TCP.
    ## With the final message, It will be set True

    closureFlag = False

    ## Closure counter is used to close the this client socket.
    ## After the number of closureCounter ms, client thinks that there is a problem with server and closes connection.
    ## This will specificly used for the possibilty of not getting closure signal from server.
    closureCounter = 0

    ## For the non-delivered packages GoBackN method is used.
    counterGoBackN = 0

    currentThreadNum = threading.currentThread().getName().split('-')[1]
    currentClientAddr = clientAddr[int(currentThreadNum) - 1]
    currentDestinationAddr = destinationAddr[int(currentThreadNum) - 1]

    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    clientSocket.bind(('', currentClientAddr[1]))
    clientSocket.settimeout(1)
    packetNumber = 0

    ## In this while loop, we sent message piece by piece. After sending whole message we can stop.
    while messageOffset < messageLength:

        ## We can only transmit MAX_SEGMENT_SIZE byte of message at a unit time.
        ## We must make sure that we took enough size of message, and there is nothing left behind.

        if messageOffset + MAX_SEGMENT_SIZE > messageLength:  ## This means we reach the end of message
            messagePart = inputMessage[messageOffset:messageLen]  ## Take the remaning last piece
            closureFlag = True  ## Let server know that it is the last piece
        else:  ## That means we have still more message then MAX_SEGMENT_SIZE
            messagePart = inputMessage[
                          messageOffset:messageOffset + MAX_SEGMENT_SIZE]  ## Take the only MAX_SEGMENT_SIZE
        messageOffset += MAX_SEGMENT_SIZE;  ## Increment the offSet

        ## CheckSum will be calculating by using md5 function of python
        ## Exact formula is that checkSum = md5(message + uniqueCheckSum)
        ## Only sender and receiver knows this unique number. It is chosen as prime number.
        checkSum = hashlib.md5()
        checkSum.update(messagePart + str(uniqueCheckSum))
        checkSum = checkSum.digest()

        ## Packet number is used to keep track of package order between client and server
        packetNumber += 1

        ## Message header is used to ease provide RDT.
        ## It contains client, server addresses, package number (for order), checkSum (to check corruption in Message,
        ## and closureFlag to let server to close connection)
        messageHeader = (currentClientAddr, currentDestinationAddr, packetNumber, checkSum, closureFlag)

        ## Message segment is a segment that will be sent to server. It contains messageHeader and original message.
        ## cPickle is used to serialize the segment to send via socket.
        messageSegment = (messageHeader, messagePart)
        messageSegment = cPickle.dumps(messageSegment)

        clientSocket.sendto(messageSegment, currentDestinationAddr)

        counterGoBackN += 1

        ## After sending WINDOW_SIZE package back-to-back, client waits for the ACK messages from server for each package.
        if (counterGoBackN == WINDOW_SIZE):
            try:
                for i in range(counterGoBackN):
                    serverResponse, address = clientSocket.recvfrom(4096)
            except timeout:
                ## If There is timeout event, It is because of the packet or the ack might be lost, Then re-transmit whole window.
                messageOffset = messageOffset - MAX_SEGMENT_SIZE * counterGoBackN
                packetNumber = packetNumber - counterGoBackN
                counterGoBackN = 0
            else:
                serverResponse = cPickle.loads(serverResponse)
                ## Check last-response, If It is not equal the last packet number, the order might be wrong. Then re-transmit whole window.
                if (serverResponse != packetNumber):
                    messageOffset = messageOffset - MAX_SEGMENT_SIZE * counterGoBackN
                    packetNumber = packetNumber - counterGoBackN
                counterGoBackN = 0
        else:
            ## If window is not, and we were preparing the close the connection, we need to wait for the final ACK from the server
            if closureFlag:
                try:
                    for i in range(counterGoBackN):
                        serverResponse, address = clientSocket.recvfrom(4096)
                except timeout:
                    closureCounter += 1
                    ## If we can not get response in 3 timeout event, that means server is closed and last ACK is lost on the way. We can close the socket.
                    if closureCounter == 3:
                        break;
                        ## If There is timeout event, It is because of the packet or the ack might be lost, Then re-transmit whole window.
                    messageOffset = messageOffset - MAX_SEGMENT_SIZE * counterGoBackN
                    packetNumber = packetNumber - counterGoBackN
                    counterGoBackN = 0
                else:
                    serverResponse = cPickle.loads(serverResponse)
                    ## Check last-response, If It is not equal the last packet number, the order might be wrong. Then re-transmit whole window.
                    ##print "ACKED :",serverResponse,". packet"
                    if (serverResponse != packetNumber):
                        messageOffset = messageOffset - MAX_SEGMENT_SIZE * counterGoBackN
                        packetNumber = packetNumber - counterGoBackN
                    counterGoBackN = 0
    # socket close
    clientSocket.close()

    # tstart.append(time.time())
    # t =tstart[1] - tstart[0]
    # print(t)


if __name__ == "__main__":
    # getting input file
    inputFile = argv[1]
    # getting experiment no
    threadNum = int(argv[2])
    # read input file and fill inputMessage array.
    with open(inputFile) as inp:
        inputMessage = inp.read()
    sys.stdout.flush()
    # calculate input file size
    msgSize = len(inputMessage)
    for i in range(threadNum):
        # created thread which arrange messageOffset with respect to experiment no
        t = threading.Thread(target=senderFunc, args=((msgSize * (i + 1)) / threadNum, (msgSize * i) / threadNum,))
        # append thread array
        threads.append(t)
        # thread start
        t.start()
    for i in range(threadNum):
        threads[i].join()
