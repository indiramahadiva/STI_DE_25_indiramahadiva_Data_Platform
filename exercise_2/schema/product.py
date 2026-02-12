from typing import Union
from pydantic import BaseModel


# Task #2: Nested object for product dimensions
class DimensionsSchema(BaseModel):
    width_cm: float
    height_cm: float
    depth_cm: float


class ProductSchema(BaseModel):
    product_id: str
    name: str
    price: float
    currency: str  # (SEK, EUR, USD)
    category: Union[str, None] = None
    brand: Union[str, None] = None
    tags: Union[list[str], None] = None  # Task #1: list of tags
    dimensions: Union[DimensionsSchema, None] = None  # Task #2: nested object
