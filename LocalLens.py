import streamlit as st
from bs4 import BeautifulSoup
import requests
from transformers import pipeline

# Initialize the Hugging Face summarization pipeline
summarizer = pipeline("summarization", model="t5-small", tokenizer="t5-small")

# Predefined list of locations and genres
locations = ["New York", "Los Angeles", "Chicago", "Houston", "Miami"]
genres = ["Politics", "Sports", "Technology", "Entertainment", "Health"]

# Mapping of sources for different locations and genres
news_sources = {
    "New York": {
        "Politics": "https://www.nytimes.com/section/politics",
        "Sports": "https://www.nytimes.com/section/sports",
        "Technology": "https://www.nytimes.com/section/technology",
        "Entertainment": "https://www.nytimes.com/section/arts",
        "Health": "https://www.nytimes.com/section/health",
    },
    "Los Angeles": {
        "Politics": "https://www.latimes.com/politics",
        "Sports": "https://www.latimes.com/sports",
        "Technology": "https://www.latimes.com/business/technology",
        "Entertainment": "https://www.latimes.com/entertainment-arts",
        "Health": "https://www.latimes.com/science",
    },
    # Add more locations and sources as needed
}

# Function to scrape headlines from the news website
def scrape_headlines(url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            # Extract headlines (customize selector based on the website)
            headlines = soup.find_all("h2", limit=5)  # Limit to top 5 headlines
            news = [headline.text.strip() for headline in headlines if headline.text]
            return news if news else ["No articles found."]
        else:
            return [f"Failed to fetch articles. HTTP Status Code: {response.status_code}"]
    except Exception as e:
        return [f"An error occurred: {str(e)}"]

# Function to summarize articles
def summarize_articles(headlines):
    summaries = []
    for headline in headlines:
        try:
            summary = summarizer(headline, max_length=50, min_length=10, do_sample=False)
            summaries.append(summary[0]['summary_text'])
        except Exception:
            summaries.append("Could not summarize this article.")
    return summaries

# Streamlit UI
st.title("Enhanced Local News Summarizer")
st.subheader("Get tailored local news based on your location and genre!")

# User input: Select location and genre
selected_location = st.selectbox("Select your location:", locations)
selected_genre = st.selectbox("Select the news genre:", genres)

if st.button("Fetch News"):
    if selected_location in news_sources and selected_genre in news_sources[selected_location]:
        with st.spinner("Fetching news articles..."):
            news_url = news_sources[selected_location][selected_genre]
            headlines = scrape_headlines(news_url)
        
        st.subheader(f"Top {selected_genre} News in {selected_location}")
        for idx, headline in enumerate(headlines):
            st.write(f"**{idx + 1}. {headline}**")
        
        if st.button("Summarize News"):
            with st.spinner("Summarizing articles..."):
                summaries = summarize_articles(headlines)
            
            st.subheader("Summarized News")
            for idx, summary in enumerate(summaries):
                st.write(f"**{idx + 1}. {summary}**")
    else:
        st.error("No news sources available for the selected location and genre.")

st.caption("Powered by Streamlit, BeautifulSoup, and Hugging Face.")
