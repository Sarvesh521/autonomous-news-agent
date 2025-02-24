import json
import streamlit as st
from googleapiclient import discovery
from auth_blogger import getBloggerService,dump_posts_to_json

dump_posts_to_json()

BLOG_ID = '8510639159580300368'

# Function to load posts from JSON
def load_posts():
    try:
        with open("blog_posts.json", "r", encoding="utf-8") as json_file:
            return json.load(json_file)
    except FileNotFoundError:
        return []

# Function to save updated posts to JSON
def save_posts(posts):
    with open("blog_posts.json", "w", encoding="utf-8") as json_file:
        json.dump(posts, json_file, ensure_ascii=False, indent=4)

# Function to delete a post
def delete_post(post_id):
    service = getBloggerService()
    try:
        service.posts().delete(blogId=BLOG_ID, postId=post_id).execute()
        
        # Remove the post from JSON file
        posts = load_posts()
        updated_posts = [post for post in posts if post["id"] != post_id]
        save_posts(updated_posts)
        
        st.success(f"✅ Post {post_id} deleted successfully!")
        st.rerun()

    except Exception as e:
        st.error(f"❌ Error deleting post: {str(e)}")

# Streamlit UI
st.title("📝 Blogger Post Manager")

posts = load_posts()

if posts:
    for post in posts:
        with st.expander(f"{post['title']}"):
            st.write(f"📌 **Location:** {post.get('location', 'N/A')}")
            st.write(f"📖 **Summary:** {post.get('summary', 'N/A')}")
            st.write(f"🔗 [View Post]({post['url']})")
            st.write(f"📅 **Published:** {post['published']}")
            if st.button(f"❌ Delete Post {post['id']}", key=post['id']):
                delete_post(post['id'])
else:
    st.warning("⚠️ No posts found. Run `dump_posts_to_json()` first.")
