import csv
import io
import json
from datetime import datetime

def parse_csv_file(file_stream, skip_duplicates=True, existing_movies=None):
    """
    Parse a CSV file containing movie data
    Returns a tuple of (success, results)
    """
    results = {
        'success': False,
        'message': '',
        'total': 0,
        'imported': 0,
        'skipped': 0,
        'failed': 0,
        'errors': [],
        'movies': []
    }
    
    try:
        # Read CSV file
        csv_data = file_stream.read().decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(csv_data))
        
        # Get field names
        field_names = csv_reader.fieldnames
        
        # Check required fields
        if 'title' not in field_names:
            results['message'] = 'CSV file must contain a "title" column'
            return results
        
        # Process rows
        for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 to account for header row
            try:
                # Skip empty rows
                if not row['title'].strip():
                    continue
                
                # Process row data
                movie_data = process_csv_row(row)
                
                # Check for duplicates if requested
                if skip_duplicates and existing_movies:
                    is_duplicate = False
                    for existing_movie in existing_movies:
                        if (existing_movie.title.lower() == movie_data['title'].lower() and
                            existing_movie.release_year == movie_data.get('release_year')):
                            is_duplicate = True
                            results['skipped'] += 1
                            break
                    
                    if is_duplicate:
                        continue
                
                # Add movie to results
                results['movies'].append(movie_data)
                results['imported'] += 1
                
            except Exception as e:
                results['failed'] += 1
                results['errors'].append(f"Row {row_num}: {str(e)}")
        
        results['total'] = results['imported'] + results['skipped'] + results['failed']
        
        if results['imported'] > 0:
            results['success'] = True
            results['message'] = f"Successfully imported {results['imported']} movies"
        else:
            results['message'] = "No movies were imported"
        
    except Exception as e:
        results['success'] = False
        results['message'] = f"Error processing CSV file: {str(e)}"
    
    return results

def process_csv_row(row):
    """
    Process a single row from the CSV file
    Returns a dictionary of movie data
    """
    # Basic movie data
    movie_data = {
        'title': row['title'].strip(),
        'release_year': None,
        'runtime_minutes': None,
        'synopsis': None,
        'poster_url': None,
        'upc': None,
        'isbn': None,
        'imdb_id': None,
        'tmdb_id': None,
        'format': None,
        'watch_status': False,
        'personal_notes': None,
        'directors': [],
        'cast': [],
        'genres': []
    }
    
    # Process release year
    if 'release_year' in row and row['release_year'].strip():
        try:
            movie_data['release_year'] = int(row['release_year'].strip())
        except ValueError:
            pass
    
    # Process runtime
    if 'runtime_minutes' in row and row['runtime_minutes'].strip():
        try:
            movie_data['runtime_minutes'] = int(row['runtime_minutes'].strip())
        except ValueError:
            pass
    
    # Process text fields
    for field in ['synopsis', 'poster_url', 'upc', 'isbn', 'imdb_id', 'tmdb_id', 'format', 'personal_notes']:
        if field in row and row[field].strip():
            movie_data[field] = row[field].strip()
    
    # Process watch status
    if 'watch_status' in row and row['watch_status'].strip().lower() in ['watched', 'true', 'yes', '1']:
        movie_data['watch_status'] = True
    
    # Process directors
    if 'director' in row and row['director'].strip():
        movie_data['directors'] = [name.strip() for name in row['director'].split(',') if name.strip()]
    
    # Process cast
    if 'cast' in row and row['cast'].strip():
        movie_data['cast'] = [name.strip() for name in row['cast'].split(',') if name.strip()]
    
    # Process genres
    if 'genre' in row and row['genre'].strip():
        movie_data['genres'] = [genre.strip() for genre in row['genre'].split(',') if genre.strip()]
    
    return movie_data

def generate_csv_template():
    """
    Generate a CSV template file for movie import
    Returns a string containing the CSV template
    """
    fields = [
        'title', 'release_year', 'director', 'cast', 'genre', 
        'runtime_minutes', 'synopsis', 'format', 'upc', 'isbn', 
        'imdb_id', 'tmdb_id', 'poster_url', 'watch_status', 'personal_notes'
    ]
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header row
    writer.writerow(fields)
    
    # Write example row
    example = [
        'The Shawshank Redemption',
        '1994',
        'Frank Darabont',
        'Tim Robbins, Morgan Freeman, Bob Gunton',
        'Drama',
        '142',
        'Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.',
        'Blu-ray',
        '12345678901',
        '',
        'tt0111161',
        '278',
        'https://image.tmdb.org/t/p/w500/q6y0Go1tsGEsmtFryDOJo3dEmqu.jpg',
        'watched',
        'My favorite movie of all time'
    ]
    writer.writerow(example)
    
    return output.getvalue()

def create_import_log(filename, status, records_total, records_imported, error_message=None):
    """
    Create an import log entry
    Returns a dictionary with import log data
    """
    return {
        'filename': filename,
        'import_date': datetime.utcnow(),
        'status': status,
        'records_total': records_total,
        'records_imported': records_imported,
        'error_message': error_message
    }
