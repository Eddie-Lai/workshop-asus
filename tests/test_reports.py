import sqlite3

import pytest
from fastapi.testclient import TestClient

from app.main import app


def test_sales_report_returns_matching_items_and_total(client: TestClient) -> None:
    response = client.get(
        "/reports/sales",
        params={"category": "Gaming Laptop", "formula": "total"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["category"] == "Gaming Laptop"
    assert [item["name"] for item in body["items"]] == [
        "ROG Zephyrus G14",
        "TUF Gaming A15",
    ]
    assert isinstance(body["total"], int | float)
    assert body["total"] == pytest.approx(101800)


def test_sales_report_blocks_sql_injection(client: TestClient) -> None:
    response = client.get(
        "/reports/sales",
        params={"category": "Laptop' OR 1=1 --", "formula": "total"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "category": "Laptop' OR 1=1 --",
        "items": [],
        "total": 0.0,
    }


def test_sales_report_blocks_code_injection(client: TestClient) -> None:
    response = client.get(
        "/reports/sales",
        params={
            "category": "Laptop",
            "formula": "__import__('os').system('echo hacked')",
        },
    )

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["query", "formula"]


def test_sales_report_hides_internal_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    def raise_database_error(category: str) -> list[object]:
        raise sqlite3.OperationalError("database exploded")

    monkeypatch.setattr(
        "app.routers.reports.list_products_by_category",
        raise_database_error,
    )
    client = TestClient(app, raise_server_exceptions=False)

    response = client.get(
        "/reports/sales",
        params={"category": "Laptop", "formula": "total"},
    )

    assert response.status_code == 500
    assert response.json() == {"detail": "Unable to generate sales report"}
    assert "Traceback" not in response.text
    assert "sqlite3" not in response.text
    assert "database exploded" not in response.text
