import socket
import json
from bs4 import BeautifulSoup

host = "127.0.0.1"
port = 8080

simplePagesToProcess = (
    "index",
    "about",
    "contacts"
)

productsPage = "products"

def main():
    for simplePage in simplePagesToProcess:
        processSimplePage(simplePage)
    processProductsPage()

def getHttpResponseBody(httpResponse: str) -> str:
    bodyStart = httpResponse.find("\r\n\r\n")
    if bodyStart == -1:
        return None
    bodyStart += 4
    return httpResponse[bodyStart:]

def processSimplePage(page: str):
    pageResult = getPage("/" + page)
    pageBody = getHttpResponseBody(pageResult)
    if (pageBody != None):
        with open(page + ".html", "w") as file:
            file.write(pageBody)

def processProductsPage():
    pageResult = getPage("/products")
    beautySoup = BeautifulSoup(pageResult, 'html.parser')
    aTags = beautySoup.find_all('a')
    products = []
    for aTag in aTags:
        productPage = aTag.get('href')
        products.append(processProductPage(productPage))

    with open("retrieved_products.json", "w") as file:
        file.write(json.dumps(products))

def processProductPage(page: str):
    productPage = getPage(page)
    beautySoup = BeautifulSoup(productPage, 'html.parser')

    product = {}
    product["product_name"] = beautySoup.find(id="product_name").text
    product["product_author"] = beautySoup.find(id="product_author").text
    product["product_price"] = beautySoup.find(id="product_price").text
    product["product_description"] = beautySoup.find(id="product_description").text

    return product

def getPage(page: str) -> str:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    request = f"GET {page} HTTP/1.1\r\n\r\n"
    client_socket.send(request.encode())
    response = client_socket.recv(4096).decode()
    client_socket.close()
    return response

if __name__ == "__main__":
    main()