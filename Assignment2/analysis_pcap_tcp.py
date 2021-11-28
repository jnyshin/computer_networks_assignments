# Yejin Shin, 111850347, yejin.shin@stonybrook.edu
# CSE 310 Programming Assignment 2

import datetime
import dpkt
import socket
from dpkt.ethernet import Ethernet

windowScaleFactor = 16384


class Packet:
    def __init__(self, ip, ts):
        tcp = ip.data
        self.tcp = tcp
        self.srcIP = socket.inet_ntop(socket.AF_INET, ip.src)
        self.dstIP = socket.inet_ntop(socket.AF_INET, ip.dst)
        self.srcPort = tcp.sport
        self.dstPort = tcp.dport
        self.ts = ts
        self.seq = tcp.seq
        self.ack = tcp.ack
        self.opts = dpkt.tcp.parse_opts(tcp.opts)
        self.win = tcp.win * windowScaleFactor
        self.length = len(tcp.data)


class Flow:
    def __init__(self, packet):
        self.srcPort = packet.srcPort
        self.dstPort = packet.dstPort
        self.packets = [packet]
        self.portDict = {self.srcPort: 1, self.dstPort: 1}
        self.ackDict = {packet.ack: 1}

    def __eq__(self, flow):
        return (self.srcPort == flow.srcPort and self.dstPort == flow.dstPort) or (
            self.srcPort == flow.dstPort and self.dstPort == flow.srcPort
        )


def matchFlow(packets):
    # organize tcp packets into flows
    flows = [Flow(packets[0])]
    for i in range(1, len(packets)):
        newFlow = Flow(packets[i])
        j = 0  # variable to check whether newFlow already exists in flows. If not, add newFlow to flows
        for flow in flows:
            if (
                newFlow == flow
            ):  # if newFlow is part of existing flow, add the packet to that flow's packets array
                flow.packets.append(packets[i])
                flow.portDict[packets[i].srcPort] += 1  # to check loss.
                if packets[i].ack in flow.ackDict:
                    flow.ackDict[packets[i].ack] += 1
                else:
                    flow.ackDict[packets[i].ack] = 1
                break
            j += 1
        if j == len(flows):
            flows.append(newFlow)
    return flows


def matchTransaction(packets):
    # organize transactions in flows
    # since very fist 2 transactions are for setting up connection, skip it and start from 3rd packet
    # unlike flow, a pair of transaction are unique
    # for this assignment, only first 2 transactions are needed. Thus return when length of transactions[] is 2
    transactions = []
    for i in range(2, 10):
        frontp_srcPort = packets[i].srcPort
        frontp_dstPort = packets[i].dstPort
        for j in range(i + 1, len(packets)):
            backp_srcPort = packets[j].srcPort
            backp_dstPort = packets[j].dstPort
            if frontp_srcPort == backp_dstPort and frontp_dstPort == backp_srcPort:
                transactions.append(packets[i])
                transactions.append(packets[j])
                break
        if len(transactions) == 4:
            return transactions
    return transactions


def calThroughput(packets):
    # calculate throughput for each flow
    # total data sent in a flow / total time took for the flow. Unit in Mbps
    payload = 0
    for p in packets:
        payload += p.length
    MbPayload = payload / 1000000
    endTime = datetime.datetime.utcfromtimestamp(packets[-1].ts)
    startTime = datetime.datetime.utcfromtimestamp(packets[0].ts)
    diff = endTime - startTime
    if diff.seconds > 0:
        return MbPayload / diff.seconds
    else:
        diff = diff.microseconds
        return MbPayload / (diff * 0.000001)


def printInfo(transaction, no):
    # print (source port, source IP, destination port, destination IP) for each flow
    # print seq, ack, and window size for first 2 transactions after connection set up
    print("\n----------Flow No.", no, "----------")
    for t in transaction:
        # print("Source Port: \t", t.srcPort, "Source IP: \t", t.srcIP, "Destination Port: \t", t.dstPort, "Destination IP: \t", t.dstIP)
        print(
            "Source Port: %d \t Source IP: %s\t Destination Port %d\t Destination IP %s\t"
            % (t.srcPort, t.srcIP, t.dstPort, t.dstIP)
        )
        print("SEQ: %d\t ACK: %d\t Window Size: %d\t\n" % (t.seq, t.ack, t.win))


def calLossRate(sent, received):
    diff = sent - received
    print("Packet Loss Rate: ", diff / sent)


def congestionWindow(packets):
    # suppose RTT is same for all pairs of transactions
    RTT = packets[2].ts - packets[0].ts
    # set start ~ end to RTT
    start = packets[3].ts
    end = packets[3].ts + RTT
    max = packets[-1].ts  # end cannot exceed the last packet's timestamp
    count = 1  # count for 3 cwnd
    index = 3  # for next round
    while end <= max:
        sum = 0
        for p in packets:
            if start <= p.ts <= end:
                sum += p.length
            elif p.ts > end:
                break
            index += 1
        print("%s st congestion window size (bytes): %d\n" % (count, sum))
        start = end  # now set start to previous end
        end = packets[index].ts + RTT  # keep ratio same
        count += 1
        if count > 3:  # after printing 3 cwnd, end this loop
            break


def retransmissionTriple(ackDict):
    # from matchFlow(), ackDict collected dictionary of {ACK : frequency}.
    # triple duplicate ACK occurs when there are 3 more duplicate ACKs.
    sum = 0
    for ack in ackDict:
        if ackDict[ack] > 2:  # meets the condition
            sum += 1
    print("Number of retransmissions due to triple duplicate ACK: ", sum)


def retransmissionTimeout(packets):
    # suppose there was retransmission from timeout if the timeout was longer than 2 RTT
    RTT = packets[2].ts - packets[0].ts
    seqDict = {}
    srcIP = packets[0].srcIP
    timeout = 0
    for p in packets:
        if p.srcIP == srcIP:  # only consider SEQ from sender
            if p.seq in seqDict:
                diff = p.ts - seqDict[p.seq]
                if diff > 2 * RTT:
                    timeout += 1
            else:
                seqDict[p.seq] = p.ts  # {SEQ : ts}
    print("Number of retransmissions due to timeout: ", timeout)


def main():
    global senderIP
    f = open("assignment2.pcap", "rb")
    pcap = dpkt.pcap.Reader(f)
    packetArray = []
    for ts, buf in pcap:
        eth = Ethernet(buf)
        ip = eth.data
        newp = Packet(ip, ts)
        packetArray.append(newp)  # convert pcap to Packets object
    no = 1  # number
    flowArray = matchFlow(packetArray)
    for flow in flowArray:
        transactions = matchTransaction(
            flow.packets
        )  # match pairs of transactions within the flow
        printInfo(transactions, no)  # print out informations
        throughput = calThroughput(flow.packets)  # calculate throughput of this flow
        print("throughput: ", throughput, "Mbps")
        calLossRate(
            flow.portDict[flow.srcPort], flow.portDict[flow.dstPort]
        )  # calculate packet loss rate of this flow
        congestionWindow(flow.packets)  # calculate and print first 3 cwnd
        retransmissionTriple(
            flow.ackDict
        )  # calculate retransmission from triple duplicate ACK in this flow
        retransmissionTimeout(
            flow.packets
        )  # calculate retransmission from timeout in this flow
        no += 1
    f.close()


main()
