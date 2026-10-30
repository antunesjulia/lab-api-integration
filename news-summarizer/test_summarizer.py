import requests
from types import SimpleNamespace

import news_api
import summarizer


FAKE_NEWS_API_URL = "https://newsapi.org/v2/everything"
FAKE_ARTICLE = {
    "title": "Libraries launch free robotics club",
    "description": "A local library started a robotics club for teenagers.",
    "content": "The library launched a free weekly robotics club for teenagers.",
    "url": "https://example.com/robotics-club",
}


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


def test_get_latest_news_uses_fake_news_payload(monkeypatch):
    payload = {"articles": [FAKE_ARTICLE]}

    def fake_get(url, params=None, headers=None, timeout=None):
        assert url == FAKE_NEWS_API_URL
        assert params["q"] == "robotics"
        assert params["pageSize"] == 1
        assert headers["X-Api-Key"] == "fake-key"
        return FakeResponse(payload)

    monkeypatch.setattr(news_api, "NEWS_API_KEY", "fake-key")
    monkeypatch.setattr(requests, "get", fake_get)

    result = news_api.get_latest_news("robotics", 1)

    assert result[0]["title"] == FAKE_ARTICLE["title"]
    assert "robotics club" in result[0]["content"].lower()


def test_get_latest_news_returns_empty_list_on_request_error(monkeypatch):
    def fake_get(url, params=None, headers=None, timeout=None):
        raise requests.exceptions.RequestException("mocked failure")

    monkeypatch.setattr(news_api, "NEWS_API_KEY", "fake-key")
    monkeypatch.setattr(requests, "get", fake_get)

    result = news_api.get_latest_news("tech", 3)

    assert result == []


def test_summarize_news_uses_openai_and_returns_summary(monkeypatch):
    expected_summary = "The library launched a free weekly robotics club for teenagers."
    calls = {}

    class FakeChatCompletions:
        def create(self, **kwargs):
            calls.update(kwargs)
            return SimpleNamespace(
                choices=[
                    SimpleNamespace(
                        message=SimpleNamespace(content=f" {expected_summary} ")
                    )
                ]
            )

    fake_client = SimpleNamespace(
        chat=SimpleNamespace(completions=FakeChatCompletions())
    )
    monkeypatch.setattr(summarizer, "client", fake_client)

    result = summarizer.summarize_news(
        [{"title": FAKE_ARTICLE["title"], "content": FAKE_ARTICLE["content"]}]
    )

    assert result == expected_summary
    assert calls["model"] == "gpt-4o-mini"
    assert calls["messages"][0]["role"] == "system"
    assert FAKE_ARTICLE["title"] in calls["messages"][1]["content"]
    assert FAKE_ARTICLE["content"] in calls["messages"][1]["content"]


def test_summarize_news_returns_message_for_empty_input(monkeypatch):
    monkeypatch.setattr(summarizer, "client", None)

    assert summarizer.summarize_news([]) == "No news to summarize."


def test_fake_news_payload_flows_into_openai_summary(monkeypatch):
    expected_summary = "A library started a free robotics club for teenagers."
    captured_request = {}

    def fake_get(url, params=None, headers=None, timeout=None):
        return FakeResponse({"articles": [FAKE_ARTICLE]})

    class FakeChatCompletions:
        def create(self, **kwargs):
            captured_request.update(kwargs)
            return SimpleNamespace(
                choices=[
                    SimpleNamespace(
                        message=SimpleNamespace(content=expected_summary)
                    )
                ]
            )

    fake_client = SimpleNamespace(
        chat=SimpleNamespace(completions=FakeChatCompletions())
    )
    monkeypatch.setattr(news_api, "NEWS_API_KEY", "fake-key")
    monkeypatch.setattr(requests, "get", fake_get)
    monkeypatch.setattr(summarizer, "client", fake_client)

    articles = news_api.get_latest_news("robotics", 1)
    result = summarizer.summarize_news(articles)

    prompt = captured_request["messages"][1]["content"]
    assert result == expected_summary
    assert FAKE_ARTICLE["title"] in prompt
    assert FAKE_ARTICLE["description"] in prompt