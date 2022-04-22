#For the non-auth routes 

from click import echo
from flask import Blueprint, render_template, url_for, redirect, request
from flask_login import login_required, current_user, login_manager
import tldextract
from . import db
from .models import Manga, MangaChapter, User
from .scrap_functions import functions_scrap

main = Blueprint('main', __name__)

@main.route("/")
@login_required
def home():
    rule = str(request.url_rule)

    mangas_list = Manga.query.all()

    echo(mangas_list[0])

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


@main.route("/abo")
@login_required
def mylist_abo():
    rule = str(request.url_rule)

    return render_template('abo.html',
                           rule=rule)


@main.route("/manga/<manga_id>", methods=['GET'])
@login_required
def DynamicUrl(manga_id):
    rule = str(request.url_rule)

    manga = Manga.query.get(manga_id)
    if manga is None:
        return redirect("/")

    return render_template('manga.html',
                           rule=rule,
                           manga=manga)


@main.route("/manga/read", methods=['POST'])
@login_required
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



@main.route("/add", methods=['GET'])
@login_required
def index():
    rule = str(request.url_rule)

    return render_template('add_follow.html',
                           rule=rule)


@main.route("/add", methods=['POST'])
@login_required
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

