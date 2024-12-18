import argparse
from app import db, User, app


def add_user(username, password, role):
    """Aggiunge un utente al database."""
    with app.app_context():
        # Verifica se il ruolo è valido
        if role not in ["member", "operative"]:
            print(
                f"Errore: Il ruolo '{role}' non è valido. Usa 'member' o 'operative'."
            )
            return

        # Verifica se l'utente esiste già
        if User.query.filter_by(username=username).first():
            print(f"Errore: L'utente '{username}' esiste già!")
            return

        # Aggiunta dell'utente
        new_user = User(username=username, password=password, role=role)
        db.session.add(new_user)
        db.session.commit()
        print(f"Utente '{username}' con ruolo '{role}' aggiunto con successo!")


if __name__ == "__main__":
    # Parsing degli argomenti da riga di comando
    parser = argparse.ArgumentParser(
        description="Aggiungi un nuovo utente al database."
    )
    parser.add_argument("--username", required=True, help="Username dell'utente.")
    parser.add_argument("--password", required=True, help="Password dell'utente.")
    parser.add_argument(
        "--role",
        required=True,
        choices=["member", "operative"],
        help="Ruolo dell'utente: 'member' o 'operative'.",
    )

    args = parser.parse_args()

    # Chiamata della funzione add_user
    add_user(args.username, args.password, args.role)
