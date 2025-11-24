from flask import Flask, jsonify, request, send_file, send_from_directory
from flask_cors import CORS
from serpapi import GoogleSearch
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from flask_apscheduler import APScheduler
import instaloader
import os
import tempfile
import re
import io
import base64
import shutil
import time

load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize scheduler
scheduler = APScheduler()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

L = instaloader.Instaloader(
            download_videos=False,
            download_video_thumbnails=False,
            download_comments=False,
            save_metadata=False,
            compress_json=False
        )

username = os.environ.get("INSTA_USERNAME")
if username:
    L.load_session_from_file(username=os.environ.get("INSTA_USERNAME"), filename=os.environ.get("INSTA_SESSIONFILE"))

    if getattr(L.context, "is_logged_in", False):
        print("Instaloader login successful for user", username)
    else:
        print("Instaloader login failed for user", username)


@app.route('/')
def home():
    """Home route"""
    return jsonify({
        "message": "Welcome to ListaLook Server!",
        "status": "running",
        "version": "1.0.0"
    })

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": "2025-11-23"
    })

@app.route('/api/instagram/download', methods=['POST'])
def download_instagram_image():
    """Download Instagram image from provided link and return image with caption"""
    try:
        data = request.get_json()
        
        if not data or 'instagram_url' not in data:
            return jsonify({"error": "Instagram URL is required"}), 400
        
        instagram_url = data['instagram_url']
        
        # Validate Instagram URL
        if not is_valid_instagram_url(instagram_url):
            return jsonify({"error": "Invalid Instagram URL"}), 400
        
        # Extract shortcode from URL
        shortcode = extract_shortcode(instagram_url)
        if not shortcode:
            return jsonify({"error": "Could not extract post ID from URL"}), 400
        
        # Download image using instaloader
       
        # Download the post
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        
        # Extract post information (like in test.py)
        post_info = {
            "shortcode": post.shortcode,
            "caption": post.caption if post.caption else "",
            "likes": post.likes,
            "date": post.date.isoformat() if post.date else None,
            "post_url": f"https://instagram.com/p/{post.shortcode}/"
        }
        
        # Get the image URL (first image if multiple)
        image_url = post.url if hasattr(post, 'url') else None
        
        # Return JSON response with image and caption
        response_data = {
            "success": True,
            "post_info": post_info,
            "image_url": image_url,
            "message": "Instagram post data retrieved successfully"
        }
        
        return jsonify(response_data), 200
                
    except instaloader.exceptions.PostUnavailableException:
        return jsonify({"error": "Instagram post is not available or private"}), 404
    except instaloader.exceptions.LoginRequiredException:
        return jsonify({"error": "Login required to access this content"}), 401
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/api/search/instagram', methods=['POST'])
def search_instagram_route():
    """Search Instagram image using Google Lens"""
    data = request.get_json()
    
    if not data or 'instagram_url' not in data:
        return jsonify({"error": "Instagram URL is required"}), 400
    
    result = search_instagram(data['instagram_url'])
    
    if "error" in result and "search_metadata" not in result:
         return jsonify(result), 400
        
    return jsonify(result), 200

def search_instagram(instagram_url):
    """
    Get image of a post from instagram and pass it to Google Lens search
    """
    try:
        # Validate Instagram URL
        if not is_valid_instagram_url(instagram_url):
            return {"error": "Invalid Instagram URL"}
        
        # Extract shortcode from URL
        shortcode = extract_shortcode(instagram_url)
        if not shortcode:
            return {"error": "Could not extract post ID from URL"}
        
        # Download image using instaloader
        L = instaloader.Instaloader(
            download_videos=False,
            download_video_thumbnails=False,
            download_comments=False,
            save_metadata=False,
            compress_json=False
        )
       
        # Get the post
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        
        # Get the image URL
        image_url = post.url
        
        if not image_url:
             return {"error": "Could not retrieve image from Instagram post"}

        # Search using SerpApi
        if not os.environ.get("SERPAPI_API_KEY"):
            return {"error": "SERPAPI_API_KEY not set in environment"}

        params = {
          "engine": "google_lens",
          "url": image_url,
          "type": "products",
          "api_key": os.environ.get("SERPAPI_API_KEY")
        }

        search = GoogleSearch(params)
        results = search.get_dict()
        return results

    except instaloader.exceptions.PostUnavailableException:
        return {"error": "Instagram post is not available or private"}
    except instaloader.exceptions.LoginRequiredException:
        return {"error": "Login required to access this content"}
    except Exception as e:
        return {"error": f"Error: {str(e)}"}

def is_valid_instagram_url(url):
    """Validate if the URL is a valid Instagram URL"""
    instagram_patterns = [
        r'https?://(?:www\.)?instagram\.com/p/([A-Za-z0-9_-]+)/?',
        r'https?://(?:www\.)?instagram\.com/reel/([A-Za-z0-9_-]+)/?',
        r'https?://(?:www\.)?instagram\.com/tv/([A-Za-z0-9_-]+)/?'
    ]
    
    for pattern in instagram_patterns:
        if re.match(pattern, url):
            return True
    return False

def extract_shortcode(url):
    """Extract shortcode from Instagram URL"""
    patterns = [
        r'instagram\.com/p/([A-Za-z0-9_-]+)',
        r'instagram\.com/reel/([A-Za-z0-9_-]+)',
        r'instagram\.com/tv/([A-Za-z0-9_-]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Upload file endpoint"""
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
        
    if file and allowed_file(file.filename):
        # Generate unique filename using timestamp
        original_filename = secure_filename(file.filename)
        extension = original_filename.rsplit('.', 1)[1].lower()
        filename = f"{int(time.time() * 1000)}.{extension}"
        
        # Ensure upload directory exists
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
            
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        return jsonify({
            "message": "File uploaded successfully", 
            "filename": filename,
            "path": file_path
        }), 201
        
    return jsonify({"error": "File type not allowed. Only images are allowed."}), 400

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

def cleanup_uploads():
    """Delete all files in uploads folder"""
    folder = app.config['UPLOAD_FOLDER']
    if os.path.exists(folder):
        print(f"Cleaning up uploads folder: {folder}")
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')
        print("Uploads folder cleaned up.")

@app.route('/api/search/image', methods=['POST'])
def search_image_route():
    """Search using uploaded image via Google Lens"""
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
        
    if file and allowed_file(file.filename):
        # Generate unique filename using timestamp
        original_filename = secure_filename(file.filename)
        extension = original_filename.rsplit('.', 1)[1].lower()
        filename = f"{int(time.time() * 1000)}.{extension}"
        
        # Ensure upload directory exists
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
            
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Construct public URL (Note: This requires the server to be publicly accessible)
        # If running locally, you might need a tunnel like ngrok
        image_url = request.host_url + 'uploads/' + filename
        
        # Search using SerpApi
        if not os.environ.get("SERPAPI_API_KEY"):
            return jsonify({"error": "SERPAPI_API_KEY not set in environment"}), 500

        try:
            params = {
              "engine": "google_lens",
              "url": image_url,
              "type": "products",
              "api_key": os.environ.get("SERPAPI_API_KEY")
            }

            search = GoogleSearch(params)
            results = search.get_dict()
            
            if "error" in results:
                 return jsonify(results), 400
                 
            return jsonify(results), 200
            
        except Exception as e:
            return jsonify({"error": f"Search failed: {str(e)}"}), 500
        
    return jsonify({"error": "File type not allowed. Only images are allowed."}), 400

if __name__ == '__main__':
    # Create uploads folder if it doesn't exist
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    # Schedule cleanup job to run every day at 12:00 AM
    scheduler.add_job(id='cleanup_task', func=cleanup_uploads, trigger='cron', hour=0, minute=0)
    scheduler.init_app(app)
    scheduler.start()
    
    app.run(debug=True, host='0.0.0.0', port=os.environ.get('PORT', 8080))