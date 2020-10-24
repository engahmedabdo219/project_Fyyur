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
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
migrate=Migrate(app,db)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website=db.Column(db.String(120))
    seeking_talent=db.Column(db.Boolean,default=False)
    seeking_description = db.Column(db.String(500))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    show=db.relationship('show',backref=db.backref('artist',lazy=True))
   # Artist= db.relationship('Artist',secondary=show,backref=db.backref('artist',lazy="dynamic"))
class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venuu=db.Column(db.Boolean,default=False)
    seeking_description = db.Column(db.String(500))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    show=db.relationship('show',backref=db.backref("venue",lazy=True))

    #Venue = db.relationship('Venue',secondary=show,backref=db.backref("venue",lazy="dynamic"))


# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class show(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   #name = db.Column(db.String,nullable=True)
   venu_id=db.Column(db.Integer, db.ForeignKey('Venue.id'))
   artist_id=db.Column(db.Integer, db.ForeignKey('Artist.id'))
   start_time=db.Column(db.DateTime,nullable=False)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format,locale='en')

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
  

  
  data = []

  # Get areas
  areas = Venue.query.with_entities(Venue.city, Venue.state).group_by(Venue.city, Venue.state).all()

    # Iterate over each area
  for area in areas:
      data_venues = []

      # Get venues by area
      venues = Venue.query.filter_by(state=area.state,city=area.city).all()

        # Iterate over each venue
      for venue in venues:
          # Get upcoming shows by venue
          upcoming_shows = db.session.query(show).filter(show.venu_id == venue.id).filter(show.start_time > datetime.now()).all()

            # Map venues
          data_venues.append({
            'id': venue.id,
            'name': venue.name,
            'num_upcoming_shows': len(upcoming_shows)
            })

        # Map areas
      data.append({
        'city': area.city,
        'state': area.state,
        'venues': data_venues
        })

  return render_template('pages/venues.html',areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
 
  search_term=request.form['search_term']
  search = "%{}%".format(search_term)

    # Get venues
  venues = Venue.query.with_entities(Venue.id, Venue.name).filter(Venue.name.match(search)).all()

    # Iterate over each venue
  data_venues = []
  for venue in venues:
        # Get upcoming shows by venue
      upcoming_shows = db.session.query(show).filter(show.venu_id == venue.id).filter(show.start_time > datetime.now()).all() 
      data_venues.append({
          'id': venue.id,
          'name': venue.name,
          'num_upcoming_shows': len(upcoming_shows)
        })

    
  data= {
      'venues': data_venues,
      'count': len(venues)
    }
  
  return render_template('pages/search_venues.html', results=data, search_term=search_term)
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  
  #data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  data_venue= Venue.query.filter(Venue.id==venue_id).first()
  upcoming_shows = db.session.query(Venue,show).join(Artist).filter(show.venu_id == venue_id,Artist.id==show.artist_id).filter(show.start_time > datetime.now()).all() 
  if len(upcoming_shows)>0:
    data_Upcoming_show=[]
    for upcoming in upcoming_shows:
      artist=db.session.query(Artist).join(show).filter(Artist.id==show.artist_id).first()
      data_Upcoming_show.append({
       'artist_id': artist.id,
       'artist_name':artist.name,
       'artist_image_link':artist.image_link,
        'start_time':str(upcoming[1].start_time)
        }) 
    data_venue.upcoming_shows=data_Upcoming_show
    data_venue.upcoming_shows_count=len(upcoming_shows)
  past_shows=db.session.query(Venue,show).join(Artist).filter(venue_id==show.venu_id,Artist.id==show.artist_id).filter(show.start_time<datetime.now()).all()
  if len(past_shows)>0:
    data_past_show=[]
    for past in past_shows:
      artist=db.session.query(Artist).join(show).filter(Artist.id==show.artist_id).first()
      data_past_show.append({
         'artist_id': artist.id,
         'artist_name':artist.name,
         'artist_image_link':artist.image_link,
         'start_time':str(past[1].start_time)
         }) 
    data_venue.past_shows=data_past_show
    data_venue.past_shows_count=len(past_shows)   



  return render_template('pages/show_venue.html', venue=data_venue)


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
  form = VenueForm()
  
  error=False
  name = request.form['name']
  city = request.form['city']
  state = request.form['state']
  address = request.form['address']
  phone = request.form['phone']
  genres = request.form.getlist('genres')
  image_link = request.form['image_link']
  facebook_link = request.form['facebook_link']
  website = request.form['website']
  seeking_talent=request.form['seeking_talent']
  seeking_description=request.form['seeking_description']
  
  #seeking_description = request.form['seeking_description']
  try:
    venue = Venue(
          name=name,
          city=city,
          state=state,
          address=address,
          phone=phone,
          genres=genres,
          image_link=image_link,
          facebook_link=facebook_link,
          website=website,
          seeking_talent=seeking_talent,
          seeking_description=seeking_description
            
            
          )
    db.session.add(venue)
    db.session.commit()
  except:
    error=True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()        

    # on successful db insert, flash success
  if error==False:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
  if error:
    flash('Venue ' + request.form['name'] + ' was unsuccessfully listed!')
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error=False
  try:
    venue = Venue.query.filter_by(id==venue_id).delete()
    db.session.delete(venue)
    db.session.commit()
  except:
    error=True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
      
      flash('An error occurred. Venue could not be deleted.',)
          
          
        
  if not error:
      flash('Venue was successfully deleted!',)
          
          
        
  

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
 
  data=[]
  artist= Artist.query.with_entities(Artist.id, Artist.name).order_by('id').all()
  for artists in artist:
    data.append({
      'id':artists.id,
      'name':artists.name

    })  


  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
 
  search_term = request.form['search_term']
  search = "%{}%".format(search_term)

 
  artists = Artist.query \
    .with_entities(Artist.id, Artist.name) \
    .filter(Artist.name.match(search)) \
    .all()

    # Iterate over each venue
  data_artist = []
  for artist in artists:
        # Get upcoming shows by venue
      upcoming_shows = db.session \
            .query(show) \
             .filter(show.artist_id == artist.id) \
              .filter(show.start_time > datetime.now()) \
                .all()

        # Map venues
      data_artist.append({
          'id': artist.id,
          'name': artist.name,
          'num_upcoming_shows': len(upcoming_shows)
        })

    # Map results
  results = {
      'artists': data_artist,
      'count': len(artists)
  }
  
  return render_template('pages/search_artists.html', results=results, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  
  #data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  data_artist =Artist.query.filter(Artist.id==artist_id).first()
  upcoming_shows = db.session.query(Artist,show).join(Venue).filter(show.artist_id == Artist.id,show.venu_id==Venue.id).filter(show.start_time > datetime.now()).all() 

  if len(upcoming_shows)>0:
    data_Upcoming_show=[]
    for upcoming in upcoming_shows:
      if upcoming[1]:
      
        venue=db.session.query(Venue).join(show).filter(Venue.id==show.venu_id).first()
        data_Upcoming_show.append({
        'venue_id': venue.id,
        'venue_name':venue.name,
        'venue_image_link':venue.image_link,
          'start_time':str(upcoming[1].start_time)
          }) 
    data_artist.upcoming_shows=data_Upcoming_show
    data_artist.upcoming_shows_count=len(upcoming_shows)
  past_shows = db.session.query(Artist,show).join(Venue).filter(show.artist_id == Artist.id,show.venu_id==Venue.id).filter(show.start_time < datetime.now()).all()
  if len(past_shows)>0:
    data_past_show=[]
    for past in past_shows:
      venue=db.session.query(Venue).join(show).filter(Venue.id==show.venu_id).first()
      data_past_show.append({
          'venue_id': venue.id,
          'venue_name':venue.name,
          'venue_image_link':venue.image_link,
          'start_time':str(past[1].start_time)
          }) 
    data_artist.past_shows=data_past_show
    #print(data)
    data_artist.past_shows_count=len(past_shows)
    #print(data)

  return render_template('pages/show_artist.html', artist=data_artist)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  
  # TODO: populate form with fields from artist with ID <artist_id>
  artist=Artist.query.filter(Artist.id==artist_id).all()
 
  form.name.data = artist.name
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.genres.data = artist.genres
  form.image_link.data = artist.image_link
  form.facebook_link.data = artist.facebook_link
  form.website.data = artist.website
  form.seeking_venuu.data=artist.seeking_venuu
  form.seeking_description.data=artist=artist.seeking_description


  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  name=request.form('name')
  city=request.form('city')
  state = request.form['state']
  phone = request.form['phone']
  genres = request.form.getlist('genres')
  image_link = request.form['image_link']
  facebook_link = request.form['facebook_link']
  website = request.form['website']
  seeking_venuu=request.form['seeking_venuu']
  seeking_description=request.form['seeking_description']
  error=False
  try:
    artists=Artist.query.filter(Artist.id==artist_id).all()
    artists.name=name
    artists.city=city
    artists.state = state
    artists.phone = phone
    artists.genres = genres
    artists.image_link = image_link
    artists.facebook_link = facebook_link
    artists.website = website
    artists.seeking_venuuu=seeking_venuu
    artists.seeking_description=seeking_description
    db.session.commit()
  except:
    error=True
    db.session.rollback()
    print(sys.exc_info()) 
  finally:
    db.session.close()  
  
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  
  # TODO: populate form with values from venue with ID <venue_id>
  venue=Venue.query.filter_by(Venue.id==venue_id).all()
 
  form.name.data = Venue.name
  form.city.data = Venue.city
  form.state.data = Venue.state
  form.phone.data = Venue.phone
  form.genres.data = Venue.genres
  form.image_link.data = Venue.image_link
  form.facebook_link.data = Venue.facebook_link
  form.website.data = Venue.website
  form.seeking_talent=Venue.seeking_talent
  form.seeking_description=Venue.seeking_description
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  name=request.form('name')
  city=request.form('city')
  state = request.form['state']
  phone = request.form['phone']
  genres = request.form.getlist('genres')
  image_link = request.form['image_link']
  facebook_link = request.form['facebook_link']
  website = request.form['website']
  seeking_description=request.form['seeking_description']
  seeking_talent=request.form['seeking_talent']
  error=False
  try:
    venues=Venue.query.get(venue_id).all()
    venues.name=name
    venues.city=city
    venues.state = state
    venues.phone = phone
    venues.genres = genres
    venues.image_link = image_link
    venues.facebook_link = facebook_link
    venues.website = website
    venues.seeking_description=seeking_description
    venues.seeking_talent=seeking_talent
    db.session.commit()
  except:
    error=True
    db.session.rollback()
    print(sys.exc_info()) 
  finally:
    db.session.close()  
  return redirect(url_for('show_venue', venue_id=venue_id))

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
  form = ArtistForm()
  error=False
  name = request.form['name']
  city = request.form['city']
  state = request.form['state']
  address = request.form['address']
  phone = request.form['phone']
  genres = request.form.getlist('genres')
  image_link = request.form['image_link']
  facebook_link = request.form['facebook_link']
  #website = request.form['website']
  
  
  try:
    artists = Artist(
          name=name,
          city=city,
          state=state,
         address=address,
          phone=phone,
          genres=genres,
          image_link=image_link,
          facebook_link=facebook_link,
         # website=website,
          
          
        )
    db.session.add(artists)
    db.session.commit()
  except:
    error=True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()        

  # on successful db insert, flash success
  if error==False:
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  if error:
    flash('Artist ' + request.form['name'] + ' was unsuccessfully listed!')

 
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  
  data = []

    # Get data
  shows = db.session.query(Venue.name,Artist.name,Artist.image_link,show.venu_id,show.artist_id, show.start_time) .filter(Venue.id == show.venu_id, Artist.id == show.artist_id)

    # Map data
  for Show in shows:
      data.append({
        'venue_name': Show[0],
        'artist_name': Show[1],
        'artist_image_link': Show[2],
        'venue_id': Show[3],
        'artist_id': Show[4],
        'start_time': str(Show[5])
        })

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
  error = False
  form = ShowForm()

    # Get data
  artist_id = request.form['artist_id']
  venu_id = request.form['venue_id']
  start_time = request.form['start_time']

  try:
    
    # Create model
    Show = show(
       artist_id=artist_id,
       venu_id=venu_id,
       start_time=start_time
          )

          # Update DB
    db.session.add(Show)
    db.session.commit()
  except :
      error = True
      db.session.rollback()
      print(sys.exc_info())
  finally:
      db.session.close()

    # Show banner
  if error:
      flash('An error occurred. Show could not be listed.',)
          
       
  if not error:
        flash('Show was successfully listed!',)
          
          
       


 
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
