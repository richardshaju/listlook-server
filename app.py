from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from serpapi import GoogleSearch
from dotenv import load_dotenv
import instaloader
import os
import tempfile
import re
import io
import base64

load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)