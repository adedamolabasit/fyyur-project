from os import error
import babel
from flask import render_template, request, Response, flash, redirect, url_for, abort, jsonify
from operator import itemgetter

from wtforms.fields.core import DateTimeField
from create import app,db
from create.forms import VenueForm,ArtistForm,ShowForm
from create.model import Venue,Show,Artist
import re
import dateutil.parser
from datetime import datetime,timedelta


# i used this third party code to format the date and time
def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format="EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format="EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)
# this filter helper that used at the show page. It makes it user interactivity interesting.
app.jinja_env.filters['datetime'] = format_datetime


# the home page view
@app.route('/')
def page():
    return render_template('home.html')


# the venue create form with method GET

@app.route('/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('form/new_venue.html', form=form)


# the venue create form with method POST

@app.route('/create',methods=['POST'])
def venue_submission():
    form=VenueForm()
    if form.validate_on_submit:
        try:
            venue=Venue(
                name=form.name.data,
                city=form.city.data,
                state=form.state.data,
                address=form.address.data,
                phone=form.phone.data,
                image_link=form.image_link.data,
                facebook_link=form.facebook_link.data,
                website=form.website.data,
                seeking_description=form.seeking_description.data)
            error=False
            db.session.add(venue)
            db.session.commit()
        except:
            error=True
            db.session.rollback()
        finally:
            db.session.close()
        if not error:
            flash('venuewas succesfully listed')
            return redirect(url_for('venue'))
        else:
            flash('error occured could not be on the list' )
            return redirect(url_for('venue_create_submission'))


# the venue view
@app.route('/venues/page/')
def venue():

    venues = Venue.query.all()
    data=[]
    cities_states=set()
    for venue in venues:
        cities_states.add( (venue.city,venue.state) )
    cities_states =list(cities_states)
    cities_states.sort(key=itemgetter(1,0))
    now=datetime.now()
    for loc in cities_states:
        venues_list=[]
        for venue in venues:
            if (venue.city == loc[0]) and (venue.state ==loc[1]):

                venue_show=Show.query.filter_by(venue_id=venue.id).all()
                num_upcoming = 0
                for show in venue_show:
                    if show.start_time > now:
                        num_upcoming += 1
                venues_list.append({
                    'id':venue.id,
                    'name':venue.name,
                    'num_upcoming_shows': num_upcoming
                })
        data.append({
            'city':loc[0],
            'state':loc[1],
            'venues':venues_list
        })

   
    return render_template('venues.html', areas=data)

# the venue details view
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venue=Venue.query.get(venue_id)
    if not venue:
        # Redirect home
        return redirect(url_for('index'))
    else:
        genres = [ genre.name for genre in venue.genres ]
        
        # Get a list of shows and count the ones in the past and future
        past_shows = []
        past_shows_count = 0
        upcoming_shows = []
        upcoming_shows_count = 0
        now = datetime.now()
        for show in venue.shows:
            if show.start_time > now:
                upcoming_shows_count += 1
                upcoming_shows.append({
                    "artist_id": show.artist_id,
                    "artist_name": show.artist.name,
                    "artist_image_link": show.artist.image_link,
                    "start_time": format_datetime(str(show.start_time))
                })
            if show.start_time < now:
                past_shows_count += 1
                past_shows.append({
                    "artist_id": show.artist_id,
                    "artist_name": show.artist.name,
                    "artist_image_link": show.artist.image_link,
                    "start_time": format_datetime(str(show.start_time))
                })

        data = {
            "id": venue_id,
            "name": venue.name,
            "genres": genres,
            "address": venue.address,
            "city": venue.city,
            "state": venue.state,
            # "phone": (venue.phone[:3] + '-' + venue.phone[3:6] + '-' + venue.phone[6:]),
            "website": venue.website,
            "facebook_link": venue.facebook_link,
            "seeking_talent": venue.seeking_talent,
            "seeking_description": venue.seeking_description,
            "image_link": venue.image_link,
            "past_shows": past_shows,
            "past_shows_count": past_shows_count,
            "upcoming_shows": upcoming_shows,
            "upcoming_shows_count": upcoming_shows_count
        }
    return render_template('venue_details.html',venue=data)

# the venue delete view
@app.route('/venues/<venue_id>/delete',methods=['GET'])
def venue_delete(venue_id):
    venue=Venue.query.get(venue_id)
    if not venue:
        return redirect(url_for('home'))
    else:
        error_on_delete =False
        venue_name=venue.name
        try:
            db.session.delete(venue)
            db.session.commit()
        except:
            error_on_delete =True
            db.session.rollback()
        finally:
            db.session.close()
        if error_on_delete:
            flash(f'An error occured deleting venue {venue_name}.')
        else:
            return jsonify({
                'deleted':True,
                'url':url_for('venues')
            })
# the venue edit view 
@app.route('/venues/<int:venue_id>/edit')
def venue_edit(venue_id):
    venue=Venue.query.get(venue_id)
    if not venue:
        return redirect(url_for('page'))
    else:        
        form=VenueForm(obj=venue)
        venue={
            'id':venue_id,
            'name':venue.name,
            'genres':venue.genres,
            'city':venue.city,
            'state':venue.state,
            'phone':venue.phone,
            'website':venue.website,
            'facebook_link':venue.facebook_link,
            'image_link':venue.image_link}

    return render_template('form/edit_venue.html',form=form,venue=venue)


#  the artists view 
@app.route('/artists')
def artists_page():
    artists=Artist.query.order_by(Artist.name).all()
    data=[]
    for artist in artists:
        data.append({
            'id':artist.id,
            'name':artist.name
        })
    return render_template('artists.html',artists=data)


# the artist create view method GET

@app.route('/artists_create', methods=['GET'])
def artist_venue_form():
  form = ArtistForm()
  return render_template('form/new_artist.html', form=form)

# the artist create view method Post

@app.route('/artists_create',methods=['POST'])
def artists_create():
    form=ArtistForm()
    if form.validate_on_submit:
        try:
            artist=Artist(
                name=form.name.data,
                city=form.city.data,
                state=form.state.data,
                phone=form.state.data,
                genres=form.genres.data,
                image_link=form.image_link.data,
                facebook_link=form.genres.data,
                website=form.website.data,
                seeking_description=form.seeking_description.data
                )
            error=False
            db.session.add(artist)
            db.session.commit()
        except:
            error=True
            db.session.rollback()
        finally:
            db.session.close()
        if not error:
            flash('artist was succesfully listed')
            return redirect(url_for('artists_page'))
        if error:
            flash('error occured could not be on the list')
            return redirect(url_for('artists_create'))
            
# the artist details views
@app.route('/artists/<artist_id>')
def artist_details(artist_id):
    artist=Artist.query.get(artist_id)
    past_shows=[]
    past_shows_count=0
    upcoming_shows=[]
    upcoming_shows_count=0
    now=datetime.now()
    for show in artist.shows:
        if show.start_time > now:
            upcoming_shows_count += 1
            upcoming_shows.append({
                'venue_id':show.venue_id,
                'venue_name':show.venue.name,
                'venue_image_link':show.venue.image_link,
                'start_time':format_datetime(str(show.start_time))
            })
        if show.start_time < now:
            past_shows_count +=1
            past_shows.append({
                'venue_id':show.venue_id,
                'venue_name':show.venue.name,
                'venue_image_link':show.venue.image_link,
                'start_time':format_datetime(str(show.start_time))
            })
    data= {
        "id": artist_id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": (artist.phone[:3] + '-' + artist.phone[3:6] + '-' + artist.phone[6:]),
        "website": artist.website,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": past_shows,
        "past_shows_count": past_shows_count,
        "upcoming_shows": upcoming_shows,
        "upcoming_shows_count": upcoming_shows_count
        }

    return render_template('show_artist.html',artist=data)




# tthe artist edit view

@app.route('/artists/<int:artist_id>/edit',methods=['GET'])
def edit_artists(artist_id):
    artist=Artist.query.get(artist_id)
    if not artist:
        return redirect(url_for('page'))
    else:
        form=ArtistForm(obj=artist)
    # genres=[genre.name for genre in artist.genres]
    artist={
        'id':artist_id,
        'name':artist.name,
        'genres':artist.genres,
        'city':artist.city,
        'state':artist.state,
        'phone':artist.phone,
        'website':artist.website,
        'facebook_link':artist.facebook_link,
        'seeking_description':artist.seeking_description,
        'image_link':artist.image_link,
    }
    return render_template('form/edit_artist.html',form=form,artist=artist)

# the artist delete view

@app.route('/artists/<int:artist_id>/delete',methods=['GET'])
def artist_delete(artist_id):
    artist=Artist.query.get(artist_id)
    if not artist:
        return redirect(url_for('page'))
    else:
        error_on_delete=False
        artist_name=artist.name
    try:
        db.session.delete(artist)
        db.session.commit()
        return redirect(url_for('home'))
    except:
        error_on_delete=True
        db.session.rollback()
    finally:
        db.session.close()
    if error_on_delete:
        flash(f"An error occured deleting {artist.name}")
        abort(500)
    else:
        return jsonify({
            'deleted':True,
            'url':url_for('artist')
        })

# the show view
@app.route('/shows')
def shows():
    data=[]
    shows=Show.query.all()
    now=datetime.now()
    almost=timedelta(minutes=30)
    upcoming_shows=[]
    past_shows=[]
    before_show=[]


    for show in shows:
        if show.start_time > now :

            upcoming_shows.append({
                'venud_id':show.venue.id,
                'venue_name':show.venue.name,
                'artist_id':show.artist.id,
                'artist_name':show.artist.name,
                'artist_image_link':show.artist.image_link,
                'start_time':format_datetime(str(show.start_time)),
                'almost':almost,
                'now':now,
                
        })
        if show.start_time < now :
  
            past_shows.append({
                'venud_id':show.venue.id,
                'venue_name':show.venue.name,
                'artist_id':show.artist.id,
                'artist_name':show.artist.name,
                'artist_image_link':show.artist.image_link,
                'start_time':format_datetime(str(show.start_time)),
                

            })
  



    return render_template('show.html',shows=upcoming_shows ,past_shows=past_shows)

# the show create view method get


@app.route('/show_create',methods=['GET'])
def show_create():
    form=ShowForm()
    return render_template('form/new_show.html',form=form)


# the show create view mwthod view
@app.route('/show_create',methods=['POST'])
def show_create_post():
    form=ShowForm()
    if form.validate_on_submit:
        try:
            show=Show(
                artist_id=form.artist_id.data,
                venue_id=form.venue_id.data,
                start_time=form.start_time.data
            )
            db.session.add(show)
            db.session.commit()
            return redirect(url_for('artist'))

        except:
            error=True
            flash(" Show cant be created")
            db.session.rollback()
        finally:
            db.session.close()
        if not error:
            flash('successful')
        else:
            flash('An error occured')
            return redirect(url_for('show_create_post'))

# the search view
@app.route('/artist/search',methods=['GET'])
def search_artist():
    search = request.form.get('search_term', '').strip()
    artists = Artist.query.filter(Artist.name.ilike('%' + search + '%')).all()  
    
    print(artists)
    artist_list = []
    now = datetime.now()
    for artist in artists:
        artist_shows = Show.query.filter_by(artist_id=artist.id).all()
        num_upcoming = 0
        for show in artist_shows:
            if show.start_time > now:
                num_upcoming += 1

        artist_list.append({
        "id": artist.id,
        "name": artist.name,
        "num_upcoming_shows": num_upcoming 
        })

        response = {
        "count": len(artists),
        "data": artist_list
    }
    return render_template('search_artists.html', results=response, search_term=request.form.get('search_term', ''))
 

# i have a whole lot features to add but time won't permit me , i want to ask if i can commit more work to this later ..thanks in anticipation waiting for your responce 











































