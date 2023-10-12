import socket
import threading
import json
import select
import base64
import os
import random

# client
# {
#   "socket": socket,
#   "name": str,
#   "id": int{5}
# }

# Server configuration
HOST = '127.0.0.1' # Loopback address for localhost
PORT = 12345 # Port to listen on
SERVER_MEDIA_FOLDER = "media"

if not os.path.exists(SERVER_MEDIA_FOLDER):
    os.mkdir(SERVER_MEDIA_FOLDER)

# Create a socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the specified address and port
try:
    server_socket.bind((HOST, PORT))
except Exception as e:
    print(e)
    exit(1)

# Listen for incoming connections
server_socket.listen()

print(f"Server is listening on {HOST}:{PORT}")

rooms = {}

def handle_client(client):
    print(f"{client['name']} entered room {client['room']}")

    while True:
        data = client["socket"].recv(1024)
        if not data:
            break

        try:
            request = data.decode()
            print(f"Client Request: {request}")
            treatClientRequest(client, json.loads(request));
        except Exception as e:
            print(e)

    # Remove the client from the list
    removeClient(client)

def treatClientRequest(client, request):
    if request["type"] == "message":
        sendMessageToRoom(client, request["payload"]["text"])
    elif request["type"] == "upload_file":
        uploadFile(client, request["payload"]["file_name"], request["payload"]["file_data"])
    elif request["type"] == "download_file":
        downloadFile(client, request["payload"]["file_name"])

def sendMessageToRoom(client, message):
    response = {
        "type": "notification",
        "payload": {
           "message": message,
           "sender_name": client["name"]
        }
    }

    for roomClient in rooms[client["room"]]:
        if roomClient != client:
            roomClient["socket"].send(json.dumps(response).encode())

def uploadFile(client, fileName, fileData):
    updatedFileName = f"{client['id']}_{fileName}"
    fullFilePath = f"{SERVER_MEDIA_FOLDER}/{client['room']}/{updatedFileName}"
    with open(fullFilePath, 'bw') as outFile:
        outFile.write(base64.b64decode(fileData))

    sendMessageToRoom(client, f"File {updatedFileName} uploaded in chat by {client['name']}")

def downloadFile(client, fileName):
    try:
        with open(f"{SERVER_MEDIA_FOLDER}/{client['room']}/{fileName}", 'br') as inFile:
            response = {
                "type": "download_file_ack",
                "payload": {
                    "file_name": fileName,
                    "file_data": base64.b64encode(inFile.read()).decode('ascii')
                }
            }
            client["socket"].send(json.dumps(response).encode())
    except Exception as e:
        print(e)
        response = {
            "type": "download_file_ack",
            "error": {
                "file_name": fileName,
                "message": "Error downloading the requested file."
            }
        }
        client["socket"].send(json.dumps(response).encode())

def acceptClient():
    while True:
        client_socket, client_address = server_socket.accept()
        print("CLient came")
        client_socket.setblocking(False)

        ready = select.select([client_socket], [], [], 2) # 2s timeout
        if not ready[0]:
            print("client not connected")
            client_socket.close()
            continue

        request = client_socket.recv(1024).decode()
        print(f"request: {request}")
        parsedRequest = ""
        try:
            parsedRequest = json.loads(request)
            print(f"parsed request: {parsedRequest}")
            if parsedRequest["type"] != "connect":
                continue

            client = {}
            client["name"] = parsedRequest["payload"]["name"]
            client["room"] = parsedRequest["payload"]["room"]
            client["address"] = client_address
            client["socket"] = client_socket
            sendConnAck(client_socket)
            client["socket"].setblocking(True)
            return client
        except Exception as e:
            print(e)
            client_socket.close()
            continue

def sendConnAck(client_socket):
    response = {}
    payload = {}
    response["type"] = "connect_ack"
    payload["message"] = "Connected to the room"
    response["payload"] = payload
    print(f"send response: {response}")
    client_socket.send(json.dumps(response).encode())

def addClientToRoom(room, client):
    client["id"] = generateUniqueClientId()
    try:
        rooms[room].append(client)
    except:
        rooms[room] = [client]
        roomFolder = f"{SERVER_MEDIA_FOLDER}/{room}"
        if not os.path.exists(roomFolder):
            os.makedirs(roomFolder)

def removeClient(client):
    client["socket"].close()
    room = client["room"]

    roomPath = f"{SERVER_MEDIA_FOLDER}/{room}"
    for filename in os.listdir(roomPath):
        if filename.startswith(str(client["id"])):
            os.remove(os.path.join(roomPath, filename))

    rooms[room].remove(client)
    if len(rooms[room]) == 0:
        del rooms[room]
        os.rmdir(roomPath)

def getClientById(id: int):
    for _, clients in rooms:
        for client in clients:
            if client["id"] == id:
                return client
            
    return None

def generateUniqueClientId():
    while True:
        randomNumber = random.randint(100, 99999)
        if getClientById(randomNumber) == None:
            return randomNumber

def main():
    while True:
        try:
            client = acceptClient()
            print("client accepted")
            addClientToRoom(client["room"], client)

            # Start a thread to handle the client
            client_thread = threading.Thread(target=handle_client, args=(client,))
            client_thread.start()
        except KeyboardInterrupt:
            server_socket.close()
            break

if __name__ == "__main__":
    main()