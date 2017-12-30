import socket
from sctp import *
import sys
import threading
from sys import argv
import os
import time

##GLOBAL VARIABLES
threadNum = 0
threads = []

##Server Adress
serverAddress = [("10.10.2.2", 50000), ("10.10.4.2", 50001)]
outputFiles = []


def receiveFunc():
    # Getting thread no which thread run
    currentThreadNum = threading.currentThread().getName().split('-')[1]
    # Select current server IP and port no by using thread getting data
    currentServer = serverAddress[int(currentThreadNum) - 1]
    # start sctp socket
    sctp = sctpsocket_tcp(socket.AF_INET)
    # current server is binded to listen
    sctp.bindx([currentServer])
    # sctp socket listen method
    sctp.listen(1)
    # created specific output file for thread since all threads do their own job and write file.
    outFile = "output" + currentThreadNum + ".txt"
    while True:
        # getting data and client addres
        connection, client_address = sctp.accept()
        # getting data
        data = connection.recv(1000)
        # checking finish flag, if it is true, sending file operation is done and merge the threads' output (1 or 2 for experiment) file.
        # If it is not done, write data in the threads' output file.

        # check end of file or thread end
        if data == "~sbkbaris17~lastEOF17" or data == "~sbkbaris17":
            if data == "~sbkbaris17~lastEOF17":
                merge()
                break
            else:
                break
        else:
            writeFile(outFile, data)

        sys.stdout.flush()
    # sctp socket close
    sctp.close()


# writing in file function
def writeFile(fileName, data):
    target = open(fileName, 'a')
    target.write(data)
    target.close()


# merge all threads' output file (1 or 2 for experiment) into one file by using cat command.
def merge():
    outputFileNames = "cat "
    for i in range(len(outputFiles)):
        outputFileNames += "output" + str((i + 1)) + ".txt "
    outputFileNames += "> output.txt"
    os.system(outputFileNames)


if __name__ == "__main__":
    # getting experiment no
    threadNum = int(argv[1])
    for i in range(threadNum):
        # created thread
        t = threading.Thread(target=receiveFunc)
        # append thread array
        threads.append(t)
        # to use merge function, all threads' output file collect one array.
        outputFiles.append("output" + str((i + 1)) + ".txt")
        # thread start
        t.start()
    for i in range(threadNum):
        threads[i].join()
