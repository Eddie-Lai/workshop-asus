import sqlite3

from app.models import Product

PRODUCTS = [
    Product(id=1, name="Zenbook 14 OLED", category="Laptop", price=42900),
    Product(id=2, name="ROG Zephyrus G14", category="Gaming Laptop", price=62900),
    Product(id=3, name="ProArt P16", category="Creator Laptop", price=79900),
    Product(id=4, name="TUF Gaming A15", category="Gaming Laptop", price=38900),
    Product(id=5, name="ROG Ally X", category="Handheld", price=26900),
    Product(id=6, name="ProArt Display PA279CRV", category="Monitor", price=15900),
]


def list_products(
    *,
    q: str | None = None,
    sort: str | None = None,
    order: str = "asc",
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Product], int]:
    products = PRODUCTS.copy()

    if q is not None:
        q_lower = q.lower()
        products = [
            product
            for product in products
            if q_lower in product.name.lower() or q_lower in product.category.lower()
        ]

    if sort == "name":
        products.sort(key=lambda product: product.name, reverse=order == "desc")
    elif sort == "price":
        products.sort(key=lambda product: product.price, reverse=order == "desc")

    total = len(products)
    start = (page - 1) * page_size
    end = start + page_size

    return products[start:end], total


def get_product(product_id: int) -> Product | None:
    return next((product for product in PRODUCTS if product.id == product_id), None)


def create_product_database() -> sqlite3.Connection:
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    connection.execute(
        "CREATE TABLE products (id INTEGER, name TEXT, category TEXT, price REAL)"
    )
    connection.executemany(
        "INSERT INTO products VALUES (?, ?, ?, ?)",
        [
            (product.id, product.name, product.category, product.price)
            for product in PRODUCTS
        ],
    )
    return connection


def list_products_by_category(category: str) -> list[Product]:
    connection = create_product_database()
    try:
        rows = connection.execute(
            "SELECT id, name, category, price FROM products WHERE category = ?",
            (category,),
        ).fetchall()
    finally:
        connection.close()

    return [Product.model_validate(dict(row)) for row in rows]
