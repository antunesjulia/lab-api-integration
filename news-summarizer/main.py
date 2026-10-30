from news_api import get_latest_news
from summarizer import summarize_news


def main():
    print("Finding the latest news...\n")
    news_items = get_latest_news()

    if not news_items:
        print("No news articles were found.")
        return

    print("Writing the summary...\n")
    summary = summarize_news(news_items)

    if summary is None:
        raise RuntimeError("The news summary could not be generated.")

    print(summary)


if __name__ == "__main__":
    main()