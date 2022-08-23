from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, URL
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)


API_KEY="4e31dca8f4152b6670e871ece73293d6"
API_URL="https://api.themoviedb.org/3/search/movie"
MOVIE_DB_IMG_URL="https://image.tmdb.org/t/p/w500/"

app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///movies-collection.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db=SQLAlchemy(app)

class Movie(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String,unique=True,nullable=True)
    year=db.Column(db.Integer,nullable=True)
    description=db.Column(db.String,nullable=True)
    rating=db.Column(db.Float,nullable=True)
    ranking=db.Column(db.Integer,nullable=True)
    review=db.Column(db.String,nullable=True)
    img_url=db.Column(db.String,nullable=True)

    def __repr__(self):
        return '<User %r>' % self.username

db.create_all()

class MovieForm(FlaskForm):
    rating=StringField(label="Your Rating Out of 10 e.g 7.5",validators=[DataRequired()])
    review=StringField(label="Your Review",validators=[DataRequired()])
    submit=SubmitField("Done")

class AddForm(FlaskForm):
    name=StringField(label="Movie Title",validators=[DataRequired()])
    submit=SubmitField("Add Movie")

@app.route("/")
def home():
    all_movies= Movie.query.order_by(Movie.rating).all()
    return render_template("index.html",movies=all_movies)

@app.route('/edit/<id>',methods=["POST","GET"])
def edit(id):
    form=MovieForm()
    movie=Movie.query.get(id)
    if form.validate_on_submit():
        new_rating=form.rating.data
        new_review=form.review.data
        movie.rating=new_rating
        movie.review=new_review
        db.session.add(movie)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('edit.html',form=form,title=movie.title)

@app.route('/delete/<id>')
def delete(id):
    movie=Movie.query.get(id)
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/add',methods=["GET","POST"])
def add():
    form=AddForm()
    if form.validate_on_submit():
        movie=form.name.data
        parameters={
            "api_key":API_KEY,
            "query":movie,
            "include_adult":True
        }
        response=requests.get(url=f"{API_URL}?",params=parameters)
        data=response.json()
        movies=data["results"]
        return render_template('select.html',movies=movies)
    return render_template('add.html',form=form)

@app.route('/find<id>')
def find(id):
    id=int(id)
    response=requests.get(url=f"https://api.themoviedb.org/3/movie/{id}?api_key={API_KEY}&language=en-US")
    movie=response.json()
    name=movie["title"]
    img=f"{MOVIE_DB_IMG_URL}/{movie['poster_path']}"
    year=movie["release_date"]
    description=movie["overview"]
    new_movie=Movie(title=name,img_url=img,year=year,description=description)
    db.session.add(new_movie)
    db.session.commit()
    movie=Movie.query.filter_by(title=name).first()
    movie_id=movie.id
    return redirect(url_for('edit',id=movie_id))



if __name__ == '__main__':
    app.run(debug=True)
