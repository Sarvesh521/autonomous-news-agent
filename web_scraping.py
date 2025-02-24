import sys
import requests
import json
import random
import re
import time
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import argparse
from urllib.parse import quote

SCRAPER_OUTPUT_FILE = "processed_articles.json"
MAX_ARTICLES_PER_SUBTOPIC = 4
MAX_NO_OF_SUBTOPICS = 5

def get_random_headers():
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/90.0.818.42",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPad; CPU OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1"
    ]
    return {"User-Agent": random.choice(user_agents)}

def get_url_links_from_topic(topic):
    headers = get_random_headers()
    topic = quote(topic)
    url = f"https://flipboard.com/search/{topic}"
    print("Fetching URL:", url)
    try:
        response = requests.get(url, headers=headers, timeout=1000)
        response.raise_for_status()
    except Exception as e:
        print("Error fetching URL:", e)
        return ([], {})

    soup = BeautifulSoup(response.text, "html.parser")
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href not in links:
            links.append(href)
    base_url = "https://flipboard.com/"
    topic_names = []
    url_link = ""
    print("Links:", links)
    keyword=""
    for link in links:
        if '/@' in link:
            # url_links.append(urljoin(base_url, link))
            url_link = urljoin(base_url, link)
            keyword=link
            # Create a topic name by slicing off the first few characters; adjust as needed.
            break
    
    return (keyword,url_link)
    


def get_article_urls_from_topic_url(topic_url,keyword):
    headers = get_random_headers()
    print("Fetching topic URL:", topic_url)
    try:
        response = requests.get(topic_url, headers=headers, timeout=1000)
        response.raise_for_status()
    except Exception as e:
        print("Error fetching topic URL:", e)
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    links = []
    list_a_tags = soup.find_all("a", href=True)
    # print("List of a tags:", list_a_tags)
    # return list_a_tags
    for a in list_a_tags:
        href = a["href"]
        if href not in links:
            links.append(href)
    base_url = "https://flipboard.com"
    # base_url = base_url + keyword
    print("Base URL:", base_url)
    article_urls = []
    for link in links:
        full_link = urljoin(base_url, link)
        article_urls.append(full_link)
    check_url = base_url + keyword
    need_urls = []
    for article_url in article_urls:
        if check_url in article_url:
            need_urls.append(article_url)
    return need_urls

def get_source_url(url):
    headers = get_random_headers()
    print("Fetching source from URL:", url)
    try:
        response = requests.get(url, headers=headers, timeout=1000)
        response.raise_for_status()
    except Exception as e:
        print("Error fetching URL:", e)
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    script_tags = soup.find_all("script")
    for script_tag in script_tags:
        if 'sourceURL' in str(script_tag):
            match = re.search(r'"sourceURL":"(.*?)"', str(script_tag))
            if match:
                source_url = match.group(1)
                return source_url
    return None

def extract_article_text(url):
    headers = get_random_headers()
    print("Extracting article text from:", url)
    try:
        response = requests.get(url, headers=headers, timeout=1000)
        response.raise_for_status()
    except Exception as e:
        print("Error fetching article text from URL:", e)
        return ""
    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style", "header", "footer", "nav", "aside", "noscript"]):
        tag.decompose()
    article = soup.find("article")
    if article:
        text = article.get_text(separator="\n")
    else:
        text = soup.get_text(separator="\n")
    lines = [line.strip() for line in text.splitlines()]
    clean_text = "\n".join(line for line in lines if line)
    return clean_text

def main(topic,MAX_ARTICLES_PER_SUBTOPIC,MAX_NO_OF_SUBTOPICS):
    result=[]
    (keyword,topic_url) = get_url_links_from_topic(topic)
    print("Keyword:", keyword)
    print("Topic URL:", topic_url)
    article_urls = get_article_urls_from_topic_url(topic_url,keyword)
    print("Article URLs:", article_urls)
    print("Number of articles:", len(article_urls))
    print("Article URLs:", article_urls)
    for article_url in article_urls:
        source_url = get_source_url(article_url)
        if not source_url:
            print("Source URL not found for article:", article_url)
            continue
        article_text = extract_article_text(source_url)
        if article_text!="":
            result.append({
                "url": source_url,
                "url_content": article_text
            })
    print("Result:", result)

    try:
        with open(SCRAPER_OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=4, ensure_ascii=False)
        print("Web scraping completed successfully. Data written to", SCRAPER_OUTPUT_FILE)
        return result
    #test
    except Exception as e:
        print("Error writing JSON file:", e)

if __name__ == "__main__":
    topic = "Football"
    start_time = time.time()
    main(topic, MAX_ARTICLES_PER_SUBTOPIC, MAX_NO_OF_SUBTOPICS)
    end_time = time.time()
    print(f"\nTotal time taken: {end_time - start_time:.2f} seconds.")