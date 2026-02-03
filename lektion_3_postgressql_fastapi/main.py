from fastapi import FastAPI, status
from psycopg_pool import ConnectionPool
from psycopg.types.json import Json  # Convert Pydantic -> JSON
from psycopg import Connection  # Open Temporary Connection

from schema.product import ProductSchema

DATABASE_URL = "postgresql://postgres:Leejunho2pm!@localhost:5432/lektion_3"
pool = ConnectionPool(DATABASE_URL)
app = FastAPI(title="lektion_3_postgresql_fastapi")


@app.get("/")
def root() -> dict:
    return {"Hello": "World"}


@app.post(
    "/products",
    status_code=status.HTTP_201_CREATED,  # Swagger Documentation clarity
    response_model=ProductSchema,  # Swagger Documentation update
)
def post_product(product: ProductSchema) -> ProductSchema:

    # Query-Insert
    with pool.connection() as conn:
        insert_product(conn, product.model_dump())
        conn.commit()  # Execute Logic (close connection when done)

    return product


# Helper Method for DB-Queries
def insert_product(conn: Connection, product: ProductSchema):
    conn.execute(
        "INSERT INTO products_raw (product) VALUES (%s)",
        (Json(product),),  # TODO - Explore the Syntax
    )
