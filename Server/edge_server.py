import threading
import socket
import os
import sys
import json

from data import Receive


ClientList = []
ClientCount = 0


class AppendClient(threading.Thread):
    """
    Append Client class
    """
    def __init__(self, socket, ip, master_socket, id, name, signal):
        threading.Thread.__init__(self)
        self.mSocket = socket
        self.mIp = ip
        self.mMasterSocket = master_socket
        self.mId = id
        self.mName = name
        self.mSignal = signal

    
    def __str__(self):
        return str(self.mId) + " " + str(self.mIp)

    
    def run(self):
        while self.mSignal:
            try:
                data = self.mSocket.recv(1024)
                self.mMasterSocket.sendall(data)

                sync_data = self.mMasterSocket.recv(1024)
            
            except:
                print("Client " + str(self.mIp) + " has disconnected")
                self.mSignal = False
                ClientList.remove(self)
                break

            if sync_data != "":
                print("[Edge]" + str(self.mId) + ": " + str(sync_data.decode("utf-8")))
                print(ClientCount)

                for client in ClientList:
                    client.mSocket.sendall(str.encode("\n[Edge]" + str(self.mId) + ": " + str(sync_data.decode("utf-8") + "\n")))

    
class EdgeServer:
    """
    Edge in distributed server model
    """
    def __init__(self, masterIp, masterPort, clientIp):
        """
        Initialize Edge Server
        """
        edge_count = self.GetEdgeCount() + 1

        self.mMasterIp = masterIp
        self.mMasterPort = masterPort
        self.mClientIp = clientIp
        self.mClientPort = masterPort + edge_count

        self.SetEdgeCount(edge_count)
        print(self.mClientPort)


    def GetEdgeCount(self):
        with open("./Settings/config.json", "r") as f:
            edge_count = json.load(f)

        return edge_count["EdgeCount"]

    
    def SetEdgeCount(self, edge_count):
        with open("./Settings/config.json", "w") as f:
            json.dump({"EdgeCount": edge_count}, f)

        
    def StartServer(self):
        """
        Make Socket between edge <-> client
        """
        try:
            sock_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock_client.bind((self.mClientIp, self.mClientPort))
            sock_client.listen(5)

            sock_master = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock_master.connect((self.mMasterIp, self.mMasterPort))

            connectThread = threading.Thread(target=self.MakeConnections, args=(sock_client, sock_master,))
            connectThread.start()

        except:
            print("Cannot run the server")
            sys.exit(0)
            '''
            print("Cannot connect to the masterserver")
            sys.exit(0)
            '''


    def MakeConnections(self, client_socket, master_socket):
        """
        Make connection between edge <-> client
        """
        while True:
            global ClientCount

            sock, address = client_socket.accept()
            ClientList.append(AppendClient(sock, address, master_socket, ClientCount, "Name", True))
            ClientList[len(ClientList) - 1].start()

            print("New connection ID " + str(ClientList[len(ClientList) - 1]))
            ClientCount += 1


if __name__ == "__main__":
    edge = EdgeServer("127.0.0.1", 5578, "127.0.0.1")
    edge.StartServer()