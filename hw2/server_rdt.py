from subprocess import call
from sys import argv
import threading
import hashlib
import cPickle
import socket
import sys
import os

threadNum = 0
threads = []
serverAddress = [("10.10.2.2", 50000), ("10.10.4.2", 50001)]


def recieverFunc():
    expectedPacketNumber = 0  ## We used this variable to keep track of order of coming packages
    uniqueCheckSum = 314159  ## This is used to detect corrupted files.

    currentThreadNum = threading.currentThread().getName().split('-')[1]
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    serverSocket.bind(('', serverAddress[int(currentThreadNum) - 1][1]))
    outFile = "output" + currentThreadNum + ".txt"
    target = open(outFile, 'w')

    while True:  ## 'Server is Waiting : '
        expectedPacketNumber += 1

        ## We take data and then deserialize it using cPickle
        clientData, address = serverSocket.recvfrom(57344)
        clientData = cPickle.loads(clientData)
        ## clientData Consist of 2 Part;
        ## First Part is the message header
        ## Second part is the origal message

        ## Coming message header schema is below
        ## messageHeader = (clientAddr, destinationAddr, packetNumber, checkSum, finFlag)
        clientDataHeader = clientData[0]
        originalMessage = clientData[1]

        ## We calculate expectedCheckSum
        ## Exact formula is that checkSum = md5(message + uniqueCheckSum)
        ## Then we will compare this data to check message is changed or not.
        expectedCheckSum = hashlib.md5();
        expectedCheckSum.update(originalMessage + str(uniqueCheckSum))
        expectedCheckSum = expectedCheckSum.digest()

        ## We fetch necassary informations from header
        clientAddr = clientDataHeader[0]
        messagePacketNumber = clientDataHeader[2]
        messageCheckSum = clientDataHeader[3]

        ## If coming message is corrupted send old succesfully recieved packet's ACK to get a retransmission of corrputed package
        if messageCheckSum != expectedCheckSum:
            messagePacketNumber = expectedPacketNumber - 1
            expectedPacketNumber = expectedPacketNumber - 1
        ## If the expected packet number and the coming packet number does not match, there is a lost packet. Change server response to Send previously successful ACK
        elif messagePacketNumber != expectedPacketNumber:
            ##print "ERROR !! Coming Packet NO:",messagePacketNumber," Expected :", expectedPacketNumber
            messagePacketNumber = expectedPacketNumber - 1
            expectedPacketNumber = expectedPacketNumber - 1
        else:
            ## If data is in-order and not corrupted, Write it to output channel.
            target.write(originalMessage)
            sys.stdout.flush()
            ## If the finish flag is arrived, close the server after sending related ACK message.
            if (clientDataHeader[4] == True):
                break

        ## Then send back a reponse message
        ## If it is broken, the previous succesfully ACK is selected above.
        messagePacketNumber = cPickle.dumps(messagePacketNumber)
        serverSocket.sendto(messagePacketNumber, clientAddr)

    serverSocket.close()


if __name__ == "__main__":

    outputFileNames = "cat "
    threadNum = int(argv[1])
    for i in range(threadNum):
        # created thread
        t = threading.Thread(target=recieverFunc)
        # append thread array
        threads.append(t)
        outputFileNames += "output" + str((i + 1)) + ".txt "
        # thread start
        t.start()
    for i in range(threadNum):
        threads[i].join()
    outputFileNames += "> output.txt"
    ## Creating threads and starting them in order.
    ## After all threads are over, we need to merge the output files into single file. and delete the pieces
    os.system(outputFileNames)
    ##os.system('rm -f output1.txt; rm -f output2.txt; rm -f output3.txt;')*
