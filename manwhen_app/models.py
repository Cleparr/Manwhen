#Our user model

from click import echo
from . import db
from flask_login import UserMixin, LoginManager


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
    id = db.Column(db.Integer, primary_key=True, index = True)
    manga_id = db.Column(db.Integer, db.ForeignKey('manga.id'), index = True)
    chapter_number = db.Column(db.Numeric, nullable=False)

    chapter_name = db.Column(db.String(100), nullable=False)
    chapter_url = db.Column(db.String(200), nullable=False)
    chapter_viewed = db.Column(db.Boolean(), default=False)

    def __repr__(self):
        return f"manga_chapter('{self.chapter_name}','{self.chapter_number}','{self.chapter_url}','{self.chapter_viewed}')"

class User(UserMixin,db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f"user('{self.email}','{self.password}')"

def init_db():
    db.create_all()

if __name__ == '__main__':
    init_db()