from socket import *

proxyPort = 1124
#make a socket for proxy-side, and listen client's request
proxySocket = socket(AF_INET, SOCK_STREAM)
proxySocket.bind(("", proxyPort))
proxySocket.listen(1)
cacheDB = {}
print("The server is ready to receive")
while True:
    #when client request comes in, accept and save it to another socket.
    clientSocket, client_addr = proxySocket.accept()
    request = clientSocket.recv(1024).decode()
    header = request.split('\n')
    #from request's header extract domain and files
    url = header[0].split()[1]
    splitURL = url.split("/")[1]
    #search cacheDB if same request was handled before. if yes, then return the value as response.
    if splitURL in cacheDB:
        clientSocket.send(cacheDB[splitURL])
        print(cacheDB)
    #if this request was not handled before, then handle it here.
    else:
        server_addr = gethostbyname(splitURL)
        #make a socket so connect to the webserver that client requested.
        serverSocket = socket(AF_INET, SOCK_STREAM)
        serverSocket.connect((server_addr, 80))
        #write a header with Host = client's requested webserver.
        #we cannot send the request from client directly to web server because Host = proxy's IP address in that request.
        #thus, a new header to correctly direct to the web server is necessary.
        seg = "GET / HTTP/1.1\r\nHost: {}\r\n\r\n".format(splitURL)
        serverSocket.send(bytes(seg, 'utf-8'))
        while True:
            #get the response from web server, and send back to client
            response = serverSocket.recv(4096)
            cacheDB[splitURL] = response
            clientSocket.send(response)
            break
        #close sockets
        serverSocket.close()
    clientSocket.close()
