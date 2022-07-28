import threading
import socket
import os
import sys
import json


EdgeServerList = []
EdgeServerCount = 0


class AppendEdge(threading.Thread):
    """
    Append Edge class
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
                print("Edge " + str(self.mIp) + " has disconnected")
                self.mSignal = False
                EdgeServerList.remove(self)
                break

            if data != "":
                print("[Master]" + str(self.mId) + ": " + str(data.decode("utf-8")))
                print(EdgeServerCount)

                for edge in EdgeServerList:
                    edge.mSocket.sendall(str.encode("\n[Master]" + str(self.mId) + "/" + str(data.decode("utf-8") + "\n")))


class MasterServer:
    """
    MasterServer in distributed server model
    """
    def __init__(self, ip, port):
        """
        Initialize MasterServer
        """
        self.mIp = ip
        self.mPort = port


    def SetEdgeCount(self):
        with open("./Settings/config.json", "w") as f:
            json.dump({"EdgeCount": EdgeServerCount}, f)

    
    def StartServer(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind((self.mIp, self.mPort))
            sock.listen(5)

            receiveThread = threading.Thread(target=self.MakeConnections, args=(sock, ))
            receiveThread.start()

            self.SetEdgeCount()

        except:
            print("Cannot run the server")
            sys.exit(0)


    def MakeConnections(self, socket):
        while True:
            global EdgeServerCount

            sock, address = socket.accept()
            EdgeServerList.append(AppendEdge(sock, address, EdgeServerCount, "Name", True))
            EdgeServerList[len(EdgeServerList) - 1].start()

            print("New connection ID " + str(EdgeServerList[len(EdgeServerList) - 1]))
            EdgeServerCount += 1


if __name__ == "__main__":
    master = MasterServer("127.0.0.1", 5578)
    master.StartServer()