import os
import json
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy

# Get base directory path
basedir = os.path.abspath(os.path.dirname(__file__))

# Initialize Flask app
app = Flask(__name__)

# Make `now` available in all templates
@app.context_processor
def inject_now():
    return {'now': datetime.now()}

# Config
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'mydb.sqlite3')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)
# Define models based on our database schema
class Movie(db.Model):
    __tablename__ = 'movies'
    
    movie_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    release_year = db.Column(db.Integer)
    runtime_minutes = db.Column(db.Integer)
    synopsis = db.Column(db.Text)
    poster_url = db.Column(db.String(255))
    upc = db.Column(db.String(50))
    isbn = db.Column(db.String(50))
    imdb_id = db.Column(db.String(20))
    tmdb_id = db.Column(db.String(20))
    format = db.Column(db.String(50))
    rating = db.Column(db.Float)
    watch_status = db.Column(db.Boolean, default=False)
    personal_notes = db.Column(db.Text)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    last_modified = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    genres = db.relationship('Genre', secondary='movie_genres', backref='movies')
    people = db.relationship('Person', secondary='movie_people', backref='movies')
    collections = db.relationship('Collection', secondary='movie_collections', backref='movies')
    tags = db.relationship('Tag', secondary='movie_tags', backref='movies')

class Genre(db.Model):
    __tablename__ = 'genres'
    
    genre_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

class MovieGenre(db.Model):
    __tablename__ = 'movie_genres'
    
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.movie_id', ondelete='CASCADE'), primary_key=True)
    genre_id = db.Column(db.Integer, db.ForeignKey('genres.genre_id', ondelete='CASCADE'), primary_key=True)

class Person(db.Model):
    __tablename__ = 'people'
    
    person_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    profile_url = db.Column(db.String(255))

class MoviePerson(db.Model):
    __tablename__ = 'movie_people'
    
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.movie_id', ondelete='CASCADE'), primary_key=True)
    person_id = db.Column(db.Integer, db.ForeignKey('people.person_id', ondelete='CASCADE'), primary_key=True)
    role_type = db.Column(db.String(50), nullable=False, primary_key=True)
    character_name = db.Column(db.String(100))

class Collection(db.Model):
    __tablename__ = 'collections'
    
    collection_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)

class MovieCollection(db.Model):
    __tablename__ = 'movie_collections'
    
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.movie_id', ondelete='CASCADE'), primary_key=True)
    collection_id = db.Column(db.Integer, db.ForeignKey('collections.collection_id', ondelete='CASCADE'), primary_key=True)

class Tag(db.Model):
    __tablename__ = 'tags'
    
    tag_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

class MovieTag(db.Model):
    __tablename__ = 'movie_tags'
    
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.movie_id', ondelete='CASCADE'), primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.tag_id', ondelete='CASCADE'), primary_key=True)

class ImportLog(db.Model):
    __tablename__ = 'import_logs'
    
    import_id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    import_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), nullable=False)
    records_total = db.Column(db.Integer)
    records_imported = db.Column(db.Integer)
    error_message = db.Column(db.Text)

# Routes
@app.route('/')
def index():
    movies = Movie.query.order_by(Movie.date_added.desc()).all()
    return render_template('index.html', movies=movies)

@app.route('/movie/<int:movie_id>')
def movie_detail(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    return render_template('movie_detail.html', movie=movie)

# Search routes
@app.route('/search')
def search():
    query = request.args.get('query', '')
    results = []
    
    if query:
        from search_utils import search_movies_by_keyword
        results = search_movies_by_keyword(query)
    
    return render_template('search.html', query=query, results=results)

@app.route('/search/identifier', methods=['GET', 'POST'])
def search_identifier():
    results = None
    
    if request.method == 'POST':
        identifier_type = request.form.get('identifier_type')
        identifier_value = request.form.get('identifier_value')
        
        if identifier_type and identifier_value:
            from search_utils import search_by_identifier
            results = search_by_identifier(identifier_type, identifier_value)
            
            if not results:
                flash(f'No movie found with {identifier_type}: {identifier_value}', 'warning')
    
    return render_template('search_identifier.html', results=results)

@app.route('/movie/add-from-search', methods=['POST'])
def add_movie_from_search():
    movie_data_json = request.form.get('movie_data')
    
    if not movie_data_json:
        flash('Invalid movie data', 'danger')
        return redirect(url_for('index'))
    
    try:
        movie_data = json.loads(movie_data_json)
        
        # Check if movie already exists in database
        existing_movie = None
        if movie_data.get('imdb_id'):
            existing_movie = Movie.query.filter_by(imdb_id=movie_data['imdb_id']).first()
        elif movie_data.get('tmdb_id'):
            existing_movie = Movie.query.filter_by(tmdb_id=movie_data['tmdb_id']).first()
        
        if existing_movie:
            flash(f'Movie "{existing_movie.title}" already exists in your collection', 'info')
            return redirect(url_for('movie_detail', movie_id=existing_movie.movie_id))
        
        # Create new movie
        new_movie = Movie(
            title=movie_data['title'],
            release_year=movie_data.get('release_year'),
            runtime_minutes=movie_data.get('runtime_minutes'),
            synopsis=movie_data.get('synopsis'),
            poster_url=movie_data.get('poster_url'),
            imdb_id=movie_data.get('imdb_id'),
            tmdb_id=movie_data.get('tmdb_id')
        )
        
        db.session.add(new_movie)
        db.session.flush()  # Get the movie_id without committing
        
        # Add genres
        for genre_name in movie_data.get('genres', []):
            genre = Genre.query.filter_by(name=genre_name).first()
            if not genre:
                genre = Genre(name=genre_name)
                db.session.add(genre)
                db.session.flush()
            
            movie_genre = MovieGenre(movie_id=new_movie.movie_id, genre_id=genre.genre_id)
            db.session.add(movie_genre)
        
        # Add directors and cast
        for director_name in movie_data.get('directors', []):
            person = Person.query.filter_by(name=director_name).first()
            if not person:
                person = Person(name=director_name)
                db.session.add(person)
                db.session.flush()
            
            movie_person = MoviePerson(
                movie_id=new_movie.movie_id, 
                person_id=person.person_id,
                role_type='director'
            )
            db.session.add(movie_person)
        
        for actor_name in movie_data.get('cast', []):
            person = Person.query.filter_by(name=actor_name).first()
            if not person:
                person = Person(name=actor_name)
                db.session.add(person)
                db.session.flush()
            
            movie_person = MoviePerson(
                movie_id=new_movie.movie_id, 
                person_id=person.person_id,
                role_type='actor'
            )
            db.session.add(movie_person)
        
        db.session.commit()
        flash(f'Movie "{new_movie.title}" added to your collection', 'success')
        return redirect(url_for('movie_detail', movie_id=new_movie.movie_id))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error adding movie: {str(e)}', 'danger')
        return redirect(url_for('index'))

# CSV Import routes
@app.route('/import/csv', methods=['GET', 'POST'])
def import_csv():
    import_results = None
    
    if request.method == 'POST':
        # Check if file was uploaded
        if 'csv_file' not in request.files:
            flash('No file selected', 'danger')
            return redirect(request.url)
        
        file = request.files['csv_file']
        
        # Check if file is empty
        if file.filename == '':
            flash('No file selected', 'danger')
            return redirect(request.url)
        
        # Check file extension
        if not file.filename.endswith('.csv'):
            flash('Only CSV files are allowed', 'danger')
            return redirect(request.url)
        
        # Process CSV file
        try:
            from csv_utils import parse_csv_file, create_import_log
            
            # Get existing movies for duplicate checking
            skip_duplicates = 'skip_duplicates' in request.form
            existing_movies = Movie.query.all() if skip_duplicates else None
            
            # Parse CSV file
            import_results = parse_csv_file(file, skip_duplicates, existing_movies)
            
            # If successful, add movies to database
            if import_results['success'] and import_results['movies']:
                for movie_data in import_results['movies']:
                    # Create new movie
                    new_movie = Movie(
                        title=movie_data['title'],
                        release_year=movie_data.get('release_year'),
                        runtime_minutes=movie_data.get('runtime_minutes'),
                        synopsis=movie_data.get('synopsis'),
                        poster_url=movie_data.get('poster_url'),
                        upc=movie_data.get('upc'),
                        isbn=movie_data.get('isbn'),
                        imdb_id=movie_data.get('imdb_id'),
                        tmdb_id=movie_data.get('tmdb_id'),
                        format=movie_data.get('format'),
                        watch_status=movie_data.get('watch_status', False),
                        personal_notes=movie_data.get('personal_notes')
                    )
                    
                    db.session.add(new_movie)
                    db.session.flush()  # Get the movie_id without committing
                    
                    # Add genres
                    for genre_name in movie_data.get('genres', []):
                        genre = Genre.query.filter_by(name=genre_name).first()
                        if not genre:
                            genre = Genre(name=genre_name)
                            db.session.add(genre)
                            db.session.flush()
                        
                        movie_genre = MovieGenre(movie_id=new_movie.movie_id, genre_id=genre.genre_id)
                        db.session.add(movie_genre)
                    
                    # Add directors
                    for director_name in movie_data.get('directors', []):
                        person = Person.query.filter_by(name=director_name).first()
                        if not person:
                            person = Person(name=director_name)
                            db.session.add(person)
                            db.session.flush()
                        
                        movie_person = MoviePerson(
                            movie_id=new_movie.movie_id, 
                            person_id=person.person_id,
                            role_type='director'
                        )
                        db.session.add(movie_person)
                    
                    # Add cast
                    for actor_name in movie_data.get('cast', []):
                        person = Person.query.filter_by(name=actor_name).first()
                        if not person:
                            person = Person(name=actor_name)
                            db.session.add(person)
                            db.session.flush()
                        
                        movie_person = MoviePerson(
                            movie_id=new_movie.movie_id, 
                            person_id=person.person_id,
                            role_type='actor'
                        )
                        db.session.add(movie_person)
                
                # Create import log
                import_log = ImportLog(
                    filename=file.filename,
                    status='completed' if import_results['failed'] == 0 else 'partial',
                    records_total=import_results['total'],
                    records_imported=import_results['imported'],
                    error_message='\n'.join(import_results['errors']) if import_results['errors'] else None
                )
                db.session.add(import_log)
                
                # Commit changes
                db.session.commit()
                flash(f"Successfully imported {import_results['imported']} movies", 'success')
            else:
                flash(import_results['message'], 'warning')
                
        except Exception as e:
            db.session.rollback()
            flash(f'Error importing CSV: {str(e)}', 'danger')
            import_results = {
                'success': False,
                'message': f'Error importing CSV: {str(e)}',
                'total': 0,
                'imported': 0,
                'skipped': 0,
                'failed': 0,
                'errors': [str(e)]
            }
    
    return render_template('import_csv.html', import_results=import_results)

@app.route('/download/csv-template')
def download_csv_template():
    from csv_utils import generate_csv_template
    from flask import Response
    
    template = generate_csv_template()
    
    return Response(
        template,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment;filename=movie_import_template.csv'}
    )

# Manual entry route
@app.route('/movie/add', methods=['GET', 'POST'])
def add_movie():
    if request.method == 'POST':
        try:
            # Get form data
            title = request.form.get('title')
            release_year = request.form.get('release_year')
            runtime_minutes = request.form.get('runtime_minutes')
            synopsis = request.form.get('synopsis')
            poster_url = request.form.get('poster_url')
            upc = request.form.get('upc')
            isbn = request.form.get('isbn')
            imdb_id = request.form.get('imdb_id')
            tmdb_id = request.form.get('tmdb_id')
            format_type = request.form.get('format')
            watch_status = 'watch_status' in request.form
            personal_notes = request.form.get('personal_notes')
            
            # Validate required fields
            if not title:
                flash('Title is required', 'danger')
                return render_template('add_movie.html', form=request.form)
            
            # Convert numeric fields
            if release_year:
                release_year = int(release_year)
            if runtime_minutes:
                runtime_minutes = int(runtime_minutes)
            
            # Create new movie
            new_movie = Movie(
                title=title,
                release_year=release_year,
                runtime_minutes=runtime_minutes,
                synopsis=synopsis,
                poster_url=poster_url,
                upc=upc,
                isbn=isbn,
                imdb_id=imdb_id,
                tmdb_id=tmdb_id,
                format=format_type,
                watch_status=watch_status,
                personal_notes=personal_notes
            )
            
            db.session.add(new_movie)
            db.session.flush()  # Get the movie_id without committing
            
            # Process directors
            directors = request.form.get('director', '')
            if directors:
                for director_name in [name.strip() for name in directors.split(',') if name.strip()]:
                    person = Person.query.filter_by(name=director_name).first()
                    if not person:
                        person = Person(name=director_name)
                        db.session.add(person)
                        db.session.flush()
                    
                    movie_person = MoviePerson(
                        movie_id=new_movie.movie_id, 
                        person_id=person.person_id,
                        role_type='director'
                    )
                    db.session.add(movie_person)
            
            # Process cast
            cast = request.form.get('cast', '')
            if cast:
                for actor_name in [name.strip() for name in cast.split(',') if name.strip()]:
                    person = Person.query.filter_by(name=actor_name).first()
                    if not person:
                        person = Person(name=actor_name)
                        db.session.add(person)
                        db.session.flush()
                    
                    movie_person = MoviePerson(
                        movie_id=new_movie.movie_id, 
                        person_id=person.person_id,
                        role_type='actor'
                    )
                    db.session.add(movie_person)
            
            # Process genres
            genres = request.form.get('genres', '')
            if genres:
                for genre_name in [name.strip() for name in genres.split(',') if name.strip()]:
                    genre = Genre.query.filter_by(name=genre_name).first()
                    if not genre:
                        genre = Genre(name=genre_name)
                        db.session.add(genre)
                        db.session.flush()
                    
                    movie_genre = MovieGenre(movie_id=new_movie.movie_id, genre_id=genre.genre_id)
                    db.session.add(movie_genre)
            
            # Commit changes
            db.session.commit()
            flash(f'Movie "{new_movie.title}" added to your collection', 'success')
            return redirect(url_for('movie_detail', movie_id=new_movie.movie_id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding movie: {str(e)}', 'danger')
            return render_template('add_movie.html', form=request.form)
    
    # For GET requests, render the form
    return render_template('add_movie.html', current_year=datetime.now().year)

# Collection management routes
@app.route('/collections')
def collections():
    collections = Collection.query.all()
    return render_template('collections.html', collections=collections)

@app.route('/collection/<int:collection_id>')
def collection_detail(collection_id):
    collection = Collection.query.get_or_404(collection_id)
    all_movies = Movie.query.all()
    return render_template('collection_detail.html', collection=collection, all_movies=all_movies)

@app.route('/collection/add', methods=['POST'])
def add_collection():
    try:
        name = request.form.get('name')
        description = request.form.get('description')
        
        if not name:
            flash('Collection name is required', 'danger')
            return redirect(url_for('collections'))
        
        new_collection = Collection(name=name, description=description)
        db.session.add(new_collection)
        db.session.commit()
        
        flash(f'Collection "{name}" created successfully', 'success')
        return redirect(url_for('collection_detail', collection_id=new_collection.collection_id))
    except Exception as e:
        db.session.rollback()
        flash(f'Error creating collection: {str(e)}', 'danger')
        return redirect(url_for('collections'))

@app.route('/collection/<int:collection_id>/edit', methods=['POST'])
def edit_collection(collection_id):
    try:
        collection = Collection.query.get_or_404(collection_id)
        
        name = request.form.get('name')
        description = request.form.get('description')
        
        if not name:
            flash('Collection name is required', 'danger')
            return redirect(url_for('collection_detail', collection_id=collection_id))
        
        collection.name = name
        collection.description = description
        db.session.commit()
        
        flash(f'Collection updated successfully', 'success')
        return redirect(url_for('collection_detail', collection_id=collection_id))
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating collection: {str(e)}', 'danger')
        return redirect(url_for('collection_detail', collection_id=collection_id))

@app.route('/collection/<int:collection_id>/delete', methods=['POST'])
def delete_collection(collection_id):
    try:
        collection = Collection.query.get_or_404(collection_id)
        db.session.delete(collection)
        db.session.commit()
        
        flash(f'Collection "{collection.name}" deleted successfully', 'success')
        return redirect(url_for('collections'))
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting collection: {str(e)}', 'danger')
        return redirect(url_for('collection_detail', collection_id=collection_id))

@app.route('/collection/<int:collection_id>/add-movies', methods=['POST'])
def add_to_collection(collection_id):
    try:
        collection = Collection.query.get_or_404(collection_id)
        movie_ids = request.form.getlist('movie_ids')
        
        if not movie_ids:
            flash('No movies selected', 'warning')
            return redirect(url_for('collection_detail', collection_id=collection_id))
        
        added_count = 0
        for movie_id in movie_ids:
            movie = Movie.query.get(movie_id)
            if movie and movie not in collection.movies:
                movie_collection = MovieCollection(movie_id=movie_id, collection_id=collection_id)
                db.session.add(movie_collection)
                added_count += 1
        
        db.session.commit()
        
        if added_count > 0:
            flash(f'Added {added_count} movies to collection', 'success')
        else:
            flash('No new movies added to collection', 'info')
        
        return redirect(url_for('collection_detail', collection_id=collection_id))
    except Exception as e:
        db.session.rollback()
        flash(f'Error adding movies to collection: {str(e)}', 'danger')
        return redirect(url_for('collection_detail', collection_id=collection_id))

@app.route('/collection/<int:collection_id>/remove-movie/<int:movie_id>', methods=['POST'])
def remove_from_collection(collection_id, movie_id):
    try:
        movie_collection = MovieCollection.query.filter_by(
            movie_id=movie_id, 
            collection_id=collection_id
        ).first_or_404()
        
        db.session.delete(movie_collection)
        db.session.commit()
        
        flash('Movie removed from collection', 'success')
        return redirect(url_for('collection_detail', collection_id=collection_id))
    except Exception as e:
        db.session.rollback()
        flash(f'Error removing movie from collection: {str(e)}', 'danger')
        return redirect(url_for('collection_detail', collection_id=collection_id))

# Initialize the database
@app.cli.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    db.drop_all()
    db.create_all()
    print('Initialized the database.')

# Create context processor for template globals
@app.context_processor
def utility_processor():
    def format_date(date):
        if date:
            return date.strftime('%Y-%m-%d')
        return ''
    return dict(format_date=format_date)

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.route('/scan_barcode')
def scan_barcode():
    """
    Render the barcode scanner page with camera access.
    """
    return render_template('scan_barcode.html')

@app.route('/api/search/<identifier_type>/<identifier_value>')
def api_search_by_identifier(identifier_type, identifier_value):
    """
    API endpoint to search for a movie by identifier (UPC, ISBN, IMDB ID, TMDB ID).
    Returns JSON response with movie data if found.
    """
    if not identifier_type or not identifier_value:
        return jsonify({'success': False, 'message': 'Missing identifier'})
    
    # Validate identifier type
    valid_types = ['upc', 'isbn', 'imdb_id', 'tmdb_id']
    if identifier_type not in valid_types:
        return jsonify({'success': False, 'message': 'Invalid identifier type'})
    
    try:
        # Import search utilities
        from search_utils import search_by_identifier
        
        # Search for movie by identifier
        movie = search_by_identifier(identifier_type, identifier_value)
        
        if movie:
            return jsonify({
                'success': True,
                'movie': movie
            })
        else:
            return jsonify({
                'success': False,
                'message': f'No movie found with {identifier_type}: {identifier_value}'
            })
            
    except Exception as e:
        print(f"API search error: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error searching for movie: {str(e)}'
        })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0')
