from app.ai.insight_engine import InsightEngine


def test_fallback_insights_growth():
    engine = InsightEngine()
    result = engine._fallback_insights(revenue=10000, orders_count=50, growth_pct=15.0)
    assert "grew" in result["summary"].lower() or "15" in result["summary"]
    assert result["insight"]
    assert result["recommendation"]


def test_fallback_insights_decline():
    engine = InsightEngine()
    result = engine._fallback_insights(revenue=5000, orders_count=20, growth_pct=-10.0)
    assert "decline" in result["summary"].lower() or "drop" in result["summary"].lower()


def test_fallback_insights_no_growth():
    engine = InsightEngine()
    result = engine._fallback_insights(revenue=8000, orders_count=30, growth_pct=None)
    assert result["summary"]
    assert result["insight"]
    assert result["recommendation"]


def test_parse_response():
    engine = InsightEngine()
    content = """SUMMARY: Revenue grew 14% with strong repeat purchases.
INSIGHT: Repeat customers drove 23% more orders than the previous day.
RECOMMENDATION: Restock top-selling items and run a loyalty campaign."""

    result = engine._parse_response(content)
    assert "14%" in result["summary"]
    assert "Repeat customers" in result["insight"]
    assert "Restock" in result["recommendation"]
