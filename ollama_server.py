#!/usr/bin/env python3

import ollama
from socket import *

class UDPCtrl():
    def __init__(
        self, 
        myIP       = "127.0.0.1", 
        myPort     = 3014,
        recIP       = "127.0.0.1",
        recPort     = 3014,
        buff        = 1024,
        clNum        = 1
    ):

        self.myAddr     = (myIP, myPort)                    # アドレスをtupleに格納
        self.recAddr    = (recIP,recPort)                   # アドレスをtupleに格納
        self.udpsock    = socket(AF_INET, SOCK_DGRAM)       # ソケット作成
        
        self.BUFSIZE = buff
        if clNum > 0:
            self.udpsock.bind(self.myAddr)
    
    def __enter__(self):
        return self

    def send(self, data):
        self.udpsock.sendto(data, self.recAddr)     # 宛先アドレスに送信
    
    def recv(self):
        data, addr = self.udpsock.recvfrom(self.BUFSIZE)# 受信
        return data, addr
    
    def __exit__(self, *args):
        self.udpsock.close()

class TCPCtrl():
    def __init__(
        self, 
        myIP        = "127.0.0.1", 
        myPort      = 3014,
        recIP       = "127.0.0.1",
        recPort     = 3014,
        buff        = 4096,
        timeout     = 5, 
        clNum       = 1
    ):
        self.myAddr     = (myIP, myPort)                    # アドレスをtupleに格納
        self.recAddr    = (recIP,recPort)                   # アドレスをtupleに格納
        self.BUFSIZE    = buff
        self.tcpsock    = socket(AF_INET, SOCK_STREAM)
        if clNum > 0:
            self.tcpsock.bind(self.myAddr)
            self.tcpsock.listen(clNum)
            self.tcpsock.settimeout(timeout)

        else:
            self.tcpsock.connect(self.recAddr)
    
    def __enter__(self):
        return self
    
    def accept(self):
        try:
            client_socket, client_address = self.tcpsock.accept()
            return client_socket, client_address
        
        except:
            return None, None
    
    def send(self, data, sock = None, encoding = "UTF-8"):
        if sock is None:
            sock = self.tcpsock
        if data is None:
            data = ""
        try:
            data = data.encode(encoding)
        except:
            pass
        finally:
            sock.send(data)

    def recv(self, sock = None, encoding = "UTF-8"):
        if sock is None:
            sock = self.tcpsock
        data = sock.recv(self.BUFSIZE)
        try:
            data = data.decode(encoding)
        except:
            pass
        finally:
            #print(data)
            return data
    
    def __exit__(self, *args):
        self.tcpsock.close()

def ollama_request(message, model = "llama3"):
    response = ollama.chat(
        model = model, 
        messages=[
            {
                "role": "user",
                "content": f"{message}",
            },
        ]
    )
    return response["message"]["content"]

if __name__ == "__main__":
    with TCPCtrl(
        myIP        = "192.168.10.66", 
        myPort      = 3014,
        recIP       = "127.0.0.1",
        recPort     = 4000,
        buff        = 4096,
        timeout     = 5, 
        clNum       = 1
    ) as protocol:
        csock, caddr = protocol.accept()
        while True:
            try:
                d = protocol.recv(csock)
                msg = ollama_request(d)
                print(msg)
                protocol.send(msg, csock)
            except:
                break