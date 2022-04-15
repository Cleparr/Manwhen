from enum import unique
from unicodedata import name
from click import echo
from flask import Flask, render_template_string, request, render_template, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
import requests
from urllib.parse import urlparse
import tldextract
from bs4 import BeautifulSoup


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)


class Manga(db.Model):
    __tablename__ = 'manga'
    id = db.Column(db.Integer, primary_key=True)
    manga_chapters = db.relationship("MangaChapter",
                                     order_by="desc(MangaChapter.chapter_number)",
                                     backref="manga",
                                     lazy=True)

    name = db.Column(db.String(120), nullable=False, unique=True)
    url = db.Column(db.String(200), nullable=False)
    cover = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f"manga('{self.name}','{self.url}','{self.cover}')"


class MangaChapter(db.Model):
    __tablename__ = 'manga_chapter'
    id = db.Column(db.Integer, primary_key=True)
    manga_id = db.Column(db.Integer, db.ForeignKey('manga.id'))
    chapter_number = db.Column(db.Numeric, nullable=False)

    chapter_name = db.Column(db.String(100), nullable=False)
    chapter_url = db.Column(db.String(200), nullable=False)
    chapter_viewed = db.Column(db.Boolean(), default=False)

    def __repr__(self):
        return f"manga_chapter('{self.chapter_name}','{self.chapter_number}','{self.chapter_url}','{self.chapter_viewed}')"


# Fonction de scrapping pour le domaine scan-vf
def scan_vf_scrap():
    #Je séléctionne le dernier manga ajouté
    manga = Manga.query.order_by(Manga.id.desc()).first()

    html_text = requests.get(manga.url).text
    soup = BeautifulSoup(html_text, 'html.parser')

    #Je vais chercher les informations sur la page du manga en question
    online_chapters = soup.find_all('h5', {'class' : 'chapter-title-rtl'} )

    #Je cherche toutes les info (name, url, title)
    for num_chap in range(len(online_chapters)):

        last_chap_url = online_chapters[num_chap].find('a')['href']
        last_chap_title = online_chapters[num_chap].find('em').getText()

        last_chap_number_process = online_chapters[num_chap].find('a').getText()
        last_chap_number_process = last_chap_number_process.split()
        last_chap_number = last_chap_number_process[len(last_chap_number_process)-1]

        state = MangaChapter.query.filter_by(chapter_number=last_chap_number, manga_id = manga.id).first()

        if state is None :
            var = MangaChapter(chapter_number = last_chap_number,
                    chapter_url = last_chap_url, 
                    chapter_name = last_chap_title, 
                    manga = manga)
            db.session.add(var)
            

    db.session.commit()

def manga1st_scrap():
     #Je séléctionne le dernier manga ajouté
    manga = Manga.query.order_by(Manga.id.desc()).first()

    # J'itère sur tous les manga
    html_text = requests.get(manga.url).text
    soup = BeautifulSoup(html_text, 'html.parser')

    #Je vais chercher les informations sur la page du manga en question
    online_chapters = soup.find_all('li', {'class' : 'wp-manga-chapter'} )
    
    #Je cherche toutes les info (name, url, title)
    for num_chap in range(len(online_chapters)):
        last_chap_url = online_chapters[num_chap].find('a')['href']
        #Il n'y a pas le titre donc je prends "Chapitre x"
        last_chap_title = online_chapters[num_chap].find('a').getText()

        last_chap_number_process = online_chapters[num_chap].find('a').getText()
        last_chap_number_process = last_chap_number_process.split()
        last_chap_number = last_chap_number_process[len(last_chap_number_process)-1]

        state = MangaChapter.query.filter_by(chapter_number=last_chap_number, manga_id = manga.id).first()
        
        if state is None :
            var = MangaChapter(chapter_number = last_chap_number,
                    chapter_url = last_chap_url, 
                    chapter_name = last_chap_title, 
                    manga = manga)
            db.session.add(var)
            

    db.session.commit()



functions_scrap = {
    "scan-vf": scan_vf_scrap,
    "manga1st": manga1st_scrap
}


@app.route("/")
def home():
    rule = str(request.url_rule)

    mangas_list = Manga.query.all()


    true_count_list = []
    false_count_list = []
    for i in range(1,len(mangas_list)+1):
        true_count_list.append(len(MangaChapter.query.filter( MangaChapter.chapter_viewed == True , MangaChapter.manga_id== str(i)).all()))
        false_count_list.append(len(MangaChapter.query.filter( MangaChapter.chapter_viewed == False , MangaChapter.manga_id== str(i)).all()))

    echo(true_count_list)
    echo(false_count_list)

    return render_template('home.html',
                           rule=rule,
                           mangas_list=mangas_list,
                           count_true = true_count_list,
                           count_false = false_count_list)


@app.route("/abo")
def mylist_abo():
    rule = str(request.url_rule)

    return render_template('abo.html',
                           rule=rule)


@app.route("/manga/<manga_id>", methods=['GET'])
def DynamicUrl(manga_id):
    rule = str(request.url_rule)

    manga = Manga.query.get(manga_id)
    if manga is None:
        return redirect("/")

    return render_template('manga.html',
                           rule=rule,
                           manga=manga)


@app.route("/manga/read", methods=['POST'])
def mark_chap_as_read():

    manga_chapter_view_clicked = int(request.form['clic'])

    mangachapter = MangaChapter.query.get(manga_chapter_view_clicked)
    if mangachapter is None:
        return redirect("/")

    #mangachapter = (MangaChapter.query.filter(MangaChapter.chapter_number==manga_chapter_view_clicked,MangaChapter.manga_id=='1').first()).chapter_viewed

    # Si le chapitre est déjà lu, je le marque en non lu
    if mangachapter.chapter_viewed:
        mangachapter.chapter_viewed = False

    # Si le chapitre est pas encore lu
    else:
        MangaChapter.query.filter(MangaChapter.chapter_number <= mangachapter.chapter_number, MangaChapter.manga_id == mangachapter.manga_id).update({MangaChapter.chapter_viewed: True}, synchronize_session=False)

        
    db.session.commit()

    return redirect("/manga/"+ str(mangachapter.manga_id)) 



@app.route("/add", methods=['GET'])
def index():
    rule = str(request.url_rule)

    return render_template('add_follow.html',
                           rule=rule)


@app.route("/add", methods=['POST'])
def add_follow():
    rule = str(request.url_rule)

    manga_name = request.form['manga_name']
    manga_url_lecture = request.form['manga_url']
    manga_cover_url = request.form['manga_cover_url']

    # Checker si le nom existe déjà en base
    manga_name_check = db.session.query(Manga.id).filter_by(name=manga_name).scalar() is not None
    
    if manga_name_check == True:
        #Je pourrais ajouter ici un message d'erreur
        echo('Le manga est déjà en base')
        return redirect("/add")


    # Checker si l'url arrive bien sur un domain dont j'ai une fonction de scrapping 
    domain_url = tldextract.extract(manga_url_lecture)

    if domain_url.domain in functions_scrap:
        #Déjà j'ajoute le manga 
        manga_to_add = Manga(name=manga_name,
                         url=manga_url_lecture,
                         cover=manga_cover_url)

        db.session.add(manga_to_add)
        db.session.commit()

        #Ensuite j'ajoute les chapitres via l'appel de fonction dans le dict de fonction de scrapping
        functions_scrap[domain_url.domain]()

        # Retourner un message visuel que c'est ajouté en base // Qu'il y a eu une erreur (la spécifier)

        return redirect("/")

    else :  
        #Je pourrais ajouter ici un message d'erreur
        echo('Le domaine ne fait pas partie de ceux en base')
        return redirect("/add")

    
