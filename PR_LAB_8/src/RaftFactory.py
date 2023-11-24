import json
import socket
import threading

UDP_BUFFER_SIZE = 1024

class RaftFactory:
    class ServiceType:
        Unspecified = 0
        Leader = 1
        Follower = 2

    def __init__(self, tcpPort):
        self._udpSocket = None
        self._currentServiceType = self.ServiceType.Unspecified
        self._followerAccepterThread = None
        self._followers = None
        self._address = "localhost"
        self._tcpPort = tcpPort
        self._exiting = False
        self._leaderCreds = None
        self._token = self._GenerateToken()

    def HaveWritePermissions(self, token = None) -> bool:
        if self._currentServiceType is self.ServiceType.Leader:
            return True
        
        if token is not None and "token" in list(self._leaderCreds.keys()) and token == self._leaderCreds["token"]:
            return True
        
        return False

    def GetToken(self):
        return self._token
    
    def GetFollowers(self):
        if self._followers is not None:
            return self._followers
        else:
            return []

    def IsLeader(self) -> bool:
        return self._currentServiceType == self.ServiceType.Leader

    def _GenerateToken(self) -> str:
        return "superToken"

    def _ReadSettings(self):
        with open("configs.json", "r") as settings:
            return json.loads(settings.read())

    def _GetServiceInfo(self):
        return {"address": self._address, "port": self._tcpPort}

    def _GetUdpPort(self):
        try:
            return self._ReadSettings()["udp-port"]
        except:
            print("Error reading udp port from settings")
            return None

    def Elect(self):
        port = self._GetUdpPort()
        if port is None:
            return
        
        self._udpSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        try:
            self._udpSocket.bind((self._address, port))
            print("Binding successful. I'm the leader")
            self._currentServiceType = self.ServiceType.Leader
            self._followerAccepterThread = threading.Thread(target=self._AcceptFollowers).start()
        except Exception as e:
            print(f"Erorr binding to port: {e}. I'm the follower")
            self._BindToLeader()

    def _BindToLeader(self):
        port = self._GetUdpPort()
        if port is None:
            return
        
        self._udpSocket.sendto("Accept".encode(), ("127.0.0.1", port))
        receivedMessage, _ = self._udpSocket.recvfrom(UDP_BUFFER_SIZE)
        self._leaderCreds = json.loads(receivedMessage.decode())
        print(f"Received credentials from the leader. {self._leaderCreds['address']}:{self._leaderCreds['port']} and token {self._leaderCreds['token']}")
        self._udpSocket.sendto(json.dumps(self._GetServiceInfo()).encode(), (self._address, port))

    def _AcceptFollowers(self):
        while True:
            receivedMessage, receiverAddress = self._udpSocket.recvfrom(UDP_BUFFER_SIZE)
            if receivedMessage.decode() == "Accept":
                serviceInfo = self._GetServiceInfo()
                serviceInfo["token"] = self._token
                serviceInfoStr = json.dumps(serviceInfo).encode()
                self._udpSocket.sendto(serviceInfoStr, receiverAddress)
            else: # This should be some follower credentials
                try:
                    self._AddFollower(json.loads(receivedMessage.decode()))
                except:
                    pass

    def _AddFollower(self, creds):
        if isinstance(self._followers, list):
            self._followers.append(creds)
        else:
            self._followers = [creds]
        print(f"Follower {creds['address']}:{creds['port']} accepted")

    def Stop(self):
        self._exiting = True
        self._udpSocket.close()
        if self._followerAccepterThread is not None:
            self._followerAccepterThread.join()