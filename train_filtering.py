from flask import Flask, request, jsonify
import sqlite3
from flasgger import Swagger, swag_from


app = Flask(__name__)
Swagger(app) 
# Filtrage des trains disponibles
@app.route('/search_trains', methods=['GET'])
@swag_from({
    "parameters": [
        {"name": "departure", "in": "query", "type": "string", "required": True, "description": "Ville de départ"},
        {"name": "arrival", "in": "query", "type": "string", "required": True, "description": "Ville d'arrivée"},
        {"name": "class", "in": "query", "type": "string", "required": True, "description": "Classe du voyage"}
    ],
    "responses": {
        200: {
            "description": "Liste des trains disponibles",
            "schema": {
                "type": "array",
                "items": {
                    "properties": {
                        "id": {"type": "integer"},
                        "departure": {"type": "string"},
                        "arrival": {"type": "string"},
                        "date": {"type": "string"},
                        "time": {"type": "string"},
                        "available_seats": {"type": "integer"},
                        "class": {"type": "string"}
                    }
                }
            }
        },
        404: {"description": "Aucun train disponible"}
    }
})

def search_trains():
    departure = request.args.get('departure')
    arrival = request.args.get('arrival')
    travel_class = request.args.get('class')

    if not departure or not arrival or not travel_class:
        return jsonify({"error": "Tous les paramètres (departure, arrival, class) sont requis."}), 400

    conn = sqlite3.connect('trains.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM trains WHERE departure=? AND arrival=? AND class=?", 
                   (departure, arrival, travel_class))
    trains = cursor.fetchall()
    conn.close()

    if trains:
        return jsonify(trains)
    else:
        return jsonify({"error": "Aucun train disponible."}), 404

# Met à jour la disponibilité des trains après une réservation
@app.route('/update_train', methods=['POST'])
@swag_from({
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "properties": {
                    "train_id": {"type": "integer", "example": 123},
                    "class": {"type": "string", "example": "Première Classe"},
                    "ticket_type": {"type": "string", "example": "flexible"}
                }
            }
        }
    ],
    "responses": {
        200: {"description": "Réservation réussie", "schema": {"success": {"type": "boolean"}}},
        400: {"description": "Erreur de réservation", "schema": {"error": {"type": "string"}}}
    }
})
def update_train():
    data = request.get_json()
    train_id = data.get('train_id')
    travel_class = data.get('class')
    ticket_type = data.get('ticket_type')  # Ajout du type de billet

    if not train_id or not travel_class or not ticket_type:
        return jsonify({"error": "train_id, class et ticket_type sont requis."}), 400

    conn = sqlite3.connect('trains.db')
    cursor = conn.cursor()

    cursor.execute("SELECT available_seats FROM trains WHERE id=? AND class=?", 
                   (train_id, travel_class))
    result = cursor.fetchone()

    if result and result[0] > 0:
        cursor.execute("UPDATE trains SET available_seats=available_seats-1 WHERE id=? AND class=?", 
                       (train_id, travel_class))
        
        conn.commit()
        conn.close()
        return jsonify({"success": True})
    else:
        conn.close()
        return jsonify({"success": False, "error": "Train complet ou ID invalide."}), 400


# Exécute l'API REST Flask sur le#ligne de débug port 5001
def run_flask():
    app.run(port=5001)

if __name__ == '__main__':
    app.run(port=5001, debug=True)


