#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for,abort,jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app,db)
# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
class Show(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'))
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'))
    start_date = db.Column(db.DateTime, nullable=False)

class Venue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.String(500))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website= db.Column(db.String(120))
    seeking_talent=db.Column(db.Boolean, nullable=False)
    seeking_description=db.Column(db.String(120))
    shows = db.relationship('Show', backref='venue', lazy=True)
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website= db.Column(db.String(120))
    seeking_venue=db.Column(db.Boolean, nullable=False)
    seeking_description=db.Column(db.String(120))
    shows = db.relationship('Show', backref='artist', lazy=True)
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  #date = dateutil.parser.parse(value)
  date = value
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  groupedLocations = db.session.query(Venue.city,Venue.state, db.func.count(Venue.id)).group_by(Venue.city,Venue.state).all()
  db_data = []
  for location in groupedLocations:
        area = {}
        area['city']=location.city
        area['state']=location.state
        area['venues'] = Venue.query.join(Show).filter(Venue.city==location.city).filter(Show.start_date > datetime.now()).all()
        db_data.append(area)
        #console.log(venues)
  return render_template('pages/venues.html', areas=db_data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term=request.form.get('search_term', '')
  search = "%{}%".format(search_term)
  search_response = Venue.query.filter(Venue.name.ilike(search)).all()
  return render_template('pages/search_venues.html', results=search_response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.filter(Venue.id == venue_id).first()
  venue_response = {}
  venue_response['id'] = venue_id
  venue_response['name'] = venue.name
  venue_response['genres'] = venue.genres.split(',')
  venue_response['address'] = venue.address
  venue_response['city'] = venue.city
  venue_response['state'] = venue.state
  venue_response['phone'] = venue.phone
  venue_response['website'] = venue.website
  venue_response['facebook_link'] = venue.facebook_link
  venue_response['seeking_talent'] = venue.seeking_talent
  venue_response['seeking_description'] = venue.seeking_description
  venue_response['image_link'] = venue.image_link
  past_shows = Artist.query.join(Show).add_columns(Show.start_date.label("start_time")).filter(Show.venue_id==venue_id).filter(Show.start_date < datetime.now()).all()
  venue_response['past_shows']=past_shows
  upcoming_shows = Artist.query.join(Show).add_columns(Show.start_date.label("start_time")).filter(Show.venue_id==venue_id).filter(Show.start_date > datetime.now()).all()
  venue_response['upcoming_shows']=upcoming_shows
  #data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  return render_template('pages/show_venue.html', venue=venue_response)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error = False
  body = {}
  try:
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    address = request.form['address']
    phone = request.form['phone']
    genre_list = request.form.getlist('genres')
    image_link = request.form['image_link']
    facebook_link = request.form['facebook_link']
    website = request.form['website']
    seeking_talent = True if 'seeking_talent' in request.form else False 
    seeking_description = request.form['seeking_description']
    genres = ','.join(genre_list)
    print(genres) 
    venue = Venue(name=name, city=city, state=state, address=address, phone=phone, genres=genres, facebook_link=facebook_link, image_link=image_link, website=website, seeking_talent=seeking_talent, seeking_description=seeking_description)
    db.session.add(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    #abort (400)
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  else:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  error = False
  body = {}
  try:
    venue = Venue.query.filter(Venue.id == venue_id).first()
    venue_name = venue.name
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
    venue_name =venue_id;
  finally:
    db.session.close()
  if error:
    #abort (400)
    status =False
  else:
    status =True
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return jsonify({ 'status': status })

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artists = Artist.query.all()
  return render_template('pages/artists.html', artists=artists)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term=request.form.get('search_term', '')
  search = "%{}%".format(search_term)
  search_response = Artist.query.filter(Artist.name.ilike(search)).all()
  return render_template('pages/search_artists.html', results=search_response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  artist = Artist.query.filter(Artist.id == artist_id).first()
  artist_response = {}
  artist_response['id'] = artist_id
  artist_response['name'] = artist.name
  artist_response['genres'] = artist.genres.split(',')
  artist_response['city'] = artist.city
  artist_response['state'] = artist.state
  artist_response['phone'] = artist.phone
  artist_response['website'] = artist.website
  artist_response['facebook_link'] = artist.facebook_link
  artist_response['seeking_venue'] = artist.seeking_venue
  artist_response['seeking_description'] = artist.seeking_description
  artist_response['image_link'] = artist.image_link
  past_shows = Venue.query.join(Show).add_columns(Show.start_date.label("start_time")).filter(Show.artist_id==artist_id).filter(Show.start_date < datetime.now()).all()
  artist_response['past_shows']=past_shows
  upcoming_shows = Venue.query.join(Show).add_columns(Show.start_date.label("start_time")).filter(Show.artist_id==artist_id).filter(Show.start_date > datetime.now()).all()
  artist_response['upcoming_shows']=upcoming_shows
  #data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artist=artist_response)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET','POST'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  print(artist)
  if request.method == 'GET' and artist: 
    form.name.data = artist.name
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.genres.data = artist.genres
    form.facebook_link.data = artist.facebook_link
    form.image_link.data = artist.image_link
    form.website.data = artist.website
    form.seeking_venue.data = artist.seeking_venue
    form.seeking_description.data = artist.seeking_description
  if request.method == 'POST':
        error = False
        try:
          artist.name = request.form['name']
          artist.city = request.form['city']
          artist.state = request.form['state']
          artist.phone = request.form['phone']
          genre_list = request.form.getlist('genres')
          artist.genres = ','.join(genre_list)
          artist.image_link = request.form['image_link']
          artist.facebook_link = request.form['facebook_link']
          artist.website = request.form['website']
          artist.seeking_venue = True if 'seeking_venue' in request.form else False 
          artist.seeking_description = request.form['seeking_description']
          db.session.commit()
        except:
          error = True
          db.session.rollback()
          print(sys.exc_info())
        finally:
          db.session.close()
        if error:
          flash('An error occurred. Artist could not be changed.')
          return render_template('forms/edit_artist.html', form=form, artist=artist)
        else:
          flash('Artist updated successfully.')
          return redirect(url_for('show_artist', artist_id=artist_id))

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/venues/<int:venue_id>/edit', methods=['GET','POST'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  if request.method == 'GET' and venue: 
    form.name.data = venue.name
    form.city.data = venue.city
    form.state.data = venue.state
    form.phone.data = venue.phone
    form.address.data = venue.address
    form.genres.data = venue.genres
    form.facebook_link.data = venue.facebook_link
    form.image_link.data = venue.image_link
    form.website.data = venue.website
    form.seeking_talent.data = venue.seeking_talent
    form.seeking_description.data = venue.seeking_description
  if request.method == 'POST':
        error = False
        try:
          venue.name = request.form['name']
          venue.city = request.form['city']
          venue.state = request.form['state']
          venue.address = request.form['address']
          venue.phone = request.form['phone']
          genre_list = request.form.getlist('genres')
          venue.genres = ','.join(genre_list)
          venue.image_link = request.form['image_link']
          venue.facebook_link = request.form['facebook_link']
          venue.website = request.form['website']
          venue.seeking_talent = True if 'seeking_talent' in request.form else False 
          venue.seeking_description = request.form['seeking_description']
          db.session.commit()
        except:
          error = True
          db.session.rollback()
          print(sys.exc_info())
        finally:
          db.session.close()
        if error:
          flash('An error occurred. Venue could not be changed.')
          return render_template('forms/edit_venue.html', form=form, venue=venue)
        else:
          flash('Venue updated successfully.')
          return redirect(url_for('show_venue', venue_id=venue_id))
  return render_template('forms/edit_venue.html', form=form, venue=venue)

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET','POST'])
def create_artist_form():
  form = ArtistForm()
  if request.method == 'GET':
    return render_template('forms/new_artist.html', form=form)
  if request.method == 'POST':
    error = False
    try:
      name = request.form['name']
      city = request.form['city']
      state = request.form['state']
      phone = request.form['phone']
      genre_list = request.form.getlist('genres')
      image_link = request.form['image_link']
      facebook_link = request.form['facebook_link']
      website = request.form['website']
      seeking_venue = True if 'seeking_venue' in request.form else False
      seeking_description = request.form['seeking_description']
      genres = ','.join(genre_list)
      print(genres) 
      artist = Artist(name=name, city=city, state=state, phone=phone, genres=genres, facebook_link=facebook_link, image_link=image_link, website=website, seeking_venue=seeking_venue, seeking_description=seeking_description)
      db.session.add(artist)
      db.session.commit()
    except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
    finally:
      db.session.close()
    if error:
      #abort (400)
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    else:
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  show = db.session.query(Show).join(Artist).join(Venue).add_columns(Artist.name.label('artist_name')).add_columns(Venue.name.label('venue_name')).add_columns(Artist.image_link.label('artist_image_link')).filter(Show.start_date > datetime.now()).order_by(db.asc(Show.start_date)).all()
  data=[{
    "venue_id": 1,
    "venue_name": "The Musical Hop",
    "artist_id": 4,
    "artist_name": "Guns N Petals",
    "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "start_time": "2035-04-08 20:00:00"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 5,
    "artist_name": "Matt Quevedo",
    "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "start_time": "2035-04-08 20:00:00"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-08 20:00:00"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-08 20:00:00"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-08 20:00:00"
  }]
  return render_template('pages/shows.html', shows=show)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  # on successful db insert, flash success
  flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
