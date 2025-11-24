import instaloader

# Create an Instaloader instance
L = instaloader.Instaloader()

# (Optional) Log in if you need to download from private accounts or access certain features
# L.load_session_from_file("your_username", "session_file_path") # Load existing session
# L.login("your_username", "your_password") # Log in

# Method 1: Download a specific post by shortcode
post_shortcode = "DMGWWFPs1Ui"  # Replace with the actual post shortcode (from URL)
try:
    post = instaloader.Post.from_shortcode(L.context, post_shortcode)
    print(f"Downloading post: {post.shortcode}")
    print(f"Caption: {post.caption}")
    
    # Download the post
    L.download_post(post, target="downloads")
    
    # Save caption to a text file
    with open(f"downloads/{post.shortcode}_caption.txt", "w", encoding="utf-8") as f:
        f.write(f"Post URL: https://instagram.com/p/{post.shortcode}/\n")
        f.write(f"Caption: {post.caption}\n")
        f.write(f"Likes: {post.likes}\n")
        f.write(f"Date: {post.date}\n")
    
    print("Download completed successfully!")
    
except Exception as e:
    print(f"Error downloading post: {e}")

