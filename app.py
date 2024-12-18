import os
from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    request,
    make_response,
    send_from_directory,
)
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user,
)

app = Flask(__name__)
app.config["SECRET_KEY"] = "supersecret"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["RESOURCES_FOLDER"] = "resources"  # Directory dove sono salvate le risorse
app.config["OPERATIVE_RESOURCES_FOLDER"] = (
    "operative_resources"  # Directory per risorse operative
)
os.makedirs(app.config["RESOURCES_FOLDER"], exist_ok=True)
os.makedirs(app.config["OPERATIVE_RESOURCES_FOLDER"], exist_ok=True)

db = SQLAlchemy(app)
login_manager = LoginManager(app)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    role = db.Column(db.String(50), default="member")  # Ruolo: 'member' o 'operative'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/")
def home():
    return render_template(
        "home.html",
        username=current_user.username if current_user.is_authenticated else None,
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            return redirect(url_for("dashboard"))
    response = make_response(render_template("login.html"))
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@app.route("/logout")
@login_required
def logout():
    logout_user()  # Effettua il logout dell'utente
    return redirect(url_for("home"))  # Reindirizza alla pagina di home


@app.route("/dashboard")
@login_required
def dashboard():
    # Elenco delle risorse nella directory RESOURCES_FOLDER
    resources = os.listdir(app.config["RESOURCES_FOLDER"])

    # Elenco delle risorse operative nella directory OPERATIVE_RESOURCES_FOLDER
    operative_resources = (
        os.listdir(app.config["OPERATIVE_RESOURCES_FOLDER"])
        if current_user.role == "operative"
        else []
    )

    return render_template(
        "dashboard.html",
        resources=resources,
        extra_resources=operative_resources,
        username=current_user.username,
    )


@app.route("/download/<folder>/<filename>")
@login_required
def download_file(folder, filename):
    if folder == "resources":
        directory = app.config["RESOURCES_FOLDER"]
    elif folder == "operative_resources" and current_user.role == "operative":
        directory = app.config["OPERATIVE_RESOURCES_FOLDER"]
    else:
        return redirect(url_for("dashboard"))

    return send_from_directory(directory, filename, as_attachment=True)


@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
