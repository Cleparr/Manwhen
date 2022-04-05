from app import Manga, MangaChapter, db

db.create_all()  

one_piece = Manga(name = "One Piece",url = "https://www.scan-vf.net/one_piece/")
boruto = Manga(name = "Boruto", url= "https://www.scan-vf.net/boruto")
fairytail100 = Manga(name = "Fairy Tail 100 Years Quest", url= "https://www.scan-vf.net/fairy-tail-100-years-quest'")
onepunchman = Manga(name = "One Punch Man", url= "https://www.scan-vf.net/one-punch-man")
hxh = Manga(name = "Hunter X Hunter", url= "https://www.scan-vf.net/hunter-x-hunter")


db.session.add_all([one_piece,boruto,fairytail100,onepunchman,hxh]) 


chap_1044_onepiece = MangaChapter(chapter_number = '1044', chapter_url = 'https://www.scan-vf.net/one_piece/chapitre-1044/' , manga = Manga(name="one_piece" ))


db.session.commit()

