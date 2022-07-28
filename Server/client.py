import threading
import socket
import os
import sys
import json
import random

from data import Receive


class Client:
    """
    Client in distributed server model
    """
    def __init__(self, ip, port):
        """
        Initialize client
        """
        rand_port = self.SetRandomPort()

        self.mIp = ip
        self.mPort = rand_port


    def SetRandomPort(self):
        with open("./Settings/config.json", "r") as f:
            edge_count = json.load(f)

        edge_count = edge_count["EdgeCount"]

        return random.randrange(5579, 5579 + edge_count)

    
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


if __name__ == "__main__":
    cli = Client("127.0.0.1", 5579)
    cli.StartClient()