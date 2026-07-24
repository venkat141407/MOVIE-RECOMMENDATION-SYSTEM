from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    jsonify
)

from werkzeug.security import generate_password_hash, check_password_hash

from recommender import recommend, autocomplete
from database import db, User, Favorite, Watchlist
import config

app = Flask(__name__)

# ---------------- CONFIG ---------------- #

app.config["SECRET_KEY"] = config.SECRET_KEY
app.config["SQLALCHEMY_DATABASE_URI"] = config.SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = config.SQLALCHEMY_TRACK_MODIFICATIONS

db.init_app(app)

with app.app_context():
    db.create_all()


# ---------------- HOME ---------------- #

@app.route("/")
def home():
    return render_template("index.html")


# ---------------- REGISTER ---------------- #

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        existing_user = User.query.filter(
            (User.email == email) |
            (User.username == username)
        ).first()

        if existing_user:
            flash("Username or Email already exists!")
            return redirect(url_for("register"))

        new_user = User(
            username=username,
            email=email,
            password=generate_password_hash(password)
        )

        db.session.add(new_user)
        db.session.commit()

        flash("Registration Successful!")
        return redirect(url_for("login"))

    return render_template("register.html")


# ---------------- LOGIN ---------------- #

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):

            session["user_id"] = user.id
            session["username"] = user.username

            flash("Login Successful!")
            return redirect(url_for("dashboard"))

        flash("Invalid Email or Password")

    return render_template("login.html")


# ---------------- DASHBOARD ---------------- #

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template(
        "dashboard.html",
        username=session["username"]
    )


# ---------------- RECOMMEND ---------------- #

@app.route("/recommend", methods=["GET", "POST"])
def recommend_page():

    if "user_id" not in session:
        return redirect(url_for("login"))

    recommendations = []

    if request.method == "POST":

        movie = request.form["movie"].strip()

        recommendations = recommend(movie)

    return render_template(
        "movie.html",
        recommendations=recommendations
    )


# ---------------- AUTOCOMPLETE API ---------------- #

@app.route("/autocomplete")
def autocomplete_api():

    if "user_id" not in session:
        return jsonify([])

    query = request.args.get("q", "").strip()

    if len(query) < 1:
        return jsonify([])

    suggestions = autocomplete(query)

    return jsonify(suggestions)


# ================= FAVORITES ================= #

@app.route("/add_favorite/<path:title>")
def add_favorite(title):

    if "user_id" not in session:
        return redirect(url_for("login"))

    exists = Favorite.query.filter_by(
        user_id=session["user_id"],
        movie_title=title
    ).first()

    if not exists:

        fav = Favorite(
            user_id=session["user_id"],
            movie_title=title
        )

        db.session.add(fav)
        db.session.commit()

        flash("Movie added to Favorites ❤️")

    return redirect(url_for("favorites"))


@app.route("/favorites")
def favorites():

    if "user_id" not in session:
        return redirect(url_for("login"))

    favorites = Favorite.query.filter_by(
        user_id=session["user_id"]
    ).all()

    return render_template(
        "favorites.html",
        favorites=favorites
    )


@app.route("/remove_favorite/<int:id>")
def remove_favorite(id):

    movie = Favorite.query.get_or_404(id)

    db.session.delete(movie)
    db.session.commit()

    flash("Favorite removed.")

    return redirect(url_for("favorites"))


# ================= WATCHLIST ================= #

@app.route("/add_watchlist/<path:title>")
def add_watchlist(title):

    if "user_id" not in session:
        return redirect(url_for("login"))

    exists = Watchlist.query.filter_by(
        user_id=session["user_id"],
        movie_title=title
    ).first()

    if not exists:

        movie = Watchlist(
            user_id=session["user_id"],
            movie_title=title
        )

        db.session.add(movie)
        db.session.commit()

        flash("Movie added to Watchlist 📺")

    return redirect(url_for("watchlist"))


@app.route("/watchlist")
def watchlist():

    if "user_id" not in session:
        return redirect(url_for("login"))

    movies = Watchlist.query.filter_by(
        user_id=session["user_id"]
    ).all()

    return render_template(
        "watchlist.html",
        watchlist=movies
    )


@app.route("/remove_watchlist/<int:id>")
def remove_watchlist(id):

    movie = Watchlist.query.get_or_404(id)

    db.session.delete(movie)
    db.session.commit()

    flash("Movie removed from Watchlist.")

    return redirect(url_for("watchlist"))


# ---------------- LOGOUT ---------------- #

@app.route("/logout")
def logout():

    session.clear()

    flash("Logged out successfully.")

    return redirect(url_for("login"))


# ---------------- RUN ---------------- #

if __name__ == "__main__":
    app.run(debug=True)