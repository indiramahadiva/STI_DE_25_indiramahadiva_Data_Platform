# Import BaseModel from pydantic
# BaseModel is the base class for creating data models with validation
from pydantic import BaseModel


# Create a new schema for the rating object
class RatingSchema(BaseModel):
    # The rating has two fields:
    rate: float  # Average rating (e.g., 4.5)
    count: int  # Number of ratings (e.g., 120)


# Define a Pydantic schema class
class ProductSchema(BaseModel):
    # Each attribute has a name and type annotation
    # Pydantic uses these types to validate incoming data

    id: int  # Integer type - must be a whole number
    title: str  # String type - must be text
    price: float  # Float type - decimal number (e.g., 29.99)
    description: str  # String type - product description
    category: str  # String type - product category
    image: str  # String type - URL to product image
    # Add rating field with type RatingSchema
    # This creates a nested object in JSON
    rating: RatingSchema
