from trending_topics.models import TrendingTopic
from trending_topics.ranking import rank_topics


def make_topic(title: str, traffic: int) -> TrendingTopic:
    return TrendingTopic(title=title, url=None, source="test", traffic=traffic)


def test_rank_topics_descending():
    topics = [make_topic("A", 100), make_topic("B", 50), make_topic("C", 200)]
    ranked = rank_topics(topics)
    assert [topic.title for topic in ranked] == ["C", "A", "B"]


def test_rank_topics_ascending():
    topics = [make_topic("A", 100), make_topic("B", 50), make_topic("C", 200)]
    ranked = rank_topics(topics, descending=False)
    assert [topic.title for topic in ranked] == ["B", "A", "C"]
