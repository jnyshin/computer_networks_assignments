from socket import *

serverPort = 1124
#make server's socket and listen for client's request
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(("", serverPort))
serverSocket.listen(1)
print("The server is ready to receive")
while True:
    #when request from client comes, accept and save it to new socket.
    connectionSocket, addr = serverSocket.accept()
    #decode the request and find the file embedded in header
    request = connectionSocket.recv(1024).decode()
    header = request.split('\n')
    file1 = header[0].split()[1][1:]
    response = ""
    #if file exists in the same directiry, then response is status 200 with the file content
    try:
        fd = open(file1, "r")
        found = fd.read()
        fd.close()
        response = 'HTTP/1.0 200 OK\n\n' + found
    #if the file doesn't exist, the response is status 404
    except FileNotFoundError:
        response = 'HTTP/1.0 404 NOT FOUND\n\n'
    #send response after file search
    connectionSocket.send(response.encode())
    #close the socket, which is made for this connection only.
    connectionSocket.close()