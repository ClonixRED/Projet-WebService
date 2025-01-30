from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

# Filtrage des trains disponibles
@app.route('/search_trains', methods=['GET'])
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


if __name__ == '__main__':
    app.run(port=5001, debug=True)
