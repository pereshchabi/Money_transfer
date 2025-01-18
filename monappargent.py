from waitress import serve
from flask import Flask, render_template, redirect, url_for, request
import json
from flask_socketio import SocketIO

# Initialisation de l'application Flask
app = Flask(__name__)

# Initialiser SocketIO avec l'application Flask (bien que vous n'en aurez plus besoin ici)
socketio = SocketIO(app)

# Chemin vers le fichier JSON qui stocke les utilisateurs
USERS_FILE = "users.json"

# Fonction pour charger les utilisateurs depuis un fichier JSON
def load_users():
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Fonction pour sauvegarder les utilisateurs dans le fichier JSON
def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

# Charger les utilisateurs existants depuis le fichier
users = load_users()

# Ajouter un compte administrateur par défaut si non présent
if "admin" not in users:
    users["admin"] = "securepassword123"
    save_users(users)

# Dictionnaire pour suivre les utilisateurs connectés
logged_in_users = {}

# Liste pour stocker les transactions en attente
pending_transactions = []

# Liste pour stocker les transactions validées
validated_transactions = []

# Route pour la page d'accueil
@app.route('/')
def home():
    return render_template('home.html', logged_in=bool(logged_in_users))

# Route pour la connexion des utilisateurs
@app.route('/login', methods=['GET', 'POST'])
def login():
    global logged_in_users
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in users and users[username] == password:
            logged_in_users[username] = True

            if username == "admin":
                return redirect(url_for('admin_dashboard'))

            return redirect(url_for('transfers'))

        return render_template('login.html', error="Nom d'utilisateur ou mot de passe incorrect")

    return render_template('login.html')

# Route pour initier un transfert
@app.route('/transfers', methods=['GET', 'POST'])
def transfers():
    if request.method == 'POST':
        sender_network = request.form['sender_network']
        receiver_network = request.form['receiver_network']
        transaction_number = request.form['transaction_number']
        receiver_name = request.form['receiver_name']
        receiver_number = request.form['receiver_number']

        transaction = {
            'transaction_id': len(pending_transactions) + 1,
            'sender_network': sender_network,
            'receiver_network': receiver_network,
            'transaction_number': transaction_number,
            'receiver_name': receiver_name,
            'receiver_number': receiver_number,
            'status': ' ',
        }

        pending_transactions.append(transaction)

        return render_template('waiting.html', transaction=transaction)

    return render_template('transfers.html', logged_in=bool(logged_in_users))

# Route pour le tableau de bord de l'administrateur
@app.route('/admin')
def admin_dashboard():
    if "admin" not in logged_in_users or not logged_in_users["admin"]:
        return redirect(url_for('login'))

    return render_template(
        'admin_dashboard.html',
        pending_transactions=pending_transactions,
        validated_transactions=validated_transactions,
        no_pending_transactions=(len(pending_transactions) == 0),
        no_validated_transactions=(len(validated_transactions) == 0)
    )

# Route pour valider une transaction
@app.route('/validate_transfer/<int:transaction_id>', methods=['POST'])
def validate_transfer(transaction_id):
    if "admin" not in logged_in_users or not logged_in_users["admin"]:
        return redirect(url_for('login'))

    transaction = next((t for t in pending_transactions if t['transaction_id'] == transaction_id), None)
    if transaction is None:
        return redirect(url_for('admin_dashboard'))

    # Mettre à jour le statut de la transaction
    transaction['status'] = 'Prise en compte'

    # Ajouter la transaction validée à la liste des transactions validées
    validated_transactions.append(transaction)

    # Supprimer la transaction de la liste des transactions en attente
    pending_transactions.remove(transaction)

    return redirect(url_for('admin_dashboard'))

# Route pour rejeter une transaction
@app.route('/reject_transfer/<int:transaction_id>', methods=['POST'])
def reject_transfer(transaction_id):
    if "admin" not in logged_in_users or not logged_in_users["admin"]:
        return redirect(url_for('login'))

    transaction = next((t for t in pending_transactions if t['transaction_id'] == transaction_id), None)
    if transaction is None:
        return redirect(url_for('admin_dashboard'))

    transaction['status'] = 'Non prise en compte'

    return redirect(url_for('admin_dashboard'))
@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    feedback = request.form['feedback']
    # Vous pouvez ici sauvegarder le feedback dans la base de données ou dans un fichier
    print("Avis reçu:", feedback)  # Affiche le feedback dans la console
    # Après avoir sauvegardé l'avis, vous pouvez rediriger vers une autre page, par exemple la page d'accueil
    return redirect(url_for('home'))

# Route pour la déconnexion
@app.route('/logout')
def logout():
    global logged_in_users
    logged_in_users = {}
    return redirect(url_for('home'))

# Démarrer le serveur Flask
if __name__ == '__main__':
    app.run(debug=True)
    socketio.run(app, debug=True)
    serve(app, host='0.0.0.0', port=8000)
