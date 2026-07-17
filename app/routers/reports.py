import logging
import sqlite3
from typing import Literal

from fastapi import APIRouter, HTTPException, Query, status

from app.models import SalesReport
from app.repository import list_products_by_category

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/sales", response_model=SalesReport)
def sales_report(
    category: str = Query(min_length=1, max_length=100),
    formula: Literal["total"] = Query(default="total"),
) -> SalesReport:
    del formula

    try:
        items = list_products_by_category(category)
    except sqlite3.Error:
        logger.exception("Failed to generate sales report")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to generate sales report",
        ) from None

    total = sum(item.price for item in items)
    return SalesReport(category=category, items=items, total=total)
