import json
import time
import random
import subprocess
import argparse
from ollama import chat, ChatResponse
import re
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
import numpy as np

# Configuration
# NO_OF_ARTICLES = 3   # Number of articles to process.
NO_OF_CHUNKS = 3     # Number of chunks to select for summarization.
SCRAPER_OUTPUT_FILE = "processed_articles.json"
MODEL_OUTPUT_FILE = "summarized_articles.json"


def extract_info(text: str) -> tuple:
    """
    Extract the title, location, and summary from the provided text.
    
    The function expects the text to begin with:
    
    **Title:** <actual title>
    
    **Location:** <actual location>
    
    followed by one or more newlines and then the summary text.
    
    Returns:
        tuple: (title, location, summary)
    """
    pattern = r"^\*\*Title:\*\*\s*(?P<title>.*?)\s*\n\s*\*\*Location:\*\*\s*(?P<location>.*?)\s*\n+(?P<summary>.*)$"
    match = re.search(pattern, text, re.DOTALL | re.MULTILINE)
    if match:
        title = match.group("title").strip()
        location = match.group("location").strip()
        summary = match.group("summary").strip()
        return (title, location, summary)
    else:
        # If the expected pattern is not found, return None for title and location,
        # and the whole text as the summary.
        return (None, None, text)

def load_processed_articles(file_path=SCRAPER_OUTPUT_FILE):
    """Load processed articles from the given JSON file."""
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def aggregate_topic_text(topic_dict):
    """
    For a given topic dictionary (with keys "topic_name" and "url_content"),
    concatenate the article texts (ignoring empty ones) into one large string.
    """
    texts = []
    for pair in topic_dict.get("url_content", []):
        # Each pair is expected to be [source_url, article_text]
        article_text = pair[1]
        if article_text.strip():
            texts.append(article_text.strip())
    return "\n".join(texts)

def create_text_chunks(text, chunk_size=1000, chunk_overlap=200):
    """
    Split text into chunks using LangChain's RecursiveCharacterTextSplitter.
    """
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return splitter.split_text(text)

def create_embeddings_for_chunks(chunks):
    """
    Create embeddings for each text chunk using a local HuggingFace model.
    (These embeddings can be used for further retrieval tasks if needed.)
    """
    hf_embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    embeddings = [hf_embeddings.embed_query(chunk) for chunk in chunks]
    return embeddings

def cosine_similarity(a, b):
    """Compute cosine similarity between two vectors."""
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def extract_title(summary_text: str):
    """
    Extracts the title from the summary text and returns a tuple of (title, cleaned_summary).
    It assumes the output begins with the line:
    
    **Title:** <actual title>
    
    followed by one or more newlines and then the rest of the summary.
    """
    # Updated regex: allow one or more newline characters after the title.
    pattern = r"^\*\*Title:\*\*\s*(.*?)\s*\n+(.*)$"
    match = re.match(pattern, summary_text, re.DOTALL)
    if match:
        title = match.group(1).strip()
        clean_summary = match.group(2).strip()
        return title, clean_summary
    else:
        return "No Title Found", summary_text

def get_chat_response(system_prompt: str, user_prompt: str, model: str = "deepseek-r1:8b") -> str:
    """
    Get a chat response from the specified model using both a system and a user prompt.
    
    Args:
        system_prompt (str): The system message that sets the context and behavior.
        user_prompt (str): The user message with the actual task.
        model (str): The model to use (default: deepseek-r1:8b).
    
    Returns:
        str: The complete output generated by the model.
    """
    response: ChatResponse = chat(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        stream=True,
    )

    full_response = ""
    for chunk in response:
        content = chunk["message"]["content"]
        print(content, end="", flush=True)
        full_response += content
    print("\n")
    # Remove any <think> sections from the response.
    full_response = re.sub(r"<think>.*?</think>", "", full_response, flags=re.DOTALL).strip()
    return full_response

def main(NO_OF_CHUNKS):
    articles = load_processed_articles(SCRAPER_OUTPUT_FILE)
    final_results = []
    system_prompt = (
        "You are an expert summarizer with advanced journalistic skills and SEO expertise. "
        "Your responses must be completely factual, concise, and authoritative. "
        "Do not hallucinate details. Always include precise geographic information, "
        "pinpointing the location to the district level if available. Otherwise hierarchies above district "
        "When including location information in your output, you must provide only the loction name alone , no need for any add ons . "
        "For example, if the input location is 'Belagavi district, Karnataka', your output should be simply 'Belagavi'. "
        "Maintain a clear, formal tone and ensure your summary is optimized with relevant SEO keywords."
    )
    print("articles")
    print(articles)

    for x in articles:
        print("x", x)
        print("x['url_content']", x['url_content'])
        user_prompt = (
            "Based on the text provided below, please generate a blog post summary. "
            "Your output must follow this strict format exactly:\n\n"
            "**Title:** <actual title of the blog post>\n\n"
            "**Location:** <geographic location – district level if possible, otherwise state>\n\n"
            "Then provide a concise, factual summary of the article. "
            "Ensure that the summary is written in clear, authoritative language and includes relevant SEO keywords.\n\n"
            "Text: {text}"
        )

        user_prompt = user_prompt.format(text=x['url_content'])
        # print("user_prompt", user_prompt)
        full_response = get_chat_response(system_prompt, user_prompt)
        print("full_response")
        print(full_response)
        print("....................")
        title, location, clean_summary = extract_info(full_response)
        final_results.append({
            "topic_name": title,
            "title": title,
            "location": location,
            "summary": clean_summary
        })
    with open(MODEL_OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(final_results, f, indent=4, ensure_ascii=False)
    print("Summarized articles saved to:", MODEL_OUTPUT_FILE)
    return final_results

if __name__ == "__main__":
    start_time = time.time()
    main(NO_OF_CHUNKS)
    end_time = time.time()
    print(f"\nTotal time taken: {end_time - start_time:.2f} seconds.")
