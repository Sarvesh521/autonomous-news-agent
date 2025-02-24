# Autonomous News Agent

An AI-powered system that automates the creation of news-based blogs using Web Scraping and Large Language Models (LLMs). This platform streamlines the process of gathering, summarizing, and publishing news articles with minimal manual effort.

## Key Features

### 📊 Admin Dashboard with Blog Management
The admin site provides statistics on blog performance and allows you to manage content, including deleting blogs as needed.

### 🔹 Effortless Blog Generation
Easily generate news-based blog posts by entering a topic on the admin panel. The system scrapes the latest news, summarizes key points, and presents sample blog drafts, ready for selection and publishing.

### 🌍 SEO-Optimized Blog Publishing
All generated blogs are automatically posted to a Blogspot domain with built-in Search Engine Optimization (SEO) strategies, ensuring increased visibility and audience reach.

### 📍 Geographical Classification
Each blog is categorized by geographic relevance, allowing users to explore news from specific regions or countries, making it easier to follow localized trends.

## How It Works
1. **Input a Topic:** Enter a news topic on the admin dashboard.
2. **Automated Scraping & Summarization:** The system fetches relevant news from trusted sources and summarizes the content using AI.
3. **Content Curation:** Review and select the best-generated blogs.
4. **Auto-Publishing:** Approved posts are published on Blogger.com with SEO optimization.
5. **Categorization:** Blogs are tagged with relevant geographical information for easy navigation.

## Installation and Running
The program can be accessed either through the admin website url or by running it locally. Here is how to run the admin dashboard locally:

Create a file `client_secrets.json` that contains your credentials for google blogspot.

Then, make sure you are in the root folder and run:

```bash
$ pip install -r requirements.txt
$ streamlit run home.py
```
All published files can be viewed at https://flipr2025.blogspot.com/ . 

The admin site can be viewed at http://54.145.35.27:8501 .

NOTE: In case of refresh token error, please run the authorize_credentials.py from the auth_blogger.py module since google API tokens expire after a certain time.

## Tech Stack
- **BeautifulSoup**: Web scraping to extract news from various sources
- **Streamlit**: Admin dashboard for managing blog generation
- **Blogger API**: Content management and automated publishing
- **AWS**: Hosting and deployment of the admin platform
- **DeepSeek-R1**: The open source LLM model is hosted on the AWS infrastructure.
- **PostgreSQL**: Database management system for storing data. This acts as a cache for the topics we have already been scraped and summarized.

## Blog Site
The blog site containts multiple blogs published via the admin site. Each blog contains labels indicating which geographical subregion they belong to.

![Blog Site](./images/Screenshot%202025-02-24%20230135.png)
![Blog Site1](./images/Screenshot%202025-02-24%20230203.png)

## Admin Site
The admin site has 2 main features.
1. **Creating and Posting Blogs**: You can enter a topic in the given field. Web scraping is done followed by LLM inference to create new blogs. These can be viewed category-wise and posted to the blog on the click of a button.

![Admin Site](./images/Screenshot%202025-02-24%20230808.png)

2. **Overview of Existing Blogs** : The live-posts page shows all the blogs that have been posted till now. You have the option of deleting any blog from here and it also has a link to the blog post.

![Admin Site1](./images/Screenshot%202025-02-24%20231128.png)




