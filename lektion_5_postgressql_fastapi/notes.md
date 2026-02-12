~~# postgresql & fastapi

## installation

(Use uv if that's your relevant tech)

```bash
pip install "fastapi[standard]"
pip install "psycopg[binary]"
pip install "psycopg[pool]"
```

# Run App

- `$ fastpi dev main.py`

## Storing data - philosophy

- What's the purpose of our data?
  - Bulk uploading
  - JSON data storage
  - Unorganized data
  - PostgreSQL database
- What's the datatype of said data?
  - Unorganized
  - unstructured
  - Json

## Database - PostgreSQL

A newly created database does NOT contain any TABLES by default.

Step #1 - Create new Table (products)

```postgresql
CREATE TABLE IF NOT EXISTS products_raw (
id BIGSERIAL PRIMARY KEY,
created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
product JSONB NOT NULL
);
```

## Step 2 – Create a database connection (URL)

To connect FastAPI to PostgreSQL, you need a **database URL**.

If you are using **pgAdmin 4**, you can find the required values here:

- **Username**  
  Right-click your **database** → _Properties_ → _Username_

- **Password**  
  The password you set when installing PostgreSQL

- **Port**  
  Right-click **PostgreSQL 17** → _Properties_ → _Connection_ → _Port_

- **Address (host)**  
  Found in the same place as **Port**  
  _(Usually `localhost`)_

```python
DATABASE_URL = "postgresql://USERNAME:PASSWORD@ADDRESS:PORT/DB_NAME"
```

Step #3 - Implement an insert function (fastAPI)

```python
def insert_product(conn: Connection, product: ProductSchema):
    conn.execute(
        "INSERT INTO products_raw (product) VALUES (%s)",
        (Json(product.product_dump()),)    # TODO - Explore the Syntax
    )
```

Use helper-method:

```python
@app.post(
    "/products",
    status_code=status.HTTP_201_CREATED,    # Swagger Documentation clarity
    response_model=ProductSchema,           # Swagger Documentation update
)
def post_product(product: ProductSchema) -> ProductSchema:

    # Query-Insert
    with pool.connection() as conn:
        with conn.transaction():
            insert_product(conn, product)

    return product
```

Postman Test against `localhost:8000/products`:

```json
{
  "product_id": "USP239",
  "name": "Wireless Mouse",
  "price": 249.0,
  "currency": "SEK",
  "category": "Electronics",
  "brand": null
}
```

## Difference: `uvicorn` vs `fastapi dev`

## `fastapi dev main.py`

- Development mode
- Auto-reload on file changes
- Extra debug output
- Slower, not production-ready
- Intended for local development only

## `uvicorn main:app`

- Production-style server
- No auto-reload by default
- Faster and more stable
- Commonly used in Docker and deployment
- Can be extended with workers, timeouts, logging
