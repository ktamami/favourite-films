from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField
from wtforms.validators import URL, NumberRange
from dotenv import load_dotenv
import os


load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL1", "sqlite:///top10films.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
admin_pass = os.environ.get("ADMIN_PASS")
db = SQLAlchemy(app)
Bootstrap(app)

class Form(FlaskForm):
    title = StringField(label="title")
    year = StringField(label="year")
    description = StringField(label="description")
    rating = FloatField(label="rating", validators=[NumberRange(min=0.0, max=10.0)])
    review = StringField(label="review")
    img_url = StringField(label="img_url", validators=[URL()])
    submit = SubmitField("Submit")

class Film(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    year = db.Column(db.String(250), nullable=False)
    description = db.Column(db.String(250), nullable=False)
    rating = db.Column(db.Float(250), nullable=False)
    ranking = db.Column(db.Integer, nullable=False)
    review = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(1000), nullable=False)
db.create_all()


@app.route("/")
def home():
    all_films = db.session.query(Film).order_by(desc(Film.rating)).all()
    n=0
    for film in all_films:
        film.ranking = n + 1
        db.session.commit()
        n += 1
    return render_template("index.html", films=all_films)

@app.route("/add", methods=["GET", "POST"])
def add():
    form = Form()
    if request.method == "POST":
        add_title = request.form.get("title")
        add_year = request.form.get("year")
        add_img_url = request.form.get("img_url")
        add_ranking = 0
        add_rating = request.form.get("rating")
        add_description = request.form.get("description")
        add_review = request.form.get("review")
        new_film = Film(
            title=add_title,
            year=add_year,
            description=add_description,
            rating=add_rating,
            ranking=add_ranking,
            review=add_review,
            img_url=add_img_url
        )
        db.session.add(new_film)
        db.session.commit()
        all_films = db.session.query(Film).order_by(desc(Film.rating)).all()
        n = 0
        for film in all_films:
            film.ranking = n + 1
            db.session.commit()
            n += 1
        return render_template("index.html", films=all_films, admin=True)
    return render_template("add.html", form=form)

@app.route("/edit/<film_id>", methods=["GET", "POST"])
def edit(film_id):
    form = Form()
    if request.method == "POST":
        update = Film.query.filter_by(id=film_id).first()
        if request.form.get("title") != "":
            update.title = request.form.get("title")
            db.session.commit()
        if request.form.get("year") != "":
            update.year = request.form.get("year")
            db.session.commit()
        if request.form.get("description") != "":
            update.description = request.form.get("description")
            db.session.commit()
        if request.form.get("rating") != "":
            update.rating = request.form.get("rating")
            db.session.commit()
        if request.form.get("review") != "":
            update.review = request.form.get("review")
            db.session.commit()
        if request.form.get("img_url") != "":
            update.img_url = request.form.get("img_url")
            db.session.commit()
        all_films = db.session.query(Film).order_by(desc(Film.rating)).all()
        n = 0
        for film in all_films:
            film.ranking = n + 1
            db.session.commit()
            n += 1
        return render_template("index.html", films=all_films, admin=True)
    update_film = Film.query.filter_by(id=film_id).first()
    return render_template("edit.html", film=update_film, form=form)


@app.route("/<film_id>")
def delete(film_id):
    delete_film = Film.query.get(film_id)
    db.session.delete(delete_film)
    db.session.commit()
    all_films = db.session.query(Film).order_by(desc(Film.rating)).all()
    n = 0
    for film in all_films:
        film.ranking = n + 1
        db.session.commit()
        n += 1
    return render_template("index.html", films=all_films, admin=True)

@app.route("/ad/<login>")
def login(login):
    if login == admin_pass:
        all_films = db.session.query(Film).order_by(desc(Film.rating)).all()
        n = 0
        for film in all_films:
            film.ranking = n + 1
            db.session.commit()
            n += 1
        return render_template("index.html", films=all_films, admin=True)
    else:
        return render_template(url_for("home"))

@app.route("/")
def logout():
    return redirect(url_for("home", admin=False))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
