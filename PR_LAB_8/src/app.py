import flask
from models.database import db
from models.electro_scooter import ElectroScooter
from flask_swagger_ui import get_swaggerui_blueprint
import sys
from RaftFactory import RaftFactory

# Swagger consts
SWAGGER_URL = "/swagger"
SWAGGER_CONFIG = "/static/swagger.json"

def readPostgressPassword():
    with open("../secrets/postgres_passwd", "r") as file:
        return file.read()

if __name__ != "__main__":
    exit(0)

apiPort = None
dbPort = None
try:
    apiPort = int(sys.argv[1])
    dbPort = int(sys.argv[2])
    # apiPort = 5001
    # dbPort = 5401
    # apiPort = input("API port: ")
    # dbPort = input("Database port: ")
except:
    print("Please, input the api server and database server ports")
    exit(1)

app = flask.Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://postgres:{readPostgressPassword()}@localhost:{dbPort}/postgres'
db.init_app(app)

# init db
with app.app_context():
    db.create_all()

swagger_ui_blueprint = get_swaggerui_blueprint(SWAGGER_URL, SWAGGER_CONFIG)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

raftFactory = RaftFactory(apiPort)
raftFactory.Elect()

import controllers.routes

app.run(port=apiPort)
raftFactory.Stop()