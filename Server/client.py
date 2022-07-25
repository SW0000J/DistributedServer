import threading
import socket
import os
import sys

from data import Receive


class Client:
    """
    Client in distributed server model
    """
    def __init__(self, ip, port):
        """
        Initialize client
        """
        self.mIp = ip
        self.mPort = port

    
    def StartClient(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.mIp, self.mPort))

            receiveThread = threading.Thread(target=Receive, args=(sock, True))
            receiveThread.start()

            while True:
                message = input()
                sock.sendall(str.encode(message))

        except:
            print("Cannot connect to the edgeserver")
            sys.exit(0)