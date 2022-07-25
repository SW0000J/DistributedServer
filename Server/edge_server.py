import threading
import socket
import os
import sys

from data import Receive


ClientList = []
ClientCount = 0


class AppendClient(threading.Thread):
    """
    Append Client class
    """
    def __init__(self, socket, ip, id, name, signal):
        threading.Thread.__init__(self)
        self.mSocket = socket
        self.mIp = ip
        self.mId = id
        self.mName = name
        self.mSignal = signal

    
    def __str__(self):
        return str(self.mId) + " " + str(self.mIp)

    
    def run(self):
        while self.mSignal:
            try:
                data = self.mSocket.recv(1024)
            
            except:
                print("Client " + str(self.mIp) + " has disconnected")
                self.mSignal = False
                ClientList.remove(self)
                break

            if data != "":
                print("ID " + str(self.mId) + ": " + str(data.decode("utf-8")))

                for client in ClientList:
                    if client.mId != self.mId:
                        client.mSocket.sendall(str.encode("\nID " + str(self.mId) + ": " + str(data.decode("utf-8") + "\n")))

    
class EdgeServer:
    """
    Edge in distributed server model
    """
    def __init__(self, masterIp, masterPort, clientIp, clientPort):
        """
        Initialize Edge Server
        """
        self.mMasterIp = masterIp
        self.mMasterPort = masterPort
        self.mClientIp = clientIp
        self.mClientPort = clientPort

        
    def StartServer(self):
        """
        Make Socket between edge <-> client
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind((self.mClientIp, self.mClientPort))
            sock.listen(5)

            receiveThread = threading.Thread(target=self.MakeConnections, args=(sock, ))
            receiveThread.start()

        except:
            print("Cannot run the server")
            sys.exit(0)


    def MakeConnections(self, socket):
        """
        Make connection between edge <-> client
        """
        while True:
            global ClientCount

            sock, address = socket.accept()
            ClientList.append(AppendClient(sock, address, ClientCount, "Name", True))
            ClientList[len(ClientList) - 1].start()

            print("New connection ID " + str(ClientList[len(ClientList) - 1]))
            ClientCount += 1


    def StartClient(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.mMasterIp, self.mMasterPort))

            receiveThread = threading.Thread(target=Receive, args=(sock, True))
            receiveThread.start()

            while True:
                message = input()
                sock.sendall(str.encode(message))

        except:
            print("Cannot connect to the masterserver")
            sys.exit(0)