from flask import Flask, request, jsonify
from spyne import Application, rpc, ServiceBase, Integer, Unicode, String
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
import sqlite3
import threading
from wsgiref.simple_server import make_server
from flasgger import Swagger
import requests

# Application Flask pour l'API REST
app = Flask(__name__)


import logging  #ligne de débug
logging.basicConfig(level=logging.DEBUG)  #ligne de débug



Swagger(app)  # Ajoute la documentation OpenAPI pour le service REST (Critère 8)

# Configuration de la base de données (Critère 6)
# Cette fonction initialise la base de données SQLite pour stocker les informations des trains.
def init_db():
    conn = sqlite3.connect('trains.db')
    cursor = conn.cursor()

    # Création de la table des trains
    cursor.execute('''CREATE TABLE IF NOT EXISTS trains (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        departure TEXT,
                        arrival TEXT,
                        date TEXT,
                        time TEXT,
                        available_seats INTEGER,
                        class TEXT,
                        UNIQUE(departure, arrival, date, time, class)  -- Évite les doublons
                    )''')

    # Insertion des trains uniquement s'ils n'existent pas déjà
    trains_data = [
        ('Paris', 'Lyon', '2025-02-01', '08:00', 50, 'Première Classe'),
        ('Paris', 'Lyon', '2025-02-01', '10:00', 30, 'Deuxième Classe'),
        ('Marseille', 'Nice', '2025-02-02', '12:00', 20, 'Première Classe'),
        ('Marseille', 'Nice', '2025-02-02', '15:00', 40, 'Deuxième Classe'),
        ('Bordeaux', 'Toulouse', '2025-02-03', '09:30', 25, 'Première Classe'),
        ('Bordeaux', 'Toulouse', '2025-02-03', '14:00', 35, 'Deuxième Classe'),
        ('Lille', 'Strasbourg', '2025-02-04', '07:00', 15, 'Première Classe'),
        ('Lille', 'Strasbourg', '2025-02-04', '13:00', 45, 'Deuxième Classe'),
        ('Nantes', 'Rennes', '2025-02-05', '08:15', 30, 'Première Classe'),
        ('Nantes', 'Rennes', '2025-02-05', '17:45', 50, 'Deuxième Classe')
    ]

    for train in trains_data:
        try:
            cursor.execute('INSERT INTO trains (departure, arrival, date, time, available_seats, class) VALUES (?, ?, ?, ?, ?, ?)', train)
        except sqlite3.IntegrityError:
            pass  # Ignore l'insertion si le train existe déjà

    conn.commit()
    conn.close()

init_db()  # Appelle l'initialisation de la base


@app.route('/all_trains', methods=['GET'])
def all_trains():
    """Renvoie la liste de tous les trains disponibles."""
    conn = sqlite3.connect('trains.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM trains")
    trains = cursor.fetchall()
    conn.close()

    if trains:
        return jsonify(trains)
    else:
        return jsonify({"error": "Aucun train disponible."}), 404


# Point de terminaison REST pour la recherche de trains (Critère 1)
@app.route('/search_trains', methods=['GET'])
def search_trains():
    """Recherche de trains disponibles"""
    logging.debug(f"Requête reçue : {request.url}")

    # Récupération des paramètres
    departure = request.args.get('departure')
    arrival = request.args.get('arrival')
    travel_class = request.args.get('class')

    if not departure or not arrival or not travel_class:
        return jsonify({"error": "Tous les paramètres (departure, arrival, class) sont requis."}), 400

    print("🔍 DEBUG :")
    print(f"🔹 Départ : {departure}")
    print(f"🔹 Arrivée : {arrival}")
    print(f"🔹 Classe : {travel_class}")

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

# Service SOAP pour la réservation de trains (Critère 2)
class TrainBookingService(ServiceBase):
    @rpc(Integer, String, String, _returns=String)  # Ajout de ticket_type
    def book_train(ctx, train_id, travel_class, ticket_type):
        print(f"Réservation demandée - Train ID: {train_id}, Classe: {travel_class}, Ticket: {ticket_type}")

        rest_url = "http://localhost:5001/update_train"
        response = requests.post(rest_url, json={"train_id": train_id, "class": travel_class, "ticket_type": ticket_type})

        if response.status_code == 200 and response.json().get("success"):
            return "Réservation réussie"
        else:
            return f"Erreur de réservation : {response.json().get('error', 'Train non disponible')}"



# Configuration du service SOAP (Critère 3)
soap_app = Application([TrainBookingService], 'TrainBookingService',
                       in_protocol=Soap11(validator='lxml'),
                       out_protocol=Soap11())
soap_server = WsgiApplication(soap_app)

# Exécution des services dans des threads séparés (Critère 4 & 7)
# Exécute l'API REST Flask sur le#ligne de débug port 5000
def run_flask():
    app.run(port=5000)

# Exécute le service SOAP sur le port 8000
def run_soap():
    print("Démarrage du serveur SOAP sur http://127.0.0.1:8000/")
    server = make_server('0.0.0.0', 8000, soap_server)
    server.serve_forever()

# Démarrage des deux services dans des threads séparés (Critère 3 & 5)
if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    threading.Thread(target=run_soap).start()
