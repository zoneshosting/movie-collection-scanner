#!/bin/bash

# Initialize the database
echo "Initializing database..."
cd /home/ubuntu/movie_collection_site
export FLASK_APP=app.py
flask init-db

# Run the application
echo "Starting the movie collection application..."
python3 app.py
