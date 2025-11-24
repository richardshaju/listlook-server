# ListaLook Server

A Flask-based REST API server for the ListaLook application.

## Features

- RESTful API endpoints
- CORS enabled for cross-origin requests
- Health check endpoint
- Sample data endpoints (GET and POST)
- JSON responses

## Setup

1. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the server:
   ```bash
   python app.py
   ```

The server will start on `http://localhost:5000`

## API Endpoints

- `GET /` - Welcome message
- `GET /health` - Health check
- `GET /api/data` - Get sample data
- `POST /api/data` - Create new data

## Development

The server runs in debug mode by default, which means:
- Auto-reload on file changes
- Detailed error messages
- Debug toolbar available

## Environment Variables

You can create a `.env` file to store environment variables:

```
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=your-secret-key-here
```