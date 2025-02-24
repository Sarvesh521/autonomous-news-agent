import streamlit as st
import time
import json
from auth_blogger import getBloggerService, dump_posts_to_json
import web_scraping
import Model as model

# Blogger posting function
def postToBlogger(payload):
    service = getBloggerService()
    post = service.posts()
    insert = post.insert(blogId='8510639159580300368', body=payload).execute()
    return insert

# Function to post a single article
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

# Simulated scraping function
def get_scraped_data(topic):
    return web_scraping.main(topic, web_scraping.MAX_ARTICLES_PER_SUBTOPIC, web_scraping.MAX_NO_OF_SUBTOPICS)

# Get articles from JSON
def get_articles(scraped_json):
    return model.main(model.NO_OF_CHUNKS)

# Function to post an article
def post_article(article, i):
    response = postSingleEntry(article)  # Call Blogger API to post article
    if response:
        st.success(f"✅ Posted: {article['title']} (URL: {response['url']})")
        st.session_state.disabled[i - 1] = True
        st.session_state.posted_articles.append(article)

# Reset button functionality
def reset():
    st.session_state.flag = 1




# Main Streamlit app
def main():

    if "flag" not in st.session_state:
        st.session_state.flag = 0
    
    if "articles" not in st.session_state:
        try:
            with open("summarized_articles.json", "r") as f:
                st.session_state.articles = json.load(f)
        except:
            st.session_state.articles = []

    st.title("Autonomous News Agent")
    topic = st.text_input("Enter a topic to scrape")

    st.button("Process", on_click=reset)

    if st.session_state.flag == 1:
        st.session_state.posted_articles = []
        st.session_state.disabled = []
        st.session_state.flag = 2
        st.write("Scraping data...")
        result = get_scraped_data(topic)
        st.write("Data scraped for", topic)
        st.write("Processing articles...")
        st.session_state.articles = get_articles(result)
        st.write("Articles processed for", topic)
        st.divider()


    result = st.session_state.articles
    st.header("Articles")
    st.divider()
    articles_topic = {}

    for article in result:
        st.session_state.disabled.append(False)
        if article["location"] not in articles_topic:
            articles_topic[article["location"]] = []
        articles_topic[article["location"]].append(article)

    topics = list(articles_topic.keys())
    print("Topics", topics)
    tabs = st.tabs(topics + ["Posted Articles"])

    i = 1
    for topic, articles in articles_topic.items():
        with tabs[topics.index(topic)]:
            st.subheader(topic)
            for article in articles:
                st.markdown(f"## {article['title']}")
                st.write(article['summary'])
                st.button(f"Post article {i}", on_click=post_article, args=(article, i), disabled=st.session_state.disabled[i - 1])
                i += 1
                st.divider()

    with tabs[-1]:
        st.subheader("Posted Articles (From the Current Topic)")
        for article in st.session_state.posted_articles:
            st.write(article['title'])
            st.divider()

if __name__ == '__main__':
    main()
