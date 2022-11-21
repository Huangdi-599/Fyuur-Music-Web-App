#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from datetime import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
## MIGRATION
migrate = Migrate(app,db)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
class Shows(db.Model):
    __tablename__ = 'Shows'
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    start_datetime = db.Column(db.DateTime, nullable = False)



class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String (500), nullable=False)
    genres = db.Column("genres",db.ARRAY(db.String ()), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    facebook_link = db.Column(db.String(120), nullable=False)
    website_link = db.Column(db.String(120), nullable=False)
    seeking_description = db.Column(db.String(120), nullable=False)
    seeking_talent = db.Column(db.Boolean, nullable=False, default=True)
    show = db.relationship('Shows',backref= db.backref('venue', lazy =True))
  

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column("genres",db.ARRAY(db.String ()), nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    facebook_link = db.Column(db.String(120), nullable=False)
    website_link = db.Column(db.String(120), nullable=False)
    seeking_venue = db.Column(db.Boolean,nullable = False, default =True)
    seeking_description =db.Column(db.String(10000), nullable=False)
    show = db.relationship('Shows',backref= db.backref('artist', lazy =True))


    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

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
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  ven = []
  response=[]

  areas = Venue.query.distinct(Venue.city, Venue.state).all()
  for area in areas:
   city ={
     'city' :area.city,
     'state' : area.state
   }
  venues = Venue.query.filter_by(state = area.state, city =area.city).all()
  for venue in venues:
    ven.append({
      'id' : area.id,
      'name': area.name,
    })
    city['venues']= ven
    response.append(city)
  return render_template('pages/venues.html', areas=response)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  data = []
  search_term=request.form.get('search_term')
  response = Venue.query.filter(Venue.name.like('%'+search_term+'%')).all()
  count = len(response)
  for res in response:
    info = {
      "id" : res.id,
      "name" : res.name

    }
    data.append(info)

  results ={
    'count' : count,
    'data' : data
    }
   
  return render_template('pages/search_venues.html', results=results,search_term=request.form.get('search_term',''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  upcoming_shows=[]
  past_shows=[]
  

  venue_data=Venue.query.filter(Venue.id==venue_id).one_or_none()
  upcoming_shows_data= db.session.query(Shows).join(Venue).filter(Shows.artist_id == Artist.id).filter(Shows.start_datetime > datetime.now()).all()
  for show in upcoming_shows_data:
    upcomingshow = {
      'artist_id': show.artist_id,
      'artist_name': show.artist.name,
      'artist_image_link': show.artist.image_link,
      'start_time': str(show.start_datetime)
      }
    upcoming_shows.append(upcomingshow)
  past_shows_data = db.session.query(Shows).join(Venue).filter(Shows.venue_id == venue_id).filter(Shows.start_datetime < datetime.now()).all()
  for show in past_shows_data:
    pastshow = {
      'artist_id': show.artist_id,
      'artist_name': show.artist.name,
      'artist_image_link': show.artist.image_link,
      'start_time': str(show.start_datetime)
      }
    past_shows.append(pastshow)
  data = {
    'id': venue_data.id,
    'name': venue_data.name,
    'genres': venue_data.genres,
    'address': venue_data.address,
    'city': venue_data.city,
    'state': venue_data.state,
    'phone': venue_data.phone,
    'website': venue_data.website_link,
    'facebook_link': venue_data.facebook_link,
    'seeking_talent': venue_data.seeking_talent,
    'seeking_description': venue_data.seeking_description,
    'image_link':  venue_data.image_link.strip('"'),
    'past_shows': past_shows,
    'upcoming_shows': upcoming_shows,
    'past_shows_count': len(past_shows),
    'upcoming_shows_count': len(upcoming_shows)
  }

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)
@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm(request.form)
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  try:
    if form.validate():

      venue = Venue(
      name = form.name.data,
      phone = form.phone.data,
      city= form.city.data,
      address = form.address.data,
      genres = form.genres.data,
      image_link = form.image_link.data,
      state = form.state.data,
      website_link = form.website_link.data, 
      facebook_link = form.facebook_link.data,
      seeking_talent = form.seeking_talent.data,
      seeking_description = form.seeking_description.data
      )

      db.session.add(venue)
      db.session.commit()
  except():
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    error = True
    print(sys.exc_info())
  finally:
    db.session.close()
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
  try:
      delete_venue = Venue.query.get(venue_id)
      db.session.delete(delete_venue)
      db.session.commit()
  except():
      db.session.rollback()
      flash('An error occurred. Venue ' + request.form['delete_venue.name'] + ' could not be deleted.')
     
  finally:
      db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')

def artists():
  # TODO: replace with real data returned from querying the database
  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  data = []
  search_term=request.form.get('search_term')
  response = Artist.query.filter(Artist.name.like('%'+search_term+'%')).all()
  count = len(response)
  for res in response:
    info = {
      "id" : res.id,
      "name" : res.name

    }
    data.append(info)

  results ={
    'count' : count,
    'data' : data
    }
  return render_template('pages/search_artists.html', results=results, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  upcoming_shows=[]
  past_shows=[]
  artist_data=Artist.query.filter(Artist.id==artist_id).one_or_none()
  past_shows_data = db.session.query(Shows).join(Artist).filter(Shows.artist_id == artist_id).filter(Shows.start_datetime < datetime.now()).all()
  for show in past_shows_data:
    past = {
      'venue_id': show.venue_id,
      'venue_name': show.venue.name,
      'venue_image_link': show.venue.image_link,
      'start_time': str(show.start_datetime)
      }
    past_shows.append(past)

  upcoming_shows_data = db.session.query(Shows).join(Artist).filter(Shows.artist_id == artist_id).filter(Shows.start_datetime > datetime.now()).all()
  for show in upcoming_shows_data:
    upcoming = {
      'venue_id': show.venue_id,
      'venue_name': show.venue.name,
      'venue_image_link': show.venue.image_link,
      'start_time': str(show.start_datetime)
      }
    upcoming_shows.append(upcoming)
  data = {
    'id': artist_data.id,
    'name': artist_data.name,
    'genres': artist_data.genres,
    'city': artist_data.city,
    'state': artist_data.state,
    'phone': artist_data.phone,
    'website': artist_data.website_link,
    'facebook_link': artist_data.facebook_link,
    'seeking_venue': artist_data.seeking_venue,
    'seeking_description': artist_data.seeking_description,
    'image_link':  artist_data.image_link.strip('"'),
    'past_shows': past_shows,
    'upcoming_shows': upcoming_shows,
    'past_shows_count': len(past_shows),
    'upcoming_shows_count': len(upcoming_shows)
  }
  return render_template('pages/show_artist.html', artist=data)

# Update

#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  edit_artist = Artist.query.get(artist_id)
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=edit_artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form = ArtistForm(request.form)
  try:
    edit_artist = Artist.query.get(artist_id)
    edit_artist.name = form.name.data
    edit_artist.phone = form.phone.data
    edit_artist.city= form.city.data
    edit_artist.genres = form.genres.data
    edit_artist.image_link = form.image_link.data
    edit_artist.state = form.state.data
    edit_artist.website_link = form.website_link.data 
    edit_artist.facebook_link = form.facebook_link.data
    edit_artist.seeking_venue = form.seeking_venue.data
    edit_artist.seeking_description = form.seeking_description.data    
   
    db.session.add(edit_artist)
    db.session.commit()
  except():
    db.session.rollback()
    flash('An error occurred. Artist could not be updated.')
    error = True
    print(sys.exc_info())
  finally:
    db.session.close()
    flash('Artist was successfully updated!')

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  edit_venue = Venue.query.get(venue_id)
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form,venue=edit_venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm(request.form)
  try:
    edit_venue = Venue.query.get(venue_id)
    edit_venue.name = form.name.data
    edit_venue.phone = form.phone.data
    edit_venue.city= form.city.data
    edit_venue.address = form.address.data
    edit_venue.genres = form.genres.data
    edit_venue.image_link = form.image_link.data
    edit_venue.state = form.state.data
    edit_venue.website_link = form.website_link.data 
    edit_venue.facebook_link = form.facebook_link.data
    edit_venue.seeking_talent = form.seeking_talent.data
    edit_venue.seeking_description = form.seeking_description.data    
   
    db.session.add(edit_venue)
    db.session.commit()
  except():
    db.session.rollback()
    flash('An error occurred. Venue could not be updated.')
    error = True
    print(sys.exc_info())
  finally:
    db.session.close()
    flash('Venue was successfully updated!')
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)
#done
@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm(request.form)
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  try:
    if form.validate():

      artist = Artist(
      name = form.name.data,
      phone = form.phone.data,
      city= form.city.data,
      genres = form.genres.data,
      image_link = form.image_link.data,
      state = form.state.data,
      website_link = form.website_link.data, 
      facebook_link = form.facebook_link.data,
      seeking_venue = form.seeking_venue.data,
      seeking_description = form.seeking_description.data
      )

      db.session.add(artist)
      db.session.commit()
  except():
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    error = True
    print(sys.exc_info())
  finally:
    db.session.close()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data=[]
  shows = Shows.query.all()
  for show in shows:
    show_data= {
      'venue_id': show.venue_id,
      'venue_name': show.venue.name,
      'artist_id': show.artist_id,
      'artist_name': show.artist.name,
      'artist_image_link': show.artist.image_link.strip('"'),
      'start_time': str(show.start_datetime)
    }
    data.append(show_data)

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():

  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  form = ShowForm(request.form)
  try:
    if form.validate():
    
      show = Shows(
      venue_id = form.venue_id.data,
      artist_id = form.artist_id.data,
      start_datetime =form.start_time.data
      )

      db.session.add(show)
      db.session.commit()
  except():
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
    error = True
    print(sys.exc_info())
  finally:
    db.session.close()
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
