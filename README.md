# 📌 Projet WebService

## 🚀 Introduction
Cette API permet la recherche et la réservation de billets de train en utilisant :
- **REST (Flask)** pour la recherche de trains.
- **SOAP (Spyne)** pour la réservation de billets.
- **SQLite** comme base de données pour stocker les informations des trains.

## 📌 1. Installation des dépendances

### 🔹 1️⃣ Créer un environnement virtuel
Dans le terminal :
```bash
python3 -m venv envwebservice
```

### 🔹 2️⃣ Activer l'environnement virtuel
- **Linux/macOS :**
```bash
source envwebservice/bin/activate
```


### 🔹 3️⃣ Installer les dépendances
Avec l'environnement activé, dans le terminal:
```bash
pip install flask spyne flasgger lxml requests zeep
```

---

## 📌 2. Démarrer le serveur
Dans le terminal :
```bash
lsof -i :8000
kill -9 pid
python webservice.py
```
✅ **Si tout fonctionne, les logs doivent afficher :**
```
 * Running on http://127.0.0.1:5000/ (REST API)
 * SOAP Server running on http://127.0.0.1:8000/
```

📌 **Ne pas fermer le terminal !** Ouvrir un **nouveau terminal** pour les tests.

---

## 📌 3. Tester l'API REST (`search_trains`)
### 🔹 Désactiver le proxy 
Dans le **nouveau terminal** :
```bash
export http_proxy=""
export https_proxy=""
```

### 🔹 Faire une requête REST pour rechercher un train
```bash
curl -G --data-urlencode "departure=Paris" --data-urlencode "arrival=Lyon" --data-urlencode "class=Première Classe" "http://localhost:5000/search_trains"
```
✅ **Résultat attendu (si un train est disponible) :**
```json
[[1,"Paris","Lyon","2025-02-01","08:00",50,"Première Classe"]]
```
❌ **Si aucun train n’est disponible :**
```json
{"error": "Aucun train disponible."}
```

---

## 📌 4. Tester l'API SOAP (`book_train`)
### 🔹 Vérifier que le WSDL est disponible
Ouvre un navigateur et accède à :
```
http://localhost:8000/?wsdl
```
✅ **Si tout fonctionne il y aura un fichier XML avec `<wsdl:definitions>`**

### 🔹 Réserver un billet avec `cURL`
```bash
curl -X POST -H "Content-Type: text/xml" --data '
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tns="TrainBookingService">
   <soapenv:Header/>
   <soapenv:Body>
      <tns:book_train>
         <tns:train_id>1</tns:train_id>
         <tns:travel_class>Première Classe</tns:travel_class>
      </tns:book_train>
   </soapenv:Body>
</soapenv:Envelope>' http://localhost:8000/
```
✅ **Réponse attendue si la réservation fonctionne :**
```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
   <soapenv:Body>
      <book_trainResponse>
         <book_trainResult>Réservation réussie</book_trainResult>
      </book_trainResponse>
   </soapenv:Body>
</soapenv:Envelope>
```

### 🔹 Vérifier que la base de données est mise à jour
```bash
sqlite3 trains.db
SELECT * FROM trains WHERE id=1;
```
✅ **Si tout fonctionne, `available_seats` doit avoir diminué.**

---

## 📌 5. Tester l'interaction entre REST et SOAP
### 🔹 1️⃣ Vérifier le nombre de places **avant** la réservation
```bash
curl -G --data-urlencode "departure=Paris" --data-urlencode "arrival=Lyon" --data-urlencode "class=Première Classe" "http://localhost:5000/search_trains"
```
📌 **Prendre le nombre de places (`available_seats`).**

### 🔹 2️⃣ Réserver un billet avec SOAP (voir commande plus haut).

### 🔹 3️⃣ Vérifier que le nombre de places a diminué avec REST
```bash
curl -G --data-urlencode "departure=Paris" --data-urlencode "arrival=Lyon" --data-urlencode "class=Première Classe" "http://localhost:5000/search_trains"
```
✅ **Si REST affiche normalement le nombre de places mis à jour**

---


## 🎯 **Conclusion : Projet Fonctionnel !**
✅ **Recherche de trains (REST) fonctionne**
✅ **Réservation de billets (SOAP) fonctionne**
✅ **Mise à jour en base de données vérifiée**
✅ **Interaction REST/SOAP validée**


---



