import socket
from sctp import *
from sys import argv
import threading

import time
import sys

MAX_SEGMENT_SIZE = 1000  ## Message Segment size is calculated by 1000 - sizeof(messageHeader)

##GLOBAL VARIABLES
inputFile = ''
threads = []
threadNum = 0
clientAddr = [("10.10.1.1", 50000), ("10.10.3.1", 50001)]
destinationAddr = [("10.10.2.2", 50000), ("10.10.4.2", 50001)]
isFinish = False
isItLastFile = False
# finish message flag
finishMessage = "~sbkbaris17"
lastFileMessage = "~lastEOF17"


# time function to calculate
# tstart = time.time()
# tfinish = 0

def sender(messageLen, messageOffset):
    # connect to global variable(s)
    global isFinish
    global isItLastFile
    # global tfinish
    # global tstart

    # Getting thread no which thread run
    currentThreadNum = threading.currentThread().getName().split('-')[1]
    # Select destination server IP and port no by using thread send data
    currentDestinationAddr = destinationAddr[int(currentThreadNum) - 1]
    sendingMessage = ""
    print("SCTP:", currentDestinationAddr[0])
    try:
        # control whether data is finish or not
        # messageLen is data length
        # messageOffset is where data start to send in inputfile
        while messageOffset < messageLen:
            # start sctp socket
            sctp = sctpsocket_tcp(socket.AF_INET)
            # connect destionation server to send data
            sctp.connect(currentDestinationAddr)
            # control sendingPacket is last one or not. If it is last packet, send it in starting messageOffset
            # if it is not, just send it in starting messageOffset and ending messageOffset + MAX_SEGMENT_SIZE
            if messageOffset + MAX_SEGMENT_SIZE > messageLen:
                sendingMessage = inputMessage[messageOffset:]
                isFinish = True
                # check end of file
                if int(currentThreadNum) == 2:
                    isItLastFile = True
            else:
                sendingMessage = inputMessage[messageOffset:messageOffset + MAX_SEGMENT_SIZE]
            # update messageOffset for next packet
            messageOffset = messageOffset + MAX_SEGMENT_SIZE
            # send data
            sctp.send(sendingMessage)

            # we used time sleep for solving connection refused and after collecting data, we subsract it in all times.
            # time.sleep(0.2)

            # socket shutdown and close it.
            sctp.shutdown(1)
            sctp.close()
        # if packet is finished, send finish flag to know that file is finish
        if isFinish == True:
            # Again socket operation like above.
            if isItLastFile == True and int(currentThreadNum) == 2:
                message = finishMessage + lastFileMessage

            else:
                message = finishMessage
            sctp = sctpsocket_tcp(socket.AF_INET)
            sctp.connect(currentDestinationAddr)
            sctp.send(message)
            sctp.shutdown(1)
            sctp.close()

            # tfinish = time.time()
    finally:
        pass


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
    sys.stdout.flush()
    for i in range(threadNum):
        # created thread which arrange messageOffset with respect to experiment no
        t = threading.Thread(target=sender, args=((msgSize * (i + 1)) / threadNum, (msgSize * i) / threadNum,))
        # append thread array
        threads.append(t)
        # thread start
        t.start()
    for i in range(threadNum):
        threads[i].join()
