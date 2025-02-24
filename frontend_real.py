import streamlit as st
import time
import json

# Blogger posting function
def postToBlogger(payload):
    service = getBloggerService()
    post = service.posts()
    insert = post.insert(blogId='711424663010730438', body=payload).execute()
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
    time.sleep(2)
    return f"Scraped data for {topic}"

# Get articles from JSON
def get_articles(scraped_json):
    time.sleep(2)
    with open("summarized_articles.json", "r") as f:
        articles = json.load(f)
    return articles

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

# Cancel button functionality
def cancel():
    st.session_state.flag = 0
    st.session_state.articles = []
    st.session_state.posted_articles = []
    st.session_state.disabled = []



# Main Streamlit app
def main():

    if "flag" not in st.session_state:
        st.session_state.flag = 0

    st.title("Streamlit App")
    topic = st.text_input("Enter a topic to scrape")

    st.button("Process", on_click=reset)
    st.button("Cancel", on_click=cancel)

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

    if st.session_state.flag == 2:
        result = st.session_state.articles
        st.header("Articles")
        st.divider()
        articles_topic = {}

        for article in result:
            st.session_state.disabled.append(False)
            if article["topic_name"] not in articles_topic:
                articles_topic[article["topic_name"]] = []
            articles_topic[article["topic_name"]].append(article)

        topics = list(articles_topic.keys())

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
