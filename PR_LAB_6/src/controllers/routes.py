from flask import jsonify
from models.database import db
from models.electro_scooter import ElectroScooter
from __main__ import app

@app.route('/api/electro-scooters', methods=['GET'])
def get_electro_scooters():
    return jsonify({"message": "List of electro scooters"})

@app.route('/api/electro-scooters/<int:scooter_id>', methods=['GET'])
def get_electro_scooter_by_id(scooter_id):
    scooter = ElectroScooter.query.get(scooter_id)
        
    if scooter is not None:
        return jsonify({
            "id": scooter.id,
            "name": scooter.name,
            "battery_level": scooter.battery_level
        }), 200
    else:
        return jsonify({"error": "Electro scooter not found"}), 404
        
@app.route('/api/electro-scooter', methods=['POST'])
def create_electro_scooter():
    try:
        data = request.get_json()

        name = data['name']
        battery_level = data['battery_level']

        electro_scooter = ElectroScooter(name=name, battery_level=battery_level)

        db.session.add(electro_scooter)
        db.session.commit()
        
        return jsonify({"message": "Electro Scooter created successfully"}), 201
    except KeyError:
        return jsonify({"error": "Invalid request data"}), 400

@app.route('/api/electro-scooters/<int:scooter_id>', methods=['PUT'])
def update_electro_scooter(scooter_id):
    try:
        # Find the Electro Scooter by ID
        scooter = ElectroScooter.query.get(scooter_id)

        if scooter is not None:
        # Get data from the request body
            data = request.get_json()

            # Update the Electro Scooter properties
            scooter.name = data.get('name', scooter.name)
            scooter.battery_level = data.get('battery_level', scooter.battery_level)

            db.session.commit()

            return jsonify({"message": "Electro Scooter updated successfully"}), 200
        else:
            return jsonify({"error": "Electro Scooter not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/electro-scooters/<int:scooter_id>', methods=['DELETE'])
def delete_electro_scooter(scooter_id):
    try:
        # Find the Electro Scooter by ID
        scooter = ElectroScooter.query.get(scooter_id)

        if scooter is None:
            return jsonify({"error": "Electro Scooter not found"}), 40425

        # Get the password from the request headers
        password = request.headers.get('X-Delete-Password')

        # Check if the provided password is correct
        if password != 'your_secret_password':
            return jsonify({"error": "Incorrect password"}), 401

        db.session.delete(scooter)
        db.session.commit()
        return jsonify({"message": "Electro Scooter deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500