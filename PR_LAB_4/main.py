from web_server import WebServer
import constants

if __name__ == "__main__":
    server = WebServer(constants.WEB_SERVER_HOST, constants.WEB_SERVER_LISTEN_PORT)
    try:
        print("Press CTRL+C to stop the server")
        server.run()
    except KeyboardInterrupt:
        server.shutdown()