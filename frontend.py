import streamlit as st
import asyncio
import concurrent.futures
import time
import json

def get_scraped_data(topic):
    time.sleep(10)
    return f"Scraped data for {topic}"

def get_articles(scraped_json):
    time.sleep(10)
    with open("summarized_articles.json", "r") as f:
        articles = json.load(f)
    return articles

async def main():
    st.title("Streamlit App")
    topic = st.text_input("Enter a topic to scrape")
    #submit button
    if st.button("Process"):
        loop = asyncio.get_running_loop()
        st.write("Scraping data...")
        with concurrent.futures.ThreadPoolExecutor() as pool:
            result = await loop.run_in_executor(pool, get_scraped_data, topic)
            st.write("Data scraped for", topic)
            st.write("Processing articles...")
            result = await loop.run_in_executor(pool, get_articles, result)
            st.write("Articles processed for", topic)
            st.write(result)


    
if __name__ == '__main__':
    asyncio.run(main())
    

    



