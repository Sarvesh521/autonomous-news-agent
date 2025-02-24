import json
import httplib2
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run_flow
from googleapiclient import discovery

# Start the OAuth flow to retrieve credentials
def authorize_credentials():
    CLIENT_SECRET = 'client_secret.json'
    SCOPE = 'https://www.googleapis.com/auth/blogger'
    STORAGE = Storage('credentials.storage')
    
    credentials = STORAGE.get()
    if credentials is None or credentials.invalid:
        flow = flow_from_clientsecrets(CLIENT_SECRET, scope=SCOPE)
        http = httplib2.Http()
        credentials = run_flow(flow, STORAGE, http=http)
    
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
    insert = post.insert(blogId='711424663010730438', body=payload).execute()
    print(f"✅ Posted: {insert['title']} (URL: {insert['url']})")
    return insert

def postFromJson():
    with open("summarized_articles.json", "r", encoding="utf-8") as file:
        posts_data = json.load(file)

    for entry in posts_data:
        title = entry["title"].strip()  
        content = entry["summary"].strip()  

        payload = {
            "kind": "blogger#post",
            "title": title,
            "content": content,
            "contentFormat": "html",
            "labels": [entry["topic_name"]]
        }
        postToBlogger(payload)

# 🔹 New Function: Post a single dictionary entry
def postSingleEntry(entry):
    title = entry["title"].strip()
    content = entry["summary"].strip()

    payload = {
        "kind": "blogger#post",
        "title": title,
        "content": content,
        "contentFormat": "html",
        "labels": [entry["topic_name"]]
    }
    
    return postToBlogger(payload)

# Example Usage:
# sample_post = {
#     "title": "Sample Blog Post",
#     "summary": "<p>This is a sample post with HTML content.</p>",
#     "topic_name": "Tech"
# }
# postSingleEntry(sample_post)
