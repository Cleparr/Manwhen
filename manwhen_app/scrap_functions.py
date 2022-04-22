# Scrapping functions for the app

import requests
from bs4 import BeautifulSoup

from . import db
from .models import Manga, MangaChapter, User

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

# Fonction de scrapping pour le domaine manga1st_scrap
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

