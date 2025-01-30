import requests
from zeep import Client

REST_API_URL = "http://localhost:5000/search_trains"
SOAP_WSDL_URL = "http://localhost:8000/?wsdl"
ALL_TRAINS_URL = "http://localhost:5000/all_trains"  

def list_all_trains():
    """Affiche tous les trains disponibles dans la base de données."""
    print("\n🔹 Récupération de tous les trains disponibles...\n")
    
    response = requests.get(ALL_TRAINS_URL)

    if response.status_code == 200:
        trains = response.json()
        if trains:
            print("✅ Liste de tous les trains disponibles :")
            for train in trains:
                train_id, dep, arr, date, time, seats, class_type = train
                print(f"🚆 ID: {train_id} | Départ: {dep} | Arrivée: {arr} | Date: {date} | Heure: {time} | Places: {seats} | Classe: {class_type}")
        else:
            print("❌ Aucun train disponible.")
    else:
        print("❌ Erreur lors de la récupération des trains :", response.text)

def search_trains():
    """Recherche les trains disponibles en demandant les informations à l'utilisateur."""
    departure = input("Entrez la gare de départ : ").strip()
    arrival = input("Entrez la gare d'arrivée : ").strip()
    date = input("Entrez la date du voyage (YYYY-MM-DD) : ").strip()
    travel_class = input("Entrez la classe de voyage (Première Classe, Deuxième Classe) : ").strip()

    params = {
        "departure": departure,
        "arrival": arrival,
        "class": travel_class
    }

    print("\n🔹 Recherche des trains en cours...\n")
    
    response = requests.get(REST_API_URL, params=params)

    if response.status_code == 200:
        trains = response.json()
        if trains:
            print("✅ Trains disponibles :")
            for train in trains:
                train_id, dep, arr, train_date, time, seats, class_type = train
                if train_date == date:  # Filtrage par date
                    print(f"🚆 Train ID: {train_id} | Départ: {dep} | Arrivée: {arr} | Date: {train_date} | Heure: {time} | Places disponibles: {seats} | Classe: {class_type}")
            return trains
        else:
            print("❌ Aucun train disponible à cette date.")
            return None
    else:
        print("❌ Erreur lors de la recherche de trains :", response.text)
        return None

def book_train():
    """Effectue la réservation d'un train via le service SOAP."""
    client = Client(wsdl=SOAP_WSDL_URL)

    try:
        train_id = int(input("\nEntrez l'ID du train à réserver : ").strip())
        travel_class = input("Entrez la classe de voyage (Première Classe, Deuxième Classe) : ").strip()
        ticket_type = input("Choisissez le type de billet (Flexible / Non Flexible) : ").strip()

        print("\n🔹 Réservation en cours...\n")
        response = client.service.book_train(train_id, travel_class, ticket_type)
        print(f"✅ Réponse du service SOAP : {response}")

    except Exception as e:
        print(f"❌ Erreur SOAP : {e}")



def main():
    print("=== 🚆 Bienvenue dans le système de réservation de trains ===\n")
    
    while True:
        print("\n1️⃣ Voir tous les trains disponibles")
        print("2️⃣ Rechercher un train")
        print("3️⃣ Réserver un train directement (si vous connaissez l'ID)")
        print("4️⃣ Quitter")

        choix = input("\n👉 Choisissez une option (1/2/3/4) : ").strip()

        if choix == "1":
            list_all_trains()
        elif choix == "2":
            trains = search_trains()
            if trains:
                sous_choix = input("\nVoulez-vous réserver un train ? (oui/non) : ").strip().lower()
                if sous_choix == "oui":
                    book_train()
        elif choix == "3":
            book_train()
        elif choix == "4":
            print("\n👋 Au revoir !")
            break  # Quitte la boucle et termine le programme
        else:
            print("❌ Choix invalide, veuillez réessayer.")

if __name__ == "__main__":
    main()
