from enum import unique
from unicodedata import name
from click import echo
from flask import Flask, render_template_string, request, render_template, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app) 

class Manga(db.Model):
    __tablename__ = 'manga'
    id = db.Column(db.Integer, primary_key= True)
    manga_chapters = db.relationship("MangaChapter", backref="manga", lazy=True)


    name = db.Column(db.String(120), nullable= False, unique = True)
    url = db.Column(db.String(200), nullable= False)
    cover = db.Column(db.String(200), nullable= False)
 

    def __repr__(self):
        return f"manga('{self.name}','{self.url}','{self.cover}')"


class MangaChapter(db.Model):
    __tablename__ = 'manga_chapter'
    manga_id = db.Column(db.Integer, db.ForeignKey('manga.id'), primary_key= True)
    chapter_number = db.Column(db.Integer, nullable= False , primary_key= True)

    chapter_name = db.Column(db.String(100), nullable= False)
    chapter_url = db.Column(db.String(200), nullable= False)


    def __repr__(self):
        return f"manga_chapter('{self.chapter_name}','{self.chapter_number}','{self.chapter_url}')"




@app.route("/")
def home():
    rule = str(request.url_rule)

    manga = Manga.query.all()

    
    return render_template('home.html',
        rule = rule,
        manga = manga )


@app.route("/abo")
def mylist_abo():
    rule = str(request.url_rule)

    return render_template('abo.html',
    rule = rule)

