from flask import Flask
from routes import main
import db_manager
import os

app = Flask(__name__)

# Configurazione Secret Key (Necessaria per gestire le sessioni utente e l'ordinamento cumulativo)
app.secret_key = 'chiave_segreta_super_sicura_fantacale'

# Registrazione del Blueprint (le rotte definite in routes.py)
app.register_blueprint(main)

def setup_app():
    """Verifica l'esistenza del DB e importa i dati se necessario"""
    if not os.path.exists(db_manager.DATABASE_NAME):
        print("Database non trovato. Inizializzazione in corso...")
        db_manager.init_db()
        
        # Verifica se esiste il file sorgente dati
        if os.path.exists('db.csv'):
            print("File dati trovato. Importazione...")
            db_manager.import_from_csv('db.csv')
        else:
            print("ATTENZIONE: File 'db.csv' non trovato. Il DB è vuoto.")
    else:
        print("Database esistente rilevato.")

if __name__ == '__main__':
    setup_app()
    # Debug=True permette il ricaricamento automatico al cambio codice
    app.run(debug=True, port=5000)