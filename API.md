# ListaLook Server API Documentation

Base URL: `http://localhost:8080`

## General Endpoints

### 1. Home
Returns a welcome message and server status.

- **URL:** `/`
- **Method:** `GET`
- **Success Response:**
  - **Code:** 200 OK
  - **Content:**
    ```json
    {
      "message": "Welcome to ListaLook Server!",
      "status": "running",
      "version": "1.0.0"
    }
    ```

### 2. Health Check
Checks if the server is running and healthy.

- **URL:** `/health`
- **Method:** `GET`
- **Success Response:**
  - **Code:** 200 OK
  - **Content:**
    ```json
    {
      "status": "healthy",
      "timestamp": "2025-11-23"
    }
    ```

## Data Endpoints

### 3. Get Sample Data
Retrieves a list of sample items.

- **URL:** `/api/data`
- **Method:** `GET`
- **Success Response:**
  - **Code:** 200 OK
  - **Content:**
    ```json
    {
      "data": [
        {"id": 1, "name": "Item 1", "description": "First item"},
        ...
      ],
      "count": 3
    }
    ```

### 4. Create Data
Creates a new data item (Mock endpoint).

- **URL:** `/api/data`
- **Method:** `POST`
- **Headers:** `Content-Type: application/json`
- **Body:**
  ```json
  {
    "name": "New Item",
    "description": "Description here"
  }
  ```
- **Success Response:**
  - **Code:** 201 Created
  - **Content:**
    ```json
    {
      "message": "Data created successfully",
      "received_data": { ... }
    }
    ```

## Instagram Endpoints

### 5. Download Instagram Image
Downloads an image from an Instagram post URL and returns metadata.

- **URL:** `/api/instagram/download`
- **Method:** `POST`
- **Headers:** `Content-Type: application/json`
- **Body:**
  ```json
  {
    "instagram_url": "https://www.instagram.com/p/CxamplePost/"
  }
  ```
- **Success Response:**
  - **Code:** 200 OK
  - **Content:**
    ```json
    {
      "success": true,
      "post_info": {
        "shortcode": "CxamplePost",
        "caption": "Post caption...",
        "likes": 100,
        "date": "2023-11-23T12:00:00",
        "post_url": "https://instagram.com/p/CxamplePost/"
      },
      "image_url": "https://instagram.fmaa1-1.fna.fbcdn.net/...",
      "message": "Instagram post data retrieved successfully"
    }
    ```
- **Error Responses:**
  - 400 Bad Request: Invalid URL or missing parameter.
  - 404 Not Found: Post unavailable or private.

### 6. Search Instagram Image (Google Lens)
Fetches an Instagram post image and searches for products using Google Lens (via SerpApi).

- **URL:** `/api/search/instagram`
- **Method:** `POST`
- **Headers:** `Content-Type: application/json`
- **Body:**
  ```json
  {
    "instagram_url": "https://www.instagram.com/p/CxamplePost/"
  }
  ```
- **Success Response:**
  - **Code:** 200 OK
  - **Content:** Returns the raw JSON response from SerpApi (Google Lens results).
- **Requirements:** `SERPAPI_API_KEY` must be set in `.env`.

## File Upload Endpoints

### 7. Upload File
Uploads an image file to the server. Files are automatically deleted at midnight.

- **URL:** `/api/upload`
- **Method:** `POST`
- **Body:** `multipart/form-data`
  - `file`: The image file to upload (Allowed extensions: png, jpg, jpeg, gif).
- **Success Response:**
  - **Code:** 201 Created
  - **Content:**
    ```json
    {
      "message": "File uploaded successfully",
      "filename": "1700956800123.jpg",
      "path": "uploads/1700956800123.jpg"
    }
    ```
- **Error Responses:**
  - 400 Bad Request: No file selected or invalid file type.

### 8. Serve Uploaded File
Access an uploaded file.

- **URL:** `/uploads/<filename>`
- **Method:** `GET`
- **Example:** `http://localhost:8080/uploads/1700956800123.jpg`

### 9. Search Uploaded Image (Google Lens)
Uploads an image and searches for products using Google Lens (via SerpApi).

- **URL:** `/api/search/image`
- **Method:** `POST`
- **Body:** `multipart/form-data`
  - `file`: The image file to upload (Allowed extensions: png, jpg, jpeg, gif).
- **Success Response:**
  - **Code:** 200 OK
  - **Content:** Returns the raw JSON response from SerpApi (Google Lens results).
- **Requirements:**
  - `SERPAPI_API_KEY` must be set in `.env`.
  - The server must be publicly accessible (e.g., via ngrok) for SerpApi to access the uploaded image URL.
- **Error Responses:**
  - 400 Bad Request: No file selected or invalid file type.
  - 500 Internal Server Error: Search failed or API key missing.
