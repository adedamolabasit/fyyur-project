from create import app
from datetime import datetime
from create import db








# create model for genre
class Genre(db.Model):
    __tablename__='genre'
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(50))


artist_genre_table=db.Table('artist_genre_table',
db.Column('genre_id',db.Integer,db.ForeignKey('genre.id'),primary_key=True),
db.Column('artist_id',db.Integer,db.ForeignKey('Artist.id'),primary_key=True))

venue_genre_table=db.Table('venue_genre_table',
db.Column('genre_id',db.Integer,db.ForeignKey('genre.id'),primary_key=True),
db.Column('venue_id',db.Integer,db.ForeignKey('Venue.id'),primary_key=True))

# venue model
class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False,server_default='False')
    seeking_description = db.Column(db.String(120))
    genres = db.relationship('Genre', secondary=venue_genre_table, backref=db.backref('venues'))
    shows = db.relationship('Show',cascade='all,delete' ,backref='venue', lazy=True)

    def __repr__(self):
        return f'<Venue {self.id} {self.name}>'



class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120))
    shows = db.relationship('Show',cascade='all,delete', backref='artist', lazy=True)   

    def __repr__(self):
        return f'<Artist {self.id} {self.name}>'



class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)   

    # Foreign key is the tablename.pk
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)   
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)

    def __repr__(self):
        return f'<Show {self.id} {self.start_time} artist_id={self.artist_id} venue_id={self.venue_id}>'











