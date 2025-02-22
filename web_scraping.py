import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import time
import random
import json

##########################
# Utility: Random User-Agent
##########################
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

##########################
# Extraction functions
##########################
def get_url_links_from_topic(topic):
    headers = get_random_headers()
    url = f"https://flipboard.com/search/{topic}"
    print("Fetching URL:", url)
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print("Error fetching URL:", e)
        exit()

    soup = BeautifulSoup(response.text, "html.parser")
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href not in links:
            links.append(href)
    # print("\nFound URLs on search page:")
    base_url = "https://flipboard.com/"
    topic_names = []
    url_links = []
    for link in links:
        if '/topic' in link:
            url_links.append(urljoin(base_url, link))
            # Slice off the initial characters to create a topic name (adjust as needed)
            topic_names.append(link[7:])
    # print("Topic Names:", topic_names)
    # print("Topic URLs:", url_links)

    # Create a dictionary that maps topic URL to topic name.
    link_topic_name = dict(zip(url_links, topic_names))
    print("Mapping:", link_topic_name)
    return (url_links, link_topic_name)

def get_article_urls_from_topic_url(topic_url):
    headers = get_random_headers()
    print("Fetching topic URL:", topic_url)
    try:
        response = requests.get(topic_url, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print("Error fetching topic URL:", e)
        exit()

    soup = BeautifulSoup(response.text, "html.parser")
    links = []
    list_a_tags = soup.find_all("a", href=True)
    for a in list_a_tags:
        href = a["href"]
        if href not in links:
            if '/topic/' in href and topic_url.split('/')[-1].lower() in href.lower() and len(href) > 30:
                links.append(href)
    # print("\nFound Article URLs (raw):", links)
    base_url = "https://flipboard.com/"
    article_urls = []
    for link in links:
        full_link = urljoin(base_url, link)
        # print(full_link)
        article_urls.append(full_link)
    
    return article_urls

def get_source_url(url):
    headers = get_random_headers()
    print("Fetching source from URL:", url)
    try:
        response = requests.get(url, headers=headers, timeout=10)
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
        response = requests.get(url, headers=headers, timeout=10)
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

##########################
# Main workflow
##########################
def main():
    # Define the topic(s) you want to process.
    topics = ["Tennis"]  # Extend this list as needed.
    result = []
    
    for topic in topics:
        # print(f"\nProcessing topic: {topic}")
        topic_url_links, topic_name_dict = get_url_links_from_topic(topic)
        print("Topic URL Links:", topic_url_links)
        print("Topic Name Dictionary:", topic_name_dict)
        # Process each topic URL
        count=0
        for topic_url in topic_url_links:
            count+=1
            print("topic_url",topic_url)
            topic_articles = []
            article_topic_name = topic_name_dict.get(topic_url, topic)
            print("article_topic_name",article_topic_name)
            # delay = random.uniform(5,8)
            # print(f"Waiting for {delay:.2f} seconds before fetching topic page.")
            # time.sleep(delay)
            
            article_urls = get_article_urls_from_topic_url(topic_url)
            print("Article URLs:", article_urls)
            # Process each article URL
            for article_url in article_urls:
                # delay = random.uniform(5, 10)
                # print(f"Waiting for {delay:.2f} seconds before processing article URL.")
                # time.sleep(delay)
                
                source_url = get_source_url(article_url)
                if not source_url:
                    print("Source URL not found for article:", article_url)
                    continue
                
                # delay = random.uniform(3, 5)
                # print(f"Waiting for {delay:.2f} seconds before fetching article text.")
                # time.sleep(delay)
                
                article_text = extract_article_text(source_url)
                topic_articles.append((source_url, article_text))
        
                # Use the topic name from the mapping (if available) from the first topic URL.
                # topic_name_extracted = topic_name_dict.get(topic_url_links[0], topic) if topic_url_links else topic
            result.append({
                "topic_name": article_topic_name,
                "url_content": topic_articles
            })
    
    # Write the final result to processed_articles.json
    with open("processed_articles.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)
    
    # print("\nFinal Result:")
    # print(json.dumps(result, indent=4))

if __name__ == "__main__":
    start_time = time.time()    
    main()
    end_time = time.time()
    print(f"\nTotal time taken: {end_time - start_time:.2f} seconds.")
