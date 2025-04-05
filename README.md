# Movie Collection App with Barcode Scanner

A Flask-based web application for managing your personal movie collection, with barcode scanning capabilities.

## Features

- **Barcode Scanning**: Scan movie barcodes using your webcam or mobile camera
- **Movie Search**: Search for movies by title, UPC, ISBN, IMDb ID, or TMDb ID
- **Collection Management**: Organize movies into custom collections
- **CSV Import/Export**: Bulk import movies using CSV files
- **Media Information**: Store comprehensive movie details including cast, genres, and more

## Technology Stack

- **Backend**: Python with Flask framework
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Barcode Scanning**: html5-qrcode.js library

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/movie-collection-scanner.git
   cd movie-collection-scanner
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Initialize the database:
   ```
   flask init-db
   ```

5. Run the application:
   ```
   python app.py
   ```

6. Access the application in your browser:
   ```
   http://127.0.0.1:5000
   ```

## Barcode Scanning

The app supports scanning movie barcodes (UPC/ISBN) using:
- Webcam on desktop/laptop computers
- Camera on mobile devices

Simply navigate to the "Scan Barcode" page in the app, grant camera permissions, and point your camera at a movie barcode.

## API Keys

To enable movie lookup by barcode, you need to obtain API keys for:
- The Movie Database (TMDb): https://www.themoviedb.org/documentation/api
- Open Movie Database (OMDb): https://www.omdbapi.com/apikey.aspx

Update these keys in the `search_utils.py` file.

## License

MIT License
