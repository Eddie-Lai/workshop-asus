from pydantic import BaseModel, ConfigDict, Field


class Product(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: int = Field(gt=0)
    name: str = Field(min_length=1)
    category: str = Field(min_length=1)
    price: float = Field(gt=0)


class ProductPage(BaseModel):
    items: list[Product]
    total: int = Field(ge=0)
    page: int = Field(ge=1)
    page_size: int = Field(ge=1)


class SalesReport(BaseModel):
    category: str = Field(min_length=1)
    items: list[Product]
    total: float = Field(ge=0)
