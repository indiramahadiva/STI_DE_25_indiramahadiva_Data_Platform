from fastapi import FastAPI, status
from psycopg.types.json import Json
from psycopg_pool import ConnectionPool

from schema.product import ProductSchema

# ─── App & Database Setup ───────────────────────────────────────────
app = FastAPI()

DATABASE_URL = "postgresql://postgres:Leejunho2pm!@localhost:5432/fastapi_postgres"
pool = ConnectionPool(DATABASE_URL)


# ─── Helper: Insert a single product ────────────────────────────────
def insert_product(conn, product_data: dict):
    """Insert a product dict into the products_raw table as JSONB."""
    conn.execute(
        "INSERT INTO products_raw (product) VALUES (%s)",
        (Json(product_data),),
    )


# ─── POST /products  —  Insert one product ──────────────────────────
# Covers Task #1 (tags) and Task #2 (dimensions) automatically,
# because ProductSchema now includes both fields.
@app.post(
    "/products",
    response_model=ProductSchema,
    status_code=status.HTTP_201_CREATED,
)
def create_product(product: ProductSchema) -> ProductSchema:
    with pool.connection() as conn:
        insert_product(conn, product.model_dump())
        conn.commit()
    return product


# ─── POST /products/bulk  —  Insert many products at once ───────────
@app.post("/products/bulk")
def create_products_bulk(products: list[ProductSchema]):
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.executemany(
                "INSERT INTO products_raw (product) VALUES (%s)",
                [(Json(product.model_dump()),) for product in products],
            )
        conn.commit()
    return {"inserted": len(products)}


# ─── GET /products  —  Fetch all products (Task #3) ─────────────────
@app.get("/products")
def get_products():
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT product FROM products_raw")
            rows = cur.fetchall()
            # rows looks like: [(dict,), (dict,), ...]
            # row[0] unpacks each dictionary from its tuple
            return [row[0] for row in rows]
