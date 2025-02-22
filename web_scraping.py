import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import get_urls as get_urls
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def is_paywalled(html_text, url=None):
    paywall_keywords = ["pay wall", "paywall", "pay-wall"]
    lower_text = html_text.lower()
    for keyword in paywall_keywords:
        if keyword in lower_text:
            print("Paywall keyword found:", keyword)
            return True
    try:
        soup = BeautifulSoup(html_text, 'html.parser')
        scripts = soup.find_all("script", type="application/ld+json")
        for script in scripts:
            try:
                json_data = json.loads(script.string)
                def check_json(data):
                    if isinstance(data, dict):
                        if 'isAccessibleForFree' in data:
                            accessible = str(data['isAccessibleForFree']).lower()
                            if accessible in ['false', 'no']:
                                return True
                        if 'hasPart' in data:
                            part = data['hasPart']
                            if isinstance(part, dict) and 'isAccessibleForFree' in part:
                                accessible = str(part['isAccessibleForFree']).lower()
                                if accessible in ['false', 'no']:
                                    return True
                            elif isinstance(part, list):
                                for item in part:
                                    if isinstance(item, dict) and 'isAccessibleForFree' in item:
                                        accessible = str(item['isAccessibleForFree']).lower()
                                        if accessible in ['false', 'no']:
                                            return True
                    return False

                if isinstance(json_data, dict) and check_json(json_data):
                    return True
                elif isinstance(json_data, list):
                    for item in json_data:
                        if check_json(item):
                            return True
            except Exception:
                continue
    except Exception:
        pass

    if url:
        try:
            headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"}
            parsed_url = urlparse(url)
            if not parsed_url.scheme:
                url = "https://" + url
            response = requests.get(url, headers=headers, timeout=10)
            googlebot_html = response.text.lower()
            for keyword in paywall_keywords:
                if keyword in googlebot_html:
                    return True
        except Exception:
            pass

    return False

# def extract_text_from_html(html):
#     soup = BeautifulSoup(html, "html.parser")
#     for tag in soup(["script", "style", "noscript"]):
#         tag.decompose()
#     text = soup.get_text(separator=" ")
#     return ' '.join(text.split())


def extract_title_and_text_with_selenium(url):
    """
    Uses Selenium (with a headless browser) to extract the full article text and title.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--blink-settings=imagesEnabled=false")  # Disables images

    # Disable images, stylesheets, and plugins via preferences.
    prefs = {
        "profile.managed_default_content_settings.images": 2,
        "profile.managed_default_content_settings.stylesheets": 2,
        "profile.managed_default_content_settings.plugins": 2
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    driver = webdriver.Chrome(options=chrome_options)
    try:
        driver.get(url)
        # Wait a bit for dynamic content to load.
        time.sleep(3)
        html = driver.page_source
    except Exception as e:
        print(f"Selenium error: {e}")
        html = ""
    finally:
        driver.quit()
    
    soup = BeautifulSoup(html, "html.parser")
    
    # Extract title from the <title> tag.
    title_tag = soup.find("title")
    title_text = title_tag.get_text().strip() if title_tag else ""
    
    for tag in soup(["script", "style", "noscript", "header", "footer", "nav", "iframe"]):
        tag.decompose()
    
    text = soup.get_text(separator=" ")
    clean_text = " ".join(text.split())
    
    return title_text, clean_text, html

def process_articles():
    count=0
    paywall_urls = []
    articles=[]
    
    for url in get_urls.urls: 
        count+=1
        print(count)
        article={}
        article["url"]=url
        title, text, html_text = extract_title_and_text_with_selenium(url)
        article["title"]=title
        article["extracted_content"]=text
        
        if is_paywalled(html_text, url):
            paywall_urls.append(url)
            article["extracted_content"] = "Paywalled article. Extraction skipped."
        
        if "About this page Our systems have detected unusual traffic from your computer network." in text:
            article["extracted_content"] = "Detected as a bot. Extraction skipped."
        articles.append(article)
    
    print("\nPaywall URLs:")
    for url in paywall_urls:
        print(url)

    print("Len of Paywall URLs: ", len(paywall_urls))
    print("Total Articles: ", count)
    if count > 0:
        print("Paywall Percentage: ", (len(paywall_urls)/count)*100)
    
    with open("articles.json", "w") as f:
        json.dump(articles, f, indent=4)

process_articles()