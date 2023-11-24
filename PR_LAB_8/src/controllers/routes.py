import flask
import requests
from models.database import db
from models.electro_scooter import ElectroScooter
from __main__ import app, raftFactory

@app.before_request
def before_request():
    if flask.request.method == "GET":
        return

    global raftFactory
    if raftFactory.IsLeader():
        print("Received a write request. I'm the leader. I'll forward this to the followers")
        forward_request_to_followers(flask.request)
    else:
        leaderToken = flask.request.headers.get("Leader-Token")
        print(f"Received write request to a follower. Leader token is {leaderToken}")
        if not raftFactory.HaveWritePermissions(leaderToken):
            flask.abort(403)

def forward_request_to_followers(original_request):
    global raftFactory
    headers = dict(original_request.headers)
    headers["Leader-Token"] = raftFactory.GetToken()

    for follower in raftFactory.GetFollowers():
        forward_url = f'http://{follower["address"]}:{follower["port"]}{original_request.path}'
        print("Forward call to "+forward_url)
        
        try:
            requests.request(
                method=original_request.method,
                url=forward_url,
                headers=headers,
                data=original_request.get_data(),
                cookies=original_request.cookies,
                allow_redirects=False
            )
        except Exception as e:
            print(f"Error forwarding request to {follower['address']}:{follower['port']}: {e}")

@app.route('/api/electro-scooters', methods=['GET'])
def get_electro_scooters():
    scooters = ElectroScooter.query.all()

    if scooters is None:
        return flask.jsonify({"error": "No scooters found"}), 404

    scooter_list = []
    for scooter in scooters:
        scooter_list.append({
            "id": scooter.id,
            "name": scooter.name,
            "battery_level": scooter.battery_level
        })
    return flask.jsonify(scooter_list), 200

@app.route('/api/electro-scooters/<int:scooter_id>', methods=['GET'])
def get_electro_scooter_by_id(scooter_id):
    scooter = ElectroScooter.query.get(scooter_id)
        
    if scooter is None:
        return flask.jsonify({"error": "Electro scooter not found"}), 404
        
    return flask.jsonify({
        "id": scooter.id,
        "name": scooter.name,
        "battery_level": scooter.battery_level
    }), 200
        
@app.route('/api/electro-scooters', methods=['POST'])
def create_electro_scooter():
    try:
        data = flask.request.get_json()

        name = data['name']
        battery_level = data['battery_level']

        electro_scooter = ElectroScooter(name=name, battery_level=battery_level)

        db.session.add(electro_scooter)
        db.session.commit()
        
        return flask.jsonify({"message": "Electro Scooter created successfully"}), 201
    except KeyError:
        return flask.jsonify({"error": "Invalid request data"}), 400

@app.route('/api/electro-scooters/<int:scooter_id>', methods=['PUT'])
def update_electro_scooter(scooter_id):
    try:
        # Find the Electro Scooter by ID
        scooter = ElectroScooter.query.get(scooter_id)

        if scooter is not None:
        # Get data from the request body
            data = flask.request.get_json()

            # Update the Electro Scooter properties
            scooter.name = data.get('name', scooter.name)
            scooter.battery_level = data.get('battery_level', scooter.battery_level)

            db.session.commit()

            return flask.jsonify({"message": "Electro Scooter updated successfully"}), 200
        else:
            return flask.jsonify({"error": "Electro Scooter not found"}), 404
    except Exception as e:
        return flask.jsonify({"error": str(e)}), 500

@app.route('/api/electro-scooters/<int:scooter_id>', methods=['DELETE'])
def delete_electro_scooter(scooter_id):
    try:
        # Find the Electro Scooter by ID
        scooter = ElectroScooter.query.get(scooter_id)

        if scooter is None:
            return flask.jsonify({"error": "Electro Scooter not found"}), 40425

        # Get the password from the request headers
        password = flask.request.headers.get('X-Delete-Password')

        # Check if the provided password is correct
        if password != 'your_secret_password':
            return flask.jsonify({"error": "Incorrect password"}), 401

        db.session.delete(scooter)
        db.session.commit()
        return flask.jsonify({"message": "Electro Scooter deleted successfully"}), 200
    except Exception as e:
        return flask.jsonify({"error": str(e)}), 500