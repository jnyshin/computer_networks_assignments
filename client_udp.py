from socket import *

#from pip._vendor.distlib.compat import raw_input

serverName = "localhost"
serverPort = 12000
clientSocket = socket(AF_INET, SOCK_DGRAM)

msg = input("Enter lowercase sentence:")
print(msg)

clientSocket.sendto(msg.encode(), (serverName, serverPort))

modifiedMessage, serverAddress = clientSocket.recvfrom(2048)

print(modifiedMessage.decode())
clientSocket.close()
