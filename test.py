from dotenv import load_dotenv
import instaloader

# Create an Instaloader instance
L = instaloader.Instaloader()

# (Optional) Log in if you need to download from private accounts or access certain features
# L.load_session_from_file()
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



# from serpapi import GoogleSearch
# import os
# load_dotenv()

# params = {
#   "engine": "google_lens",
#   "url": "https://encrypted-tbn2.gstatic.com/shopping?q=tbn:ANd9GcTNqv8-gkEnfOU9oEkd3ypdsg31032I2Mz4qMjbPL9ihTmUaabRt3ust__XHl7sFBUP5LLN9u2z980JuPJDicT_Pun9SOR9NcdsQ1G7rSIOOjX2KbCfXQZyQFuengVgDphozAwZtgSa&usqp=CAc",
#   "type": "products",
#   "api_key": os.environ["SERPAPI_API_KEY"]
# }

# search = GoogleSearch(params)
# results = search.get_dict()
# for product in results.get("products_results", []):
#     title = product.get("title", "No title")
#     price = product.get("price", "No price")
#     link = product.get("link", "No link")
#     print(f"Title: {title}\nPrice: {price}\nLink: {link}\n")