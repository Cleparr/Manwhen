from enum import unique
from unicodedata import name
from click import echo
from flask import Flask, render_template_string, request, render_template, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
import requests
from urllib.parse import urlparse
import tldextract


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app) 

class Manga(db.Model):
    __tablename__ = 'manga'
    id = db.Column(db.Integer, primary_key= True)
    manga_chapters = db.relationship("MangaChapter", 
                                    order_by = "desc(MangaChapter.chapter_number)",
                                    backref="manga", 
                                    lazy=True)


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

    mangas_list = Manga.query.all()

    
    return render_template('home.html',
        rule = rule,
        mangas_list = mangas_list )


@app.route("/abo")
def mylist_abo():
    rule = str(request.url_rule)

    return render_template('abo.html',
    rule = rule)


@app.route("/manga/<manga_id>")
def DynamicUrl(manga_id):
    rule = str(request.url_rule)

    manga = Manga.query.get(manga_id)
    if manga is None:
        return redirect("/")
    
    return render_template('manga.html',
    rule = rule,
    manga = manga)


@app.route("/add", methods=['GET'])
def index():
    rule = str(request.url_rule)
    
    return render_template('add_follow.html',
        rule = rule)

@app.route("/add", methods=['POST'])
def add_follow():
    rule = str(request.url_rule)

    manga_name = request.form['manga_name']
    manga_url_lecture = request.form['manga_url']
    manga_cover_url = request.form['manga_cover_url']

    # Checker si le nom existe déjà en base
    manga_name_check = db.session.query(Manga.id).filter_by(name=manga_name).scalar() is not None
       
    #Checker si l'url arrive bien sur une page que je connais : https://www.scan-vf.net/

    domain_url = tldextract.extract(manga_url_lecture)

    echo(domain_url.domain)

    if domain_url.domain != 'scan-vf' :
        return redirect("/add")
    
        
    manga_to_add = Manga(name = manga_name,
                            url = manga_url_lecture,
                            cover = manga_cover_url)
    
    db.session.add(manga_to_add)

    db.session.commit()

    #Retourner un message visuel que c'est ajouté en base // Qu'il y a eu une erreur (la spécifier)

    return redirect("/")

