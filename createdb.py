from app import app, db  # Importa l'istanza di Flask 'app' e il database 'db'

# Crea il contesto dell'applicazione
with app.app_context():
    db.create_all()
    print("Database creato con successo!")
