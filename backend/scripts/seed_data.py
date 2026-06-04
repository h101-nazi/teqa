"""Seed script to create demo merchant data for development/testing."""

import asyncio
import random
import uuid
from datetime import date, datetime, timedelta, timezone

from app.core.security import hash_password
from app.database.session import async_session_factory
from app.models import (
    Business,
    Customer,
    Integration,
    IntegrationStatus,
    IntegrationType,
    Product,
    Report,
    ReportDelivery,
    Subscription,
    Transaction,
    TransactionItem,
    User,
)

DEMO_PRODUCTS = [
    {"name": "Black Hoodie", "price": 450, "category": "Clothing", "stock": 15},
    {"name": "White T-Shirt", "price": 180, "category": "Clothing", "stock": 50},
    {"name": "Denim Jeans", "price": 650, "category": "Clothing", "stock": 30},
    {"name": "Running Shoes", "price": 1200, "category": "Footwear", "stock": 8},
    {"name": "Baseball Cap", "price": 120, "category": "Accessories", "stock": 100},
    {"name": "Leather Belt", "price": 350, "category": "Accessories", "stock": 25},
    {"name": "Backpack", "price": 550, "category": "Bags", "stock": 20},
    {"name": "Sunglasses", "price": 280, "category": "Accessories", "stock": 40},
    {"name": "Watch", "price": 1500, "category": "Accessories", "stock": 5},
    {"name": "Perfume", "price": 800, "category": "Beauty", "stock": 35},
]


async def seed():
    async with async_session_factory() as db:
        # Create demo user
        user = User(
            id=uuid.uuid4(),
            email="demo@teqa.app",
            hashed_password=hash_password("demo123"),
            full_name="Ahmed Hassan",
            is_active=True,
            is_verified=True,
        )
        db.add(user)

        # Create business
        business = Business(
            id=uuid.uuid4(),
            owner_id=user.id,
            name="Hassan Fashion Store",
            industry="Fashion & Retail",
            country="Egypt",
            currency="EGP",
            whatsapp_number="+201001234567",
            timezone="Africa/Cairo",
            is_onboarded=True,
        )
        db.add(business)

        # Create integration
        integration = Integration(
            id=uuid.uuid4(),
            business_id=business.id,
            type=IntegrationType.CSV,
            status=IntegrationStatus.CONNECTED,
            metadata_json={"source": "seed_data"},
        )
        db.add(integration)

        # Create products
        products = []
        for p in DEMO_PRODUCTS:
            product = Product(
                id=uuid.uuid4(),
                business_id=business.id,
                name=p["name"],
                price=p["price"],
                category=p["category"],
                stock_quantity=p["stock"],
                low_stock_threshold=10,
            )
            products.append(product)
            db.add(product)

        # Create customers
        customer_names = [
            "Mohamed Ali", "Fatma Ahmed", "Omar Khaled", "Sara Ibrahim",
            "Youssef Mahmoud", "Nour El-Din", "Layla Hassan", "Kareem Mostafa",
        ]
        customers = []
        for name in customer_names:
            customer = Customer(
                id=uuid.uuid4(),
                business_id=business.id,
                name=name,
                email=f"{name.lower().replace(' ', '.')}@example.com",
                phone=f"+20100{random.randint(1000000, 9999999)}",
            )
            customers.append(customer)
            db.add(customer)

        # Create transactions for the last 30 days
        today = date.today()
        for day_offset in range(30):
            day = today - timedelta(days=day_offset)
            num_orders = random.randint(30, 70)
            for _ in range(num_orders):
                num_items = random.randint(1, 4)
                items = random.sample(products, min(num_items, len(products)))
                total = sum(p.price * random.randint(1, 3) for p in items)

                txn = Transaction(
                    id=uuid.uuid4(),
                    business_id=business.id,
                    integration_id=integration.id,
                    customer_id=random.choice(customers).id,
                    amount=total,
                    currency="EGP",
                    status="completed",
                    payment_method=random.choice(["card", "cash", "mobile_wallet"]),
                    items_count=num_items,
                    transaction_date=datetime.combine(
                        day,
                        datetime.min.time().replace(
                            hour=random.randint(8, 22),
                            minute=random.randint(0, 59),
                        ),
                        tzinfo=timezone.utc,
                    ),
                )
                db.add(txn)

                for product in items:
                    qty = random.randint(1, 3)
                    item = TransactionItem(
                        id=uuid.uuid4(),
                        transaction_id=txn.id,
                        product_id=product.id,
                        product_name=product.name,
                        quantity=qty,
                        unit_price=product.price,
                        total_price=product.price * qty,
                    )
                    db.add(item)

        # Create subscription
        subscription = Subscription(
            id=uuid.uuid4(),
            business_id=business.id,
            plan="growth",
            status="active",
            monthly_price=999.0,
        )
        db.add(subscription)

        await db.commit()
        print(f"✓ Seeded demo merchant: {user.email} / demo123")
        print(f"✓ Business: {business.name}")
        print(f"✓ Products: {len(products)}")
        print(f"✓ Customers: {len(customers)}")
        print(f"✓ ~30 days of transaction data")


if __name__ == "__main__":
    asyncio.run(seed())
