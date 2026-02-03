from typing import Union

from pydantic import BaseModel


class ProductSchema(BaseModel):
    product_id: str
    name: str
    price: float
    currency: str  # SEK, USD, EUR
    category: Union[str, None]
    brand: Union[str, None]  # TODO - Checkup the Optional Alternative
