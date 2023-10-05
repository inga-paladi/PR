import socket
import constants
import json

class WebServer():
    def __init__(self, address, port):
        self.address = address
        self.port = port
        self.listeningSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listeningSocket.bind((address, port))

    def run(self):
        print(f"Listening on {self.address}:{self.port}")
        self.listening = True
        self.listeningSocket.listen(5)
        self.processRequests()

    def shutdown(self):
        self.listening = False
        self.listeningSocket.close()

    def processRequests(self):
        while self.listening:
            clientSocket, _ = self.listeningSocket.accept()
            rawClientRequest = clientSocket.recv(1024).decode('utf-8')
            processedClientRequest = {}
            response = ""
            
            try:
                processedClientRequest = self.processHttpRequest(rawClientRequest)
            except:
                processedClientRequest["method"] = ""
            
            if processedClientRequest["method"] == "GET":
                response = self.processGetRequest(processedClientRequest["path"])
            else:
                response = self.respondMethodNotImplemented(clientSocket)
    
            clientSocket.send(response.encode('utf-8'))
            clientSocket.close()

    def processHttpRequest(self, rawData):
        processedRequest = {}
        
        requestLines = rawData.split('\r\n')
        firstLine = requestLines[0].strip().split()
        processedRequest["method"] = firstLine[0].upper()
        processedRequest["path"] = firstLine[1]
        
        return processedRequest

    def respondMethodNotImplemented(self, socket):
        return ""

    def processGetRequest(self, path):
        if path == '/' or path == '/index':
            return self.processPageIndex()
        elif path == '/about':
            return self.processPageAbout()
        elif path == '/contacts':
            return self.processPageContact()
        elif path == '/products':
            return self.processProducts()
        elif path.startswith('/product/'):
            return self.processProduct(path)
        else:
            return self.processPage404()

    def getHttpResponseHeader200(self):
        return "HTTP/1.1 200 OK"

    def getHttpHeader(self, name, value):
        return name + ": " + value

    def processPageIndex(self):
        response = self.getHttpResponseHeader200() + '\r\n'
        response += self.getHttpHeader("Content-type", "text/html") + '\r\n'
        response += "\r\n"
        response += self.readHtmlPage("index")
        return response

    def processPageAbout(self):
        response = self.getHttpResponseHeader200() + '\r\n'
        response += self.getHttpHeader("Content-type", "text/html") + '\r\n'
        response += "\r\n"
        response += self.readHtmlPage("about")
        return response

    def processPageContact(self):
        response = self.getHttpResponseHeader200() + '\r\n'
        response += self.getHttpHeader("Content-type", "text/html") + '\r\n'
        response += "\r\n"
        response += self.readHtmlPage("contact")
        return response

    def processProducts(self):
        response = self.getHttpResponseHeader200() + '\r\n'
        response += self.getHttpHeader("Content-type", "text") + '\r\n'
        response += "\r\n"

        body = ""
        products = self.readProductsData()
        for productId in range(0, len(products)):
            body += self.applyProductDataInHtml(products[productId]) + '\r\n'
            body += f"<a href=\"/product/{productId}\">/product/{productId}</a>\n"
        
        response += self.readHtmlPage("body").format(body = body)
        return response

    def processProduct(self, path):
        try:
            productId = int(path.split('/')[-1])
            productData = self.readProductsData()[productId]
            htmlResult = self.readHtmlPage("body").format(
                body = self.applyProductDataInHtml(productData)
            )
            response = self.getHttpResponseHeader200() + '\r\n'
            response += self.getHttpHeader("Content-type", "text/html") + '\r\n'
            response += "\r\n"
            response += htmlResult
            return response
        except:
            return self.processPage404()

    def processPage404(self):
        response = "HTTP/1.1 404 Not Found\r\n"
        response += "Content-type: text\r\n"
        response += "\r\n"
        response += "404: Not Found"
        return response
    
    def readHtmlPage(self, name):
        with open(name+".html", "r") as file:
            return file.read()
        
    def readProductsData(self):
        with open(constants.PRODUCTS_DATA_FILENAME, "r") as file:
            return json.load(file)

    def applyProductDataInHtml(self, productData):
        htmlBase = self.readHtmlPage("product")
        return htmlBase.format(
            product_name=productData["name"],
            product_author=productData["author"],
            product_price=productData["price"],
            product_description=productData["description"]
        )