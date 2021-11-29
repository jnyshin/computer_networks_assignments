from ctypes import sizeof
import os
import sys
import struct
import time
import select
from socket import *
import binascii

ICMP_ECHO_REQUEST = 8


def checksum(str):
    csum = 0
    countTo = (len(str) / 2) * 2

    count = 0
    while count < countTo:
        #thisVal = ord(str[count + 1]) * 256 + ord(str[count])
        thisVal = str[count + 1] * 256 + str[count]
        csum = csum + thisVal
        csum = csum & 0xffffffff  # does "L" need to be attatched at the end?
        count = count + 2

    if countTo < len(str):
        #csum = csum + ord(str[len(str) - 1])
        csum = csum + str[len(str) - 1]
        csum = csum & 0xffffffff  # does "L" need to be attatched at the end?

    csum = (csum >> 16) + (csum & 0xffff)
    csum = csum + (csum >> 16)
    answer = ~csum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer


def receiveOnePing(mySocket, ID, timeout, destAddr):
    global rtt_min, rtt_max, rtt_sum, rtt_cnt
    timeLeft = timeout
    while 1:

        startedSelect = time.time()
        whatReady = select.select([mySocket], [], [], timeLeft)
        howLongInSelect = (time.time() - startedSelect)
        if whatReady[0] == []:  # Timeout
            return "Request Timeout 1. "

        timeReceived = time.time()
        recPacket, addr = mySocket.recvfrom(1024)

        #Fill in start

        #Fetch the ICMP header from the IP packet

        ttl = recPacket[8]
        icmp = recPacket[20:28]
        type, code, csum, id, seq = struct.unpack("bbHHh", icmp)
        size = len(recPacket)
        rtt = round((timeReceived - startedSelect) * 1000, 2)

        #print only when appropriate Echo Reply comes in. type == 0 AND code == 0
        if type == 0 and code == 0:
            rtt_cnt += 1
            if rtt < rtt_min:
                rtt_min = rtt
            if rtt > rtt_max:
                rtt_max = rtt
            rtt_sum += rtt
            return (
                "{} bytes from {}: icmp_seq={} ID={} ttl={} time={} ms".format(
                    size, destAddr, seq, id, ttl, rtt))

        # print(
        #     ttl,
        #     addr,
        #     size,
        #     rtt,
        # )

        #Fill in end

        timeLeft = timeLeft - howLongInSelect
        if timeLeft <= 0:
            return "Request timed out 2."


def sendOnePing(mySocket, destAddr, ID, cnt):
    # Header is type (8), code (8), checksum (16), id (16), sequence (16)

    myChecksum = 0
    # Make a dummy header with a 0 checksum.
    # struct -- Interpret strings as packed binary data
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, cnt)
    data = struct.pack("d", time.time())
    # Calculate the checksum on the data and the dummy header.
    myChecksum = checksum(header + data)

    # Get the right checksum, and put in the header
    if sys.platform == 'darwin':
        myChecksum = htons(myChecksum) & 0xffff
        #Convert 16-bit integers from host to network byte order.
    else:
        myChecksum = htons(myChecksum)

    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, cnt)
    packet = header + data
    #print(packet) #prints binary string

    mySocket.sendto(packet,
                    (destAddr, 1))  # AF_INET address must be tuple, not str
    #Both LISTS and TUPLES consist of a number of objects
    #which can be referenced by their position number within the object


def doOnePing(destAddr, timeout, cnt):
    icmp = getprotobyname("icmp")
    #SOCK_RAW is a powerful socket type. For more details see: http://sock-raw.org/papers/sock_raw

    #Fill in start

    #Create Socket here
    mySocket = socket(AF_INET, SOCK_RAW, icmp)

    #Fill in end

    myID = os.getpid() & 0xFFFF  #Return the current process i
    sendOnePing(mySocket, destAddr, myID, cnt)
    delay = receiveOnePing(mySocket, myID, timeout, destAddr)

    mySocket.close()
    return delay
    #return "check"


def ping(host, timeout=1):
    global rtt_min, rtt_max, rtt_sum, rtt_cnt
    rtt_min = float('+inf')
    rtt_max = float('-inf')
    rtt_sum = 0
    rtt_cnt = 0
    cnt = 0
    #timeout=1 means: If one second goes by without a reply from the server,
    #the client assumes that either the client's ping or the server's pong is lost
    dest = gethostbyname(host)
    print("Pinging " + dest + " using Python:")
    #Send ping requests to a server separated by approximately one second
    try:
        while True:
            cnt += 1
            print(doOnePing(dest, timeout, cnt))
            time.sleep(1)
    except KeyboardInterrupt:
        if cnt != 0:
            print('--- {} ping statistics ---'.format(host))
            print(
                '{} packets transmitted, {} packets received, {:.1f}% packet loss'
                .format(cnt, rtt_cnt, 100.0 - rtt_cnt * 100.0 / cnt))
            if rtt_cnt != 0:
                print('round-trip min/avg/max {:.3f}/{:.3f}/{:.3f} ms'.format(
                    rtt_min, rtt_sum / rtt_cnt, rtt_max))


ping(sys.argv[1])