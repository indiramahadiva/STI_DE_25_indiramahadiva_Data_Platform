# Import the FastAPI class from the fastapi module
from fastapi import FastAPI

# Import your ProductSchema from the schema folder
from schema.product import ProductSchema, RatingSchema

import requests

# Create an instance of FastAPI
# 'title' parameter sets the API name shown in documentation
app = FastAPI(title="My First API")


# Define a GET endpoint at the root path "/"
# @app.get() is a decorator that tells FastAPI this function handles GET requests
@app.get("/")
def hello_world():
    # Return a Python dictionary
    # FastAPI automatically converts it to JSON
    return {"message": "Hello World"}


# Create a list of products
# Type annotation: list[ProductSchema] means "list containing ProductSchema objects"
productList: list[ProductSchema] = [
    ProductSchema(
        id=1,
        title="Laptop",
        price=299.99,
        description="Powerful laptop for work",
        category="Electronics",
        image="https://www.microsoft.com/en-us/surface/devices/surface-laptop",
        # Add rating field
        rating=RatingSchema(rate=4.2, count=85),
    ),
    ProductSchema(
        id=2,
        title="Mouse",
        price=29.99,
        description="Ergonomic wireless mouse",
        category="Electronics",
        image="https://thetechhacker.com/2016/12/05/what-is-mouse/",
        # Add rating field
        rating=RatingSchema(rate=4.5, count=120),  # Average rating  # Number of reviews
    ),
]


@app.get("/products", response_model=list[ProductSchema])
def get_products() -> list[ProductSchema]:
    # Make HTTP GET request to FakeStore API
    # This sends a request to the external API and waits for response
    result = requests.get("https://fakestoreapi.com/products")

    # Parse the JSON response into Python data structures
    # Converts JSON string to a Python list of dictionaries
    response_json = result.json()

    # Create an empty list to store validated ProductSchema objects
    # Type hint indicates this list will contain ProductSchema instances
    products: list[ProductSchema] = []

    # Loop through each product dictionary in the response
    for item in response_json:
        # Convert dictionary to ProductSchema using unpacking
        # **item unpacks the dict: {"id": 1, "title": "X"} becomes ProductSchema(id=1, title="X")
        # Pydantic automatically validates all fields and data types
        product = ProductSchema(**item)

        # Add the validated product to our list
        products.append(product)

    # Return the list of validated products
    # FastAPI automatically converts ProductSchema objects to JSON
    return list(products)
