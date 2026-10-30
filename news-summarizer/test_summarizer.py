import requests

import news_api


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