from trending_topics.collectors import _parse_hot_value


def test_parse_hot_value_plain_integer():
    assert _parse_hot_value("12345") == 12345


def test_parse_hot_value_with_wan_unit():
    assert _parse_hot_value("1.2万") == 12000


def test_parse_hot_value_with_yi_unit():
    assert _parse_hot_value("0.5亿") == 50_000_000


def test_parse_hot_value_invalid_input():
    assert _parse_hot_value("未知") == 0
