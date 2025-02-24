import streamlit as st
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

def post_article(article,i):
    print(f"Article {article['title']} posted")
    
    st.session_state.disabled[i-1] = True
    st.session_state.posted_articles.append(article)

def reset():
    st.session_state.flag = 1
    print(st.session_state["flag"], "HELLO")

def cancel():
    st.session_state.flag = 0
    st.session_state.articles = []
    st.session_state.posted_articles = []
    st.session_state.disabled = []
    print(st.session_state["flag"], "HELLO")





def main():
    
    if "flag" not in st.session_state:
        st.session_state.flag = 0

    st.title("Streamlit App")
    topic = st.text_input("Enter a topic to scrape")

    st.button("Process", on_click=reset)
    st.button("Cancel", on_click=cancel)

    print(st.session_state["flag"])

    if(st.session_state.flag == 1):
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

    if(st.session_state.flag == 2 or st.session_state.flag == 1):
        
        result = st.session_state.articles
        st.header("Articles")
        st.divider()
        articles_topic = dict()
        for article in result:
            st.session_state.disabled.append(False)
            if article["topic_name"] not in articles_topic:
                articles_topic[article["topic_name"]] = []
            articles_topic[article["topic_name"]].append(article)
        
        topics = []
        for topic, articles in articles_topic.items():
            topics.append(topic)
        

        
        tabs = st.tabs(topics + ["Posted Articles"])
            

        i = 1
        for topic, articles in articles_topic.items():
            #write topic big
            with tabs[topics.index(topic)]:
                st.subheader(topic)
                for article in articles:
                    st.markdown(f"## {article['title']}")
                    st.write(article['summary'])
                    st.button(f"Post article {i}", on_click= post_article, args=(article,i,), disabled=st.session_state.disabled[i-1])
                    i += 1
                
                    st.divider()

        with tabs[-1]:
            st.subheader("Posted Articles (From the Current Topic)")
            for article in st.session_state.posted_articles:
                st.write(article['title'])
                st.divider()
    
            



    
if __name__ == '__main__':
    main()
    

    



