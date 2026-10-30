import requests
from config import NEWS_API_KEY

NEWS_API_URL = "https://newsapi.org/v2/everything"


def get_latest_news(topic="tech", limit=3):
    """
    Find tech news articles.
    """
    if not NEWS_API_KEY:
        raise ValueError("NEWS_API_KEY is missing. Add it to the .env file.")

    headers = {
        "X-Api-Key": NEWS_API_KEY,
    }

    params = {
        "q": topic,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": limit,
        "apiKey": NEWS_API_KEY,
    }

    try:
        response = requests.get(
            NEWS_API_URL,
            params=params,
            headers=headers,
            timeout=10,
        )
        response.raise_for_status()

        data = response.json()
        articles = data.get("articles", [])

        news_list = []
        for item in articles:
            news_list.append({
                "title": item.get("title"),
                "content": item.get("description") or item.get("content") or "No content available.",
            })

        return news_list

    except requests.exceptions.RequestException as e:
        print(f"Error finding news: {e}")
        return []


# Test block
if __name__ == "__main__":
    print("Finding news...")
    news_items = get_latest_news()

    for i, article in enumerate(news_items, 1):
        print(f"\n--- News {i} ---")
        print(f"Title: {article['title']}")
        print(f"Content: {article['content']}")