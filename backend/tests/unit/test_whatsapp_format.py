from app.services.whatsapp_service import WhatsAppService


def test_format_daily_report():
    service = WhatsAppService()
    message = service.format_daily_report(
        owner_name="Ahmed",
        currency="EGP",
        revenue=18450.0,
        orders_count=52,
        orders_growth_pct=12.0,
        avg_order_value=355.0,
        top_product="Black Hoodie",
        inventory_alert="Only 5 units left",
        ai_insight="Revenue increased because repeat customers purchased 23% more.",
        recommendation="Restock Black Hoodie within 2 days.",
    )

    assert "Good Morning Ahmed" in message
    assert "EGP 18,450" in message
    assert "52 (+12%)" in message
    assert "EGP 355" in message
    assert "Black Hoodie" in message
    assert "Only 5 units left" in message
    assert "— Teqa" in message


def test_format_daily_report_negative_growth():
    service = WhatsAppService()
    message = service.format_daily_report(
        owner_name="Sara",
        currency="EGP",
        revenue=5000.0,
        orders_count=20,
        orders_growth_pct=-8.0,
        avg_order_value=250.0,
        top_product=None,
        inventory_alert=None,
        ai_insight="Sales declined compared to yesterday.",
        recommendation="Consider running a flash sale.",
    )

    assert "Good Morning Sara" in message
    assert "20 (-8%)" in message
    assert "Top Product" not in message
    assert "Inventory Alert" not in message
