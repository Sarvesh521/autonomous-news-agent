import requests
import json

# Replace with your actual OpenRouter API Key
API_KEY = "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"

def summarize_text(text, keyword):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = json.dumps({
        "model": "deepseek/deepseek-r1-distill-llama-8b",  # Using DeepSeek Mixtral model (free)
        "messages": [
            {"role": "user", "content": f'''Give me SEO optimized summarization of the following paragraph: {text} and give the response in a single paragraph.
            The summarization should focus on the keyword {keyword} and also provide relevant links to resources and also generate relevant images. Dont use an example link. Provide popular links related to the topic.'''}
        ],
        "top_p": 1,
        "temperature": 1,
        "repetition_penalty": 1
    })

    response = requests.post(url, headers=headers, data=data)
    
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"Error: {response.json()}"

if __name__ == "__main__":
    input_text = """
    In recent years, artificial intelligence has seen tremendous growth, influencing numerous industries 
    such as healthcare, finance, and transportation. AI-powered systems are now capable of diagnosing diseases 
    with remarkable accuracy, predicting stock market trends, and even driving autonomous vehicles. 
    The integration of machine learning models into everyday applications has streamlined processes and improved efficiency, 
    allowing businesses to make data-driven decisions faster than ever before. However, concerns about ethical implications, 
    data privacy, and job displacement have also arisen. Governments and regulatory bodies are now working to ensure AI development 
    aligns with societal values and ethical considerations while still fostering innovation.
    """

    summary = summarize_text(input_text, "AI")
    print("\nSummarized Text:\n", summary)