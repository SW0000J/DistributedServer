import threading
import socket
import os
import sys


def Receive(socket, signal):
    while signal:
        try:
            data = socket.recv(1024)
            print(str(data.decode("utf-8")))

        except:
            print("Disconnected from server")
            signal = False
            break