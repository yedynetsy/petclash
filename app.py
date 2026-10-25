from flask import Flask, render_template, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

import os
import uuid
import random

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pets.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'dev-key'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    hash = db.Column(db.String(255), nullable=False)

    pets = db.relationship('Pet', backref='owner', lazy=True)

class Pet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image_path = db.Column(db.String(255), nullable=False)
    elo_rating = db.Column(db.Integer, default=1200)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


with app.app_context():
    db.create_all()


@app.route("/")
def index():
    all_pets = Pet.query.all()

    if len(all_pets) < 2:
        return render_template("index.html", pet1=None, pet2=None)

    pet1, pet2 = random.sample(all_pets, 2)

    return render_template("index.html", pet1=pet1, pet2=pet2)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username:
            flash("Please enter your username")
            return redirect("/register")
        elif not password:
            flash("Please enter your password")
            return redirect("/register")
        elif password != confirmation:
            flash("Passwords do not match")
            return redirect("/register")

        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            flash("User with that name already exists")
            return redirect("/register")

        hashed_password = generate_password_hash(password)

        new_user = User(username=username, hash=hashed_password)

        db.session.add(new_user)
        db.session.commit()

        session["user_id"] = new_user.id

        flash("Registration was successful")
        return redirect("/")

    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    session.pop("user_id", None)

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            flash("Please provide both username and password")
            return redirect("/login")

        user = User.query.filter_by(username=username).first()

        if user is None:
            flash("Invalid username")
            return redirect("/login")
        elif not check_password_hash(user.hash, password):
            flash("Invalid password")
            return redirect("/login")

        session["user_id"] = user.id
        flash("Logged in successfully")
        return redirect("/")

    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out")
    return redirect("/")


@app.route("/add_image", methods=["GET", "POST"])
def add_image():
    if session.get("user_id") is None:
        flash("You must be logged in to add a pet")
        return redirect("/login")

    if request.method == "POST":
        pet_name = request.form.get("name")
        pet_image = request.files.get("image")

        if not pet_name:
            flash("Please provide a name for your pet")
            return redirect("/add_image")

        if not pet_image or pet_image.filename == '':
            flash("Please upload an image")
            return redirect("/add_image")

        if pet_image:
            _, extension = os.path.splitext(pet_image.filename)
            unique_filename = str(uuid.uuid4()) + extension

            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            pet_image.save(filepath)

            new_pet = Pet(name=pet_name, image_path=filepath, user_id=session["user_id"])
            db.session.add(new_pet)
            db.session.commit()

            flash(f"Successfully added {pet_name}")
            return redirect("/add_image")

    else:
        return render_template("add_image.html")


@app.route("/vote", methods=["POST"])
def vote():
    winner_id = request.form.get("winner_id")
    loser_id = request.form.get("loser_id")

    if not winner_id or not loser_id:
        flash("Invalid vote")
        return redirect("/")

    winner = Pet.query.get(winner_id)
    loser = Pet.query.get(loser_id)

    if winner and loser:
        k = 32

        expected_winner = 1 / (1 + 10 ** ((loser.elo_rating - winner.elo_rating) / 400))
        expected_loser = 1 / (1 + 10 ** ((winner.elo_rating - loser.elo_rating) / 400))

        winner.elo_rating = winner.elo_rating + k * (1 - expected_winner)
        loser.elo_rating = loser.elo_rating + k * (0 - expected_loser)

        db.session.commit()

    return redirect("/")


@app.route("/leaderboard")
def leaderboard():
    lim = 20
    top_pets = Pet.query.order_by(Pet.elo_rating.desc()).limit(lim).all()

    return render_template("leaderboard.html", pets=top_pets)


if __name__ == "__main__":
    app.run(debug=True)

