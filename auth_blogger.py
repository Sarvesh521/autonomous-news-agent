import json
import httplib2
import time
import random
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run_flow
from googleapiclient import discovery

BLOG_ID = '8510639159580300368'  # Change this to your blog ID

# Start the OAuth flow to retrieve credentials
def authorize_credentials():
    CLIENT_SECRET = 'client_secrets.json'
    SCOPE = 'https://www.googleapis.com/auth/blogger'
    STORAGE = Storage('credentials.storage')

    credentials = STORAGE.get()

    if not credentials or credentials.invalid:
        flow = flow_from_clientsecrets(CLIENT_SECRET, scope=SCOPE)
        http = httplib2.Http()
        credentials = run_flow(flow, STORAGE, http=http)
    
    if credentials.access_token_expired:
        print("🔄 Refreshing expired token...")
        credentials.refresh(httplib2.Http())

    return credentials


def getBloggerService():
    credentials = authorize_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://blogger.googleapis.com/$discovery/rest?version=v3')
    service = discovery.build('blogger', 'v3', http=http, discoveryServiceUrl=discoveryUrl)
    return service

def postToBlogger(payload):
    service = getBloggerService()
    post = service.posts()
    insert = post.insert(blogId=BLOG_ID, body=payload).execute()
    print(f"✅ Posted: {insert['title']} (URL: {insert['url']})")
    return insert

def postFromJson():
    with open("summarized_articles.json", "r", encoding="utf-8") as file:
        posts_data = json.load(file)

    for entry in posts_data:
        # Check for missing or empty fields
        if not all(entry.get(field) and entry[field].strip() for field in ["title", "summary", "location"]):
            print(f"⚠️ Skipping entry due to missing fields: {entry}")
            continue

        title = entry["title"].strip()
        content = entry["summary"].strip()

        payload = {
            "kind": "blogger#post",
            "title": title,
            "content": content,
            "contentFormat": "html",
            "labels": [entry["location"]]
        }
        
        postToBlogger(payload)

        # 🔹 Random delay to prevent bans (30-90 seconds)
        print(f"⏳ Waiting 20 seconds before next post...")
        time.sleep(20)

# 🔹 New Function: Post a single dictionary entry
def postSingleEntry(entry):
    if not all(entry.get(field) and entry[field].strip() for field in ["title", "summary", "location"]):
        print(f"⚠️ Skipping entry due to missing fields: {entry}")
        return None

    title = entry["title"].strip()
    content = entry["summary"].strip()

    payload = {
        "kind": "blogger#post",
        "title": title,
        "content": content,
        "contentFormat": "html",
        "labels": [entry["location"]]
    }
    
    return postToBlogger(payload)

# 🔴 New Function: Delete a Post
def deletePost(post_id):
    """Deletes a post from Blogger using its post_id."""
    service = getBloggerService()
    try:
        service.posts().delete(blogId=BLOG_ID, postId=post_id).execute()
        print(f"🗑️ Deleted post with ID: {post_id}")
    except Exception as e:
        print(f"❌ Error deleting post: {str(e)}")

# Example Usage:
# deletePost("POST_ID_HERE")  # Replace with the actual post ID

def dump_posts_to_json():
    """Fetch all posts and save them to a JSON file."""
    service = getBloggerService()
    
    try:
        posts = service.posts().list(blogId=BLOG_ID, fetchBodies=False).execute()
        post_list = []

        for post in posts.get("items", []):
            post_list.append({
                "id": post["id"],
                "title": post["title"],
                "url": post["url"],
                "published": post["published"]
            })

        with open("blog_posts.json", "w", encoding="utf-8") as json_file:
            json.dump(post_list, json_file, ensure_ascii=False, indent=4)

        print("✅ Blog posts dumped to 'blog_posts.json'")

    except Exception as e:
        print(f"❌ Error fetching posts: {str(e)}")

