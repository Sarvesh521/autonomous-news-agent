import streamlit as st
import asyncio
import concurrent.futures
import time
import json

def get_scraped_data(topic):
    time.sleep(2)
    return f"Scraped data for {topic}"

def get_articles(scraped_json):
    time.sleep(2)
    with open("summarized_articles.json", "r") as f:
        articles = json.load(f)
    return articles

def check_buttons(buttons, articles):
    for i in range(len(buttons)):
        if buttons[i]:
            st.write(f"Article {articles[i]['title']} posted")
    return articles

def post_article(article):
    print(f"Article {article['title']} posted")
    st.write(f"Article {article['title']} posted")

def process(topic):
    result = get_scraped_data(topic)
    st.write("Data scraped for", topic)
    st.write("Processing articles...")
    result = get_articles(result)
    st.write("Articles processed for", topic)
    st.divider()
    st.header("Articles")
    st.divider()

    articles_topic = dict()
    for article in result:
        if article["topic_name"] not in articles_topic:
            articles_topic[article["topic_name"]] = []
        articles_topic[article["topic_name"]].append(article)
    
    topics = []
    for topic, articles in articles_topic.items():
        topics.append(topic)
    
    tabs = st.tabs(topics)
    

    i = 1
    for topic, articles in articles_topic.items():
        #write topic big
        with tabs[topics.index(topic)]:
            st.subheader(topic)
            for article in articles:
                st.markdown(f"## {article['title']}")
                st.write(article['summary'])
                st.button(f"Post article {i}", on_click= post_article, args=(article,))
                i += 1
            
            st.divider()
    
async def main():
    st.title("Streamlit App")
    topic = st.text_input("Enter a topic to scrape")
    #submit button
    if st.button("Process"):
        loop = asyncio.get_running_loop()
        st.write("Scraping data...")
        with concurrent.futures.ThreadPoolExecutor() as pool:
            await loop.run_in_executor(pool, process, topic)
            
            



    
if __name__ == '__main__':
    asyncio.run(main())
    

    



