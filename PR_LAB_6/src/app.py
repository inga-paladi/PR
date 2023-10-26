from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models.database import db

from models.electro_scooter import ElectroScooter

def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Jcxd32bpsvgFhkPf4BZMaKALuynqeQmY@localhost:5432/postgres'
    db.init_app(app)
    return app

if __name__ == "__main__":
    app = create_app()
    import controllers.routes
    app.run(debug=False)



