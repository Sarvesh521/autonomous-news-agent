import os
import json
from dotenv import load_dotenv
import requests

load_dotenv()

api_key = os.getenv("NEWS_API_KEY")
if not api_key:
    raise ValueError("No API key found. Please set NEWS_API_KEY in your environment.")

GLOBALS = {
    'output_filename': 'articles.json',
    'topic': 'football', #Change this to your desired topic
    'from_date': '2025-01-21', #Adjust the date as needed
    'sort_by': 'publishedAt', #Options include: relevancy, popularity, publishedAt
}

def get_articles(query, from_date, sort_by, api_key):
    url = f"https://newsapi.org/v2/everything?q={query}&from={from_date}&sortBy={sort_by}&apiKey={api_key}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        data = response.json()
        if data.get('status') != 'ok':
            print("Error from NewsAPI:", data)
            return []
        return data.get('articles', [])
    except requests.RequestException as e:
        print("Error during API call:", e)
        return []


articles = get_articles(GLOBALS["topic"], GLOBALS['from_date'], GLOBALS["sort_by"] , api_key)

if not articles:
    print("No articles found.")
else:
    articles_to_save = []
    for i, article in enumerate(articles, start=1):
        articles_to_save.append({
            "Article Number": i,
            "Source": article.get("source", {}).get("name", "No Source"),
            # "Author": article.get("author", "No Author"),
            "Title": article.get("title", "No Title"),
            "Description": article.get("description", ""),
            "URL": article.get("url", "No URL"),
            # "Published At": article.get("publishedAt", "No Published Date"),
            "Content": article.get("content", "No Content Available")
        })
        
    # Write the output to a JSON file
    with open(GLOBALS["output_filename"], "w", encoding="utf-8") as f:
        json.dump(articles_to_save, f, indent=4)
    
    print(f"Articles successfully written to {GLOBALS['output_filename']}.")