from pydantic import BaseModel


class RatingSchema(BaseModel):
    rate: float
    count: int


class ProductSchema(BaseModel):
    id: int
    title: str
    price: float
    description: str
    category: str
    image: str
    rating: RatingSchema
