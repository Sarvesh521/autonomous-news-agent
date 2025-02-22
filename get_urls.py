import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def get_google_news_urls(topic):
    base_url = "https://news.google.com"
    search_url = f"{base_url}/search?q={topic}&hl=en-US&gl=US&ceid=US:en"
    print("Fetching search results from:", search_url)
    headers = {
            "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/115.0.0.0 Safari/537.36")
            }
    response = requests.get(search_url, headers=headers)
    print("response:", response)
    print("response.status_code:", response.status_code)
    if response.status_code != 200:
        print("Error: Unable to fetch the page")
        return []
    print("Successfully fetched the page")
    soup = BeautifulSoup(response.text, "html.parser")
    urls=[]
    urls_dict = {}
    for a in soup.find_all("a"):
        href = a.get("href")
        class_name = a.get("class")
        if class_name is not None:
            class_name = " ".join(class_name)
        if href:
            url_added = urljoin(base_url, href)
            if "https://news.google.com/read" in url_added:
                urls.append(url_added)
                if class_name is not None:
                    if class_name in urls_dict:
                        urls_dict[class_name].append(urljoin(base_url, href))
                    else:
                        urls_dict[class_name] = [urljoin(base_url, href)]
            
    return (urls, urls_dict)

news_urls = get_google_news_urls("football")
urls = list(set(news_urls[0]))
print("urls:", urls)
if len(urls)>10:
    urls = urls[:10]
print("urls:", urls)