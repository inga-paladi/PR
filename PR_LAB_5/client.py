import socket
import threading
import json
import base64
from os.path import exists
import os

# Server configuration
HOST = '127.0.0.1' # Server's IP address
PORT = 12345       # Server's port
CLIENT_MEDIA_FOLDER = "client_media"

if not exists(CLIENT_MEDIA_FOLDER):
    os.mkdir(CLIENT_MEDIA_FOLDER)

# Create a socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)10

def connectToRoom(roomName, userName):
    # Connect to the server
    request = {}
    payload = {}
    request["type"] = "connect"
    payload["name"] = userName
    payload["room"] = roomName
    request["payload"] = payload
    
    client_socket.connect((HOST, PORT))
    client_socket.send(json.dumps(request).encode())

    response = client_socket.recv(1024).decode()
    try:
        return json.loads(response)["type"] == "connect_ack"
    except Exception as e:
        print(e)
        return False

room = input("Enter room: ")
name = input("Enter name: ")

if connectToRoom(room, name):
    print(f"Connected to {HOST}:{PORT}, room {room}")
else:
    print(f"Error connecting")
    exit(0)

def receive_messages():
    while True:
        data = client_socket.recv(1024)
        if not data:
            break # Exit the loop when the server disconnects

        try:
            parsedMessage = json.loads(data.decode())
            treatServerMessages(parsedMessage)
        except Exception as e:
            print(e)

def treatServerMessages(message):
    if message["type"] == "notification":
        print(f"Received: {message['payload']['message']}")
    elif message["type"] == "download_file_ack":
        treatMessageDownload(message)

def treatMessageDownload(message):
    success = False
    try:
        message["payload"]
        success = True
    except:
        pass

    if not success:
        print(f"Received: File: {message['error']['file_name']}, Server message: {message['error']['message']}")
        return
    
    downloadPath = f"{CLIENT_MEDIA_FOLDER}/{message['payload']['file_name']}"
    with open(downloadPath, "bw") as outFile:
        outFile.write(base64.b64decode(message["payload"]["file_data"]))
        print(f"Received: file {message['payload']['file_name']} downloaded in {downloadPath}")

def sendMessage(userInput):
    message = {
        "type": "message",
        "payload": {
            "text": userInput
        }
    }
    client_socket.send(json.dumps(message).encode())

def main():
    # Start the message reception thread
    receive_thread = threading.Thread(target=receive_messages)
    receive_thread.daemon = True # Thread will exit when the main program exits
    receive_thread.start()

    while True:
        userInput = input("Enter a message (or 'exit' to quit): ")

        if userInput.lower() == 'exit':
            break
        elif len(userInput) == 0:
            continue

        treatUserInput(userInput)


def treatUserInput(userInput):
    try:
        if userInput.startswith("upload:"):
            filePath = userInput.split("upload:")[1]
            uploadFileToServer(filePath)
        elif userInput.startswith("download:"):
            fileName = userInput.split("download:")[1]
            downloadFileFromServer(fileName)
        else:
            sendMessage(userInput)
    except Exception as e:
        print(e)

def uploadFileToServer(filePath):
    if not exists(filePath):
        print(f"File {filePath} does not exist.")
        return

    try:
        with open(filePath, 'br') as file:
            fileData = file.read()
            request = {
                "type": "upload_file",
                "payload": {
                    "file_name": filePath.split('/')[-1],
                    "file_data": base64.b64encode(fileData).decode("ascii")
                }
            }
            client_socket.send(json.dumps(request).encode())
    except:
        print(f"File {filePath} could not be uploaded.")

def downloadFileFromServer(fileName):
    request = {
        "type": "download_file",
        "payload": {
            "file_name": fileName
        }
    }
    client_socket.send(json.dumps(request).encode())

if __name__ == "__main__":
    main()