#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
from cmath import phase
import json
from unittest import result
from xmlrpc.client import Boolean

import dateutil.parser
import babel
from flask import Flask, render_template, request, abort, jsonify, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from models import db, Artist, Venue, Shows
from types import SimpleNamespace
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)

migrate = Migrate(app, db)

# TODO: connect to a local postgresql database
SQLALCHEMY_DATABASE_URI = 'postgresql://Olawale@localhost:5432/fyyur-db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
# Used MVC Done
## #----------------------------------------------------------------------------#
# # Filters.
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
  areas_data = []
  query_data = Venue.query.distinct(Venue.city, Venue.state).all()
  for q_data in query_data:
        ven_info = {
            "city": q_data.city,
            "state": q_data.state
        }
        
        venues = Venue.query.filter_by(city=q_data.city, state=q_data.state).all()
        arr_of_venues = []
        for venue in venues:
            arr_of_venues.append({
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": len(list(filter(lambda x: x.start_time > datetime.now(), venue.shows)))
            })
        
        ven_info["venues"] = arr_of_venues
        areas_data.append(ven_info)
   
  return render_template('pages/venues.html', areas=areas_data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  search_term = request.form.get('search_term')
  query_data = Venue.query.filter(
      Venue.name.ilike('%{}%'.format(search_term))).all() 
  results = {}
  results['count'] = len(query_data)
  results['data'] = query_data
  return render_template('pages/search_venues.html', results=results, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venue = Venue.query.get(venue_id)

    past_shows = list(filter(lambda x: x.start_time <
                             datetime.today(), venue.shows))
    upcoming_shows = list(filter(lambda x: x.start_time >=
                                 datetime.today(), venue.shows))

    past_shows = list(map(lambda x: x.show_artist(), past_shows))
    upcoming_shows = list(map(lambda x: x.show_artist(), upcoming_shows))

    data = venue.make_dict()
    data['past_shows'] = past_shows
    data['upcoming_shows'] = upcoming_shows
    data['past_shows_count'] = len(past_shows)
    data['upcoming_shows_count'] = len(upcoming_shows)
    
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
  error = False
  try:
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    address = request.form['address']
    phone = request.form['phone']
    website = request.form['website_link']
    facebook_link = request.form['facebook_link']
    genres = request.form['genres']
    image_link = request.form['image_link']
    seeking_talent = request.form.get('seeking_talent')
    seeking_description = request.form['seeking_description']
    venue = Venue(name = name, city = city , state = state, address = address, phone = phone, genres = genres, facebook_link = facebook_link, website =website, image_link = image_link, seeking_talent = Boolean(seeking_talent), seeking_description = seeking_description )
   
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.  
  except:
    error = True
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  finally:
    return render_template('pages/home.html' )
   # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
    flash("Venue " + venue.name + " was deleted successfully!")
  except:
    db.session.rollback()
    flash("Venue was not deleted successfully.")
  finally:
    db.session.close()

  return redirect(url_for("index"))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  query_data = Artist.query.all()
  return render_template('pages/artists.html', artists=query_data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  
  search_term = request.form.get('search_term')
  query_data = Artist.query.filter(
      Artist.name.ilike('%{}%'.format(search_term))).all() 
  results = {}
  results['count'] = len(query_data)
  results['data'] = query_data

  return render_template('pages/search_artists.html', results=results,
                           search_term=request.form.get('search_term', ''))



  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist = Artist.query.get(artist_id)

  past_shows = list(filter(lambda x: x.start_time <
                             datetime.today(), artist.shows))  #Anoymouse function that filters past shows
  upcoming_shows = list(filter(lambda x: x.start_time >=
                                 datetime.today(), artist.shows))

  past_shows = list(map(lambda x: x.show_venue(), past_shows))
  upcoming_shows = list(map(lambda x: x.show_venue(), upcoming_shows))  #Anoymouse function that filters upcoming shows

  data = artist.make_dict()
  data['past_shows'] = past_shows
  data['upcoming_shows'] = upcoming_shows
  data['past_shows_count'] = len(past_shows)
  data['upcoming_shows_count'] = len(upcoming_shows)
  
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  # TODO: populate form with fields from artist with ID <artist_id>
  
  artist = Artist.query.get(artist_id)

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
   try:
        update = Artist.query.get(artist_id) 

        name = request.form.get("name")
        city = request.form.get("city")
        state = request.form.get("state")
        phone = request.form.get("phone")
        genres = request.form.getlist("genres")
        facebook_link = request.form.get("facebook_link")

        update.name = name
        update.city = city
        update.state = state
        update.phone = phone
        update.facebook_link = facebook_link
        update.image_link = "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"

        db.session.add(update)
        db.session.commit()

        db.session.refresh(update)
        flash("This artist was successfully updated!")

   except:
      db.session.rollback()
      flash( "An error occurred. Artist "+ request.form.get("name") + " could not be updated.")
   finally:
      db.session.close()
      return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  try:
        ed_venue = Venue.query.get(venue_id)

        data = {
            "id": ed_venue.id,
            "name": ed_venue.name,
            "city": ed_venue.city,
            "state": ed_venue.state,
            "address": ed_venue.address,
            "phone": ed_venue.phone,
            "genres": ed_venue.genres,
            "facebook_link": ed_venue.facebook_link,
            "seeking_talent": ed_venue.seeking_talent,
            "seeking_description": ed_venue.seeking_description,
            "image_link": ed_venue.image_link,
        }

  except:
    flash("Something went wrong. Please try again.")
    return redirect(url_for("index"))

  finally:
    db.session.close()
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=data)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  try:
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    address = request.form['address']
    phone = request.form['phone']
    genres = request.form['genres']
    facebook_link = request.form['facebook_link']

    edit_venue_data = Venue.query.get(venue_id)

    edit_venue_data.name = name
    edit_venue_data.city = city
    edit_venue_data.state = state
    edit_venue_data.address = address
    edit_venue_data.phone = phone
    edit_venue_data.facebook_link = facebook_link
    edit_venue_data.genres = genres

    db.session.add(edit_venue_data)
    db.session.commit()
    db.session.refresh(edit_venue_data)
    flash("This venue was successfully updated!")
  except:
    db.session.rollback()
    flash( "An error occurred. Venue " + request.form.get("name") + " could not be updated.")
  finally:
    db.session.close()
    return redirect(url_for("show_venue", venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error = False
  try:
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    website = request.form['website_link']
    facebook_link = request.form['facebook_link']
    genres = request.form['genres']
    image_link = request.form['image_link']
    seeking_venue = request.form.get('seeking_venue')
    seeking_description = request.form['seeking_description']
    
    artist = Artist(name = name, city = city , state = state, phone = phone, genres = genres, facebook_link = facebook_link, website=website, image_link = image_link, seeking_venue = Boolean(seeking_venue), seeking_description = seeking_description )
    
    db.session.add(artist)
    db.session.commit()

    flash('Artist ' + request.form['name'] + ' was successfully listed!')
   # TODO: on unsuccessful db insert, flash an error instead.
  except:
    error = True
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  finally:
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
   return render_template('pages/home.html' )


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
      
  arr_of_shows = []
  try:
    shows = Shows.query.all()
    for show in shows:
          venue_id = show.venue_id
          artist_id = show.artist_id
          artist = Artist.query.get(artist_id)
          
          show_info = {
            "venue_id": venue_id,
            "venue_name": Venue.query.get(venue_id).name,
            "artist_id": artist_id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": str(show.start_time),
            }
          arr_of_shows.append(show_info)

  except:
    db.session.rollback()
    print('Something went wrong')
  finally:
    print('The try except is finished')
    return render_template('pages/shows.html', shows=arr_of_shows)

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
  error = False
  try:
    show = Shows()
    show.artist_id = request.form['artist_id']
    show.venue_id = request.form['venue_id']
    show.start_time = request.form['start_time']
    db.session.add(show)
    db.session.commit()
    flash('Requested show was successfully listed')
  except:
    error = True
    db.session.rollback()
    flash('An error occurred. Requested show could not be listed.')
  finally:
    db.session.close()
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
