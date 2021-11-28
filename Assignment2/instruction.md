How to run this program:

1. If running in Visual Studio Code
   - open the uncompressed zip folder in VS Code
   - from the menu, go to Terminal -> New Terminal
   - run "python analysis_pcap_tcp.py" in the terminal
2. If running in PyCharm CE
   - open the uncompressed zip folder in VS Code
   - from the menu, Run -> Run -> select analysis_pcap_tcp.py

Please put the test pcap files in the same folder as analysis_pcap_tcp.py.
Change the name of file in line 176, f = open("assignment2.pcap", "rb").
For example, if you want to run "listsOfTCP.pcap" file, change line 176 as f = open("listsOfTCP.pcap", "rb").

- "rb" needs to be stay within the parentheses!!
