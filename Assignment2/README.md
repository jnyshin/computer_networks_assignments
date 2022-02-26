#### Assignment 2
This assignment was to analyze a pcap file, especially for TCP entries. The ```dpkt``` library was used to disassemble the entries.<br>
There are two classes(objects) I made, <b>Packet</b> and <b>Flow</b>. Using these two classes helped a lot, since there were thousands of pcap entries. It may take some time to convert all pcap packets to Packet and Flow object, but the variables were very easy to reach after the process.

1. class <b>Packet</b>

- contains all specifications about one TCP packet.
- windowScaleFactor was used to display as the window size in WireShark. It is mentioned in the option section of TCP packet only some times, when window size is huge while the same scale factor is applied everytime. Therefore I have set the variable windowScaleFactor for convenienve.

2. class <b>Flow</b>

- contains necessary fields to organize tcp packets into flows. Since the packtets are considered as group of same flow if they move between same source port and destination port.
- packets filed is used to contain this flow's packets in order.
- ackDict is used for calculating retransmissions from triple duplicate ACK later. This dictionary holds {ACK : frequency}.
- portDict is used to calculate packet loss rate. A flow has only 2 ports regardless of they are source port or destination port.

3. matchFlow

- this method orgamizeds Packets to Flows based on their source port and destination port. Since sender can initiate run multiple flows at the same time, there were individual flows althouhgh some ports can overlap.

4. matchTransaction

- this method mathces pairs of packets in the same flow, by order. In other words, a packet that sender sent and a packet that sender received is one pair, transaction. The assignment asked to analyze only first 2 transactions after connection setup, thus for loop starts from index 2.
- system looks for a packet that has pivot packet's source port as its destination port, and pivot packet's destination port and its source port. Thus opposite. After 2 pairs of transactions are collected, the method terminates.

5. callThroughput

- calculates throuput of each flow.
- total data sent in a flow / total time took for the flow
- Packet object's length field returns the size of TCP packet in integer number of bytes.
- A flow might now take 1 second to handle the data sent in the flow. In this case, I took microsecond of the difference in time value, and converted it to seconds by multiplying 0.000001. Then the result is in unit Mbps

6. PrintInfo

- for each flow, this method prints out its source port, source IP, destination port, and destination IP first. Then SEQ, ACK, and window size follows.
- only 4 packets are analyzed because they are the first 2 transactions of each flow.

7. calLossRate

- this method uses portDict field in Flow class.
- if there was no loss, then the difference between occurance of two ports should be 0. If not, the difference is the number of lost packet.

8. congestionWindow

- calculates first 3 congestion window size for each flow.
- since this is not specified in TCP packet, the length of TCP packet's data were used.
- found RTT taking the difference of timestamp of first packet(when it starts) and thrid packet(when it arrives back) in the flow. Then the data sent during the RTT period can be measured by adding bytes that sent from packets which timestamp falls into [start, end] interval. (Note: end - start = RTT)
- if a packet's timestamp is pass end, then start variable takes previous end and new end is set up to packets[index].ts + RTT. Index variable is used to keep track.

9. retransmissionTriple

- ackDict field from Flow class is used.
- check how many duplicate ACK were sent more than 3 times, and print out the number

10. retransmissionTimeout

- at first, I wanted to see whether there are duplicate SEQs in a flow. seqDict was made to test this, and turned out that there were many of them due to package loss or timeout. So I supposed the SEQ was went due to timeout and used 2 RTT for the timeout value.
- going through packets in a flow
- need to check whether the packet's source IP is same as the senders since sender will resend the same SEQ, not from receiver.
- if the SEQ is not present in seqDict, add new entry with the SEQ and the packet's timestamp.
- if the SEQ exists, then compare with the packet's timestamp and the timestamp stored in dictionary. If the difference is more than 2 RTT, then consider this packet was resending SEQ due to timeout.
- print out the total number of timeout.
