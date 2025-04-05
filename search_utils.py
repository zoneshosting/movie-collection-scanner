import os
import json
import requests
from flask import request, jsonify, flash, redirect, url_for

# API key for The Movie Database (TMDb)
TMDB_API_KEY = "6f1b33dc51fa128bb66f25f15d7ece66"  # This is a placeholder key, would need a real one in production
OMDB_API_KEY = "a1b2c3d4"  # This is a placeholder key, would need a real one in production

def search_by_identifier(identifier_type, identifier_value):
    """
    Search for a movie using various identifiers (UPC, ISBN, IMDB ID, TMDB ID)
    Returns movie data if found, None otherwise
    """
    if identifier_type == 'upc':
        # UPC lookup could use a product database API
        # For now, we'll simulate by searching TMDB by EAN/UPC
        # In a real implementation, you would use a UPC/product database API
        return search_by_upc(identifier_value)
    
    elif identifier_type == 'isbn':
        # ISBN lookup could use a book database API
        # For now, we'll simulate by searching for movie adaptations
        return search_by_isbn(identifier_value)
    
    elif identifier_type == 'imdb_id':
        # Search by IMDB ID using OMDB API
        return search_by_imdb_id(identifier_value)
    
    elif identifier_type == 'tmdb_id':
        # Search by TMDB ID
        return search_by_tmdb_id(identifier_value)
    
    return None

def search_by_upc(upc):
    """
    Search for a movie by UPC code
    In a real implementation, this would use a UPC database API
    For now, we'll simulate by searching TMDB with the UPC as a keyword
    """
    # This is a simplified implementation
    # In reality, you would use a dedicated UPC/barcode database API
    
    # For demonstration, we'll search TMDB by UPC as keyword
    # This is not reliable but serves as a placeholder
    url = f"https://api.themoviedb.org/3/search/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "query": upc,
        "include_adult": "false"
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if response.status_code == 200 and data.get('results') and len(data['results']) > 0:
            # Take the first result
            movie_data = data['results'][0]
            return format_tmdb_result(movie_data)
    except Exception as e:
        print(f"Error searching by UPC: {e}")
    
    return None

def search_by_isbn(isbn):
    """
    Search for a movie by ISBN
    In a real implementation, this would use a book database API to find the book,
    then search for movie adaptations of that book
    """
    # This is a simplified implementation
    # In reality, you would use a book database API like Google Books or Open Library
    # to get the book title, then search for movie adaptations
    
    # For demonstration, we'll search TMDB by ISBN as keyword
    # This is not reliable but serves as a placeholder
    url = f"https://api.themoviedb.org/3/search/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "query": isbn,
        "include_adult": "false"
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if response.status_code == 200 and data.get('results') and len(data['results']) > 0:
            # Take the first result
            movie_data = data['results'][0]
            return format_tmdb_result(movie_data)
    except Exception as e:
        print(f"Error searching by ISBN: {e}")
    
    return None

def search_by_imdb_id(imdb_id):
    """
    Search for a movie by IMDB ID using OMDB API
    """
    # Ensure the IMDB ID has the correct format (tt followed by numbers)
    if not imdb_id.startswith('tt'):
        imdb_id = f"tt{imdb_id}"
    
    url = f"http://www.omdbapi.com/"
    params = {
        "apikey": OMDB_API_KEY,
        "i": imdb_id,
        "plot": "full"
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if response.status_code == 200 and data.get('Response') == 'True':
            return format_omdb_result(data)
    except Exception as e:
        print(f"Error searching by IMDB ID: {e}")
    
    return None

def search_by_tmdb_id(tmdb_id):
    """
    Search for a movie by TMDB ID
    """
    url = f"https://api.themoviedb.org/3/movie/{tmdb_id}"
    params = {
        "api_key": TMDB_API_KEY,
        "append_to_response": "credits"
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if response.status_code == 200 and data.get('id'):
            return format_tmdb_result(data, include_credits=True)
    except Exception as e:
        print(f"Error searching by TMDB ID: {e}")
    
    return None

def search_movies_by_keyword(query, page=1):
    """
    Search for movies by keyword/title using TMDB API
    Returns a list of movie results
    """
    url = f"https://api.themoviedb.org/3/search/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "query": query,
        "page": page,
        "include_adult": "false"
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if response.status_code == 200 and data.get('results'):
            results = []
            for movie_data in data['results']:
                formatted_result = format_tmdb_result(movie_data)
                if formatted_result:
                    results.append(formatted_result)
            return results
    except Exception as e:
        print(f"Error searching movies by keyword: {e}")
    
    return []

def format_tmdb_result(movie_data, include_credits=False):
    """
    Format TMDB API result into a standardized format
    """
    if not movie_data:
        return None
    
    # Get poster URL if available
    poster_url = None
    if movie_data.get('poster_path'):
        poster_url = f"https://image.tmdb.org/t/p/w500{movie_data['poster_path']}"
    
    # Get director and cast if credits are included
    directors = []
    cast = []
    
    if include_credits and movie_data.get('credits'):
        # Extract directors
        for crew_member in movie_data['credits'].get('crew', []):
            if crew_member.get('job') == 'Director':
                directors.append(crew_member.get('name'))
        
        # Extract top cast members
        for cast_member in movie_data['credits'].get('cast', [])[:5]:  # Get top 5 cast members
            cast.append(cast_member.get('name'))
    
    # Get genres
    genres = []
    for genre in movie_data.get('genres', []):
        if isinstance(genre, dict) and genre.get('name'):
            genres.append(genre.get('name'))
    
    # Create formatted result
    result = {
        'title': movie_data.get('title', ''),
        'release_year': int(movie_data.get('release_date', '').split('-')[0]) if movie_data.get('release_date') else None,
        'runtime_minutes': movie_data.get('runtime'),
        'synopsis': movie_data.get('overview', ''),
        'poster_url': poster_url,
        'imdb_id': movie_data.get('imdb_id'),
        'tmdb_id': str(movie_data.get('id')),
        'directors': directors,
        'cast': cast,
        'genres': genres,
        'found': True
    }
    
    # Add JSON data for form submission
    result['json_data'] = json.dumps(result)
    
    return result

def format_omdb_result(movie_data):
    """
    Format OMDB API result into a standardized format
    """
    if not movie_data or movie_data.get('Response') != 'True':
        return None
    
    # Get directors and cast
    directors = movie_data.get('Director', '').split(', ') if movie_data.get('Director') else []
    cast = movie_data.get('Actors', '').split(', ') if movie_data.get('Actors') else []
    
    # Get genres
    genres = movie_data.get('Genre', '').split(', ') if movie_data.get('Genre') else []
    
    # Parse runtime
    runtime_minutes = None
    if movie_data.get('Runtime'):
        try:
            runtime_str = movie_data.get('Runtime', '0 min').split(' ')[0]
            runtime_minutes = int(runtime_str) if runtime_str.isdigit() else None
        except:
            pass
    
    # Create formatted result
    result = {
        'title': movie_data.get('Title', ''),
        'release_year': int(movie_data.get('Year', '0').split('–')[0]) if movie_data.get('Year') else None,
        'runtime_minutes': runtime_minutes,
        'synopsis': movie_data.get('Plot', ''),
        'poster_url': movie_data.get('Poster') if movie_data.get('Poster') != 'N/A' else None,
        'imdb_id': movie_data.get('imdbID'),
        'directors': directors,
        'cast': cast,
        'genres': genres,
        'found': True
    }
    
    # Add JSON data for form submission
    result['json_data'] = json.dumps(result)
    
    return result
