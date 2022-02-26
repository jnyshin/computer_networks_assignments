### Assignment 1
This assignment was to make a simple UDP server and a proxy server. 

The only library used for this assignment was python sockets.

#### How to run my programs:
<I>The port number {1124} was used for both programs.</I> <br>
<b>For webserver.py: </b>
1. Run webserver.py in your computer (cmd or terminal)
2. Put http://localhost:1124/HelloWorld.html in your browser's bar. 
Since ```HelloWorld.html``` is in the same directory as these files, there should be no problem. 

<b>For proxyserver.py:</b>
1. Run proxyserver.py in your computer (cmd or terminal)
2. Put http://localhost:1124/www.example.com in your browser's bar. 
   - I used ```example.com``` because this website is not content-heavy. ```google.com```  might fail this test. 
3. You can try with other websites such as ```stonybrook.edu``` or ```uber.com```
4. If this error ```[OSError: [Errno 48] Address already in use]``` comes up, wait few mintues and try with the same command.
