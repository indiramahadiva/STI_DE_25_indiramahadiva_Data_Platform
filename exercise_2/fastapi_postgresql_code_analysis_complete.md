# FastAPI & PostgreSQL - Code Analysis Answers

Complete answers to all three code analysis questions from the FastAPI & PostgreSQL exercise.

---

## Table of Contents
1. [Code Analysis #1 - Connection Management](#code-analysis-1---connection-management)
2. [Code Analysis #2 - model_dump()](#code-analysis-2---model_dump)
3. [Code Analysis #3 - Bulk Insert Analysis](#code-analysis-3---bulk-insert-analysis)

---

# Code Analysis #1 - Connection Management

## Question
```python
import psycopg
from psycopg_pool import ConnectionPool

pool = ConnectionPool("postgresql://postgres:password@localhost:5432/demo_5")

def store_value(value: str):
    with pool.connection() as conn:
        conn.execute(
            "INSERT INTO demo_table (value) VALUES (%s)",
            (value,)
        )
        conn.commit()
```

**Where does the connection OPEN and where does it CLOSE?**
**What does 'with' and 'as' mean in this context?**

---

## Answer

### Where the Connection Opens and Closes

#### **Connection OPENS:**
- When `pool.connection()` is called (entering the `with` block)
- The pool retrieves an available connection from the connection pool
- If no connection is available, it waits or creates a new one

#### **Connection CLOSES:**
- Automatically when the `with` block exits
- This happens regardless of whether the code:
  - Completes normally ✅
  - Raises an exception ❌
  - Is interrupted by the user ⚠️

### What 'with' and 'as' Mean

#### **`with` - Context Manager**
- A Python construct for **automatic resource management**
- Guarantees that resources are properly cleaned up
- Called a "context manager" in Python terminology

**How it works:**
```python
with resource() as variable:
    # 1. resource() is called and opens the resource
    # 2. The resource is assigned to 'variable'
    # 3. Code in the block executes
    # 4. Resource is AUTOMATICALLY closed when the block exits
```

#### **`as` - Variable Assignment**
- Assigns the opened resource to a variable name
- In this case: the connection object is assigned to `conn`
- We can now use `conn` to interact with the database

---

## Why This Is Important

### ❌ Without context manager (dangerous):
```python
def store_value_bad(value: str):
    conn = pool.connection()
    conn.execute("INSERT INTO demo_table (value) VALUES (%s)", (value,))
    conn.commit()
    conn.close()  # What happens if an error occurs before this line?
```

**Problems:**
- If an exception is raised before `conn.close()`, the connection leaks
- Connection is never returned to the pool
- Pool can run out of connections (resource exhaustion)

### ✅ With context manager (safe):
```python
def store_value_good(value: str):
    with pool.connection() as conn:
        conn.execute("INSERT INTO demo_table (value) VALUES (%s)", (value,))
        conn.commit()
    # conn.close() is called AUTOMATICALLY here, even on errors
```

**Benefits:**
- Connection always returns to the pool
- No risk of connection leaks
- Cleaner, more readable code
- Follows Python best practices

---

## Flow Diagram

```
1. pool.connection() is called
   ↓
2. Connection is retrieved from the pool
   ↓
3. Connection is assigned to 'conn' (via 'as')
   ↓
4. Code in the with block executes:
   - execute() - runs SQL query
   - commit() - saves the changes
   ↓
5. with block exits
   ↓
6. Connection closes AUTOMATICALLY
   ↓
7. Connection returns to the pool
```

---

## Comparison with Other Resources

Context managers are used for many types of resources:

```python
# Files
with open('file.txt', 'r') as f:
    data = f.read()
# File closes automatically

# Database connections
with pool.connection() as conn:
    conn.execute("SELECT * FROM users")
# Connection closes automatically

# Locks (threading)
with lock:
    # Critical section
    shared_resource.update()
# Lock releases automatically
```

---

## Summary

| Concept | What It Does |
|---------|-------------|
| **`with`** | Creates a context manager that guarantees automatic cleanup |
| **`as conn`** | Assigns the connection object to the variable `conn` |
| **Connection OPENS** | When `pool.connection()` is called (at the `with` line) |
| **Connection CLOSES** | Automatically when the `with` block exits |

**Key Takeaway:** Context managers prevent resource leaks and make code safer and more robust! 🛡️

---

# Code Analysis #2 - model_dump()

## Question
```python
@app.post("/products", response_model=ProductSchema,
          status_code=status.HTTP_201_CREATED)
def products(product: ProductSchema) -> ProductSchema:
    with pool.connection() as conn:
        insert_product(conn, product.model_dump())
        conn.commit()
    return product
```

**What is 'product.model_dump()' and why is it necessary?**

---

## Answer

### What is `model_dump()`?

`model_dump()` is a **Pydantic method** that converts a Pydantic model object into a Python dictionary.

#### **Before conversion:**
```python
# ProductSchema object (Pydantic model instance)
product = ProductSchema(
    product_id="SKU-123",
    name="Wireless Mouse",
    price=299.0,
    currency="SEK"
)

print(type(product))  # <class 'ProductSchema'>
```

#### **After conversion:**
```python
# Dictionary (standard Python dict)
product_dict = product.model_dump()

print(type(product_dict))  # <class 'dict'>
print(product_dict)
# {
#     'product_id': 'SKU-123',
#     'name': 'Wireless Mouse',
#     'price': 299.0,
#     'currency': 'SEK'
# }
```

---

## Why Is It Necessary?

### 1. **Database functions expect dictionaries**

```python
def insert_product(conn, product_data: dict):
    """
    This function expects a dictionary,
    not a Pydantic model object
    """
    conn.execute(
        "INSERT INTO products_raw (product) VALUES (%s)",
        (Json(product_data),)  # Json() needs dict, not Pydantic model
    )
```

### 2. **Pydantic models are not directly serializable**

❌ **Without `model_dump()`:**
```python
# This will cause an error!
def products_broken(product: ProductSchema):
    with pool.connection() as conn:
        insert_product(conn, product)  # ❌ TypeError!
        conn.commit()
    return product
```

✅ **With `model_dump()`:**
```python
# This works perfectly!
def products_working(product: ProductSchema):
    with pool.connection() as conn:
        insert_product(conn, product.model_dump())  # ✅ Converts to dict
        conn.commit()
    return product
```

---

## Detailed Explanation with Examples

### Scenario: Complex nested object

```python
from pydantic import BaseModel
from typing import Union

class DimensionsSchema(BaseModel):
    width_cm: float
    height_cm: float
    depth_cm: float

class ProductSchema(BaseModel):
    product_id: str
    name: str
    price: float
    tags: Union[list[str], None] = None
    dimensions: Union[DimensionsSchema, None] = None
```

### Input (Pydantic object):
```python
product = ProductSchema(
    product_id="SKU-456",
    name="Gaming Keyboard",
    price=899.0,
    tags=["gaming", "rgb", "mechanical"],
    dimensions=DimensionsSchema(
        width_cm=45.5,
        height_cm=3.5,
        depth_cm=15.0
    )
)
```

### Output after `model_dump()`:
```python
product_dict = product.model_dump()

print(product_dict)
# {
#     'product_id': 'SKU-456',
#     'name': 'Gaming Keyboard',
#     'price': 899.0,
#     'tags': ['gaming', 'rgb', 'mechanical'],
#     'dimensions': {
#         'width_cm': 45.5,
#         'height_cm': 3.5,
#         'depth_cm': 15.0
#     }
# }
```

**Note:** Nested Pydantic models (`DimensionsSchema`) are also automatically converted to dictionaries! 🎯

---

## Alternatives to `model_dump()`

### Older Pydantic versions (v1.x):
```python
# Pydantic v1
product_dict = product.dict()  # Old method

# Pydantic v2
product_dict = product.model_dump()  # New method (recommended)
```

### Other useful methods:

```python
# Convert to JSON string
json_string = product.model_dump_json()
# '{"product_id":"SKU-123","name":"Wireless Mouse",...}'

# Exclude certain fields
product_dict = product.model_dump(exclude={'price', 'currency'})

# Include only certain fields
product_dict = product.model_dump(include={'product_id', 'name'})

# Exclude None values
product_dict = product.model_dump(exclude_none=True)
```

---

## Why Use Pydantic at All?

### Advantages of Pydantic models:

#### 1. **Type Safety**
```python
product = ProductSchema(
    product_id="SKU-123",
    name="Mouse",
    price="invalid"  # ❌ ValidationError: price must be float
)
```

#### 2. **Automatic validation**
```python
product = ProductSchema(
    product_id="SKU-123",
    name="Mouse",
    price=-50.0  # You can add validators to prevent negative prices
)
```

#### 3. **Documentation**
```python
class ProductSchema(BaseModel):
    """Product information schema"""
    product_id: str  # Unique product identifier
    name: str  # Product name
    price: float  # Price in currency units
```

#### 4. **IDE Support**
```python
product = ProductSchema(...)
product.name  # ✅ IDE knows this is a string
product.price  # ✅ IDE knows this is a float
product.invalid_field  # ❌ IDE warns you immediately
```

---

## Data Flow in a FastAPI Endpoint

```
1. HTTP Request arrives
   ↓
2. FastAPI receives JSON data:
   {
     "product_id": "SKU-123",
     "name": "Mouse",
     "price": 299.0
   }
   ↓
3. FastAPI + Pydantic validates and converts to ProductSchema object
   ↓
4. Your endpoint function receives a validated ProductSchema object
   ↓
5. You call product.model_dump() to get a dictionary
   ↓
6. Dictionary is sent to the database function
   ↓
7. Database function uses Json() to convert to JSONB
   ↓
8. Data is saved in PostgreSQL
```

---

## Practical Example: Complete Workflow

```python
from fastapi import FastAPI, status
from pydantic import BaseModel
from psycopg_pool import ConnectionPool
from psycopg.types.json import Json

app = FastAPI()
pool = ConnectionPool("postgresql://postgres:password@localhost:5432/demo_5")

# 1. Define schema
class ProductSchema(BaseModel):
    product_id: str
    name: str
    price: float
    currency: str = "SEK"

# 2. Database helper function
def insert_product(conn, product_data: dict):
    """Expects a DICTIONARY, not a Pydantic object"""
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO products_raw (product) VALUES (%s)",
            (Json(product_data),)
        )

# 3. FastAPI endpoint
@app.post("/products", response_model=ProductSchema, status_code=status.HTTP_201_CREATED)
def create_product(product: ProductSchema) -> ProductSchema:
    """
    product: is a ProductSchema object (Pydantic model)
    product.model_dump(): converts to dictionary
    """
    with pool.connection() as conn:
        insert_product(conn, product.model_dump())  # ← Here we convert!
        conn.commit()
    
    return product  # FastAPI converts back to JSON automatically
```

---

## Summary

| Aspect | Explanation |
|--------|-----------|
| **What is it?** | Method that converts Pydantic model → dictionary |
| **Why is it needed?** | Database functions expect dict, not Pydantic objects |
| **When is it used?** | Before sending data to database, API calls, or serialization |
| **Alternative name** | `.dict()` in Pydantic v1 (deprecated in v2) |
| **Handling nested objects** | Recursively converts all nested Pydantic models |

**Key Insight:** Pydantic models are for **validation and type safety**. Dictionaries are for **data transport and storage**. `model_dump()` builds the bridge between these two worlds! 🌉

---

# Code Analysis #3 - Bulk Insert Analysis

## Question
```python
@app.post("/products/bulk")
def products_bulk(products: list[ProductSchema]):
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.executemany(
                "INSERT INTO products_raw (product) VALUES (%s)",
                [(Json(product.model_dump()),) for product in products]
            )
        conn.commit()
    return {"inserted": len(products)}
```

**Just by analyzing the code… what do you think this does?**

---

## Answer

### Overall Functionality

This endpoint **inserts multiple products simultaneously** into the database in an efficient way (bulk insert operation).

---

## Step-by-Step Breakdown

### 1. **Endpoint definition**
```python
@app.post("/products/bulk")
def products_bulk(products: list[ProductSchema]):
```

- HTTP POST endpoint at `/products/bulk`
- Accepts a **list of ProductSchema objects**
- Example input:
  ```json
  [
    {
      "product_id": "SKU-001",
      "name": "Mouse",
      "price": 299.0
    },
    {
      "product_id": "SKU-002",
      "name": "Keyboard",
      "price": 899.0
    }
  ]
  ```

### 2. **Connection management**
```python
with pool.connection() as conn:
    with conn.cursor() as cur:
```

- **Outer `with`**: Manages database connection from the pool
- **Inner `with`**: Creates a cursor to execute operations
- Both close automatically when their blocks exit

### 3. **Bulk insert operation**
```python
cur.executemany(
    "INSERT INTO products_raw (product) VALUES (%s)",
    [(Json(product.model_dump()),) for product in products]
)
```

This is the heart of the function! Let's break it down:

#### **`executemany()` vs `execute()`**

❌ **Inefficient way (loop with execute):**
```python
# This makes N database round-trips!
for product in products:
    cur.execute(
        "INSERT INTO products_raw (product) VALUES (%s)",
        (Json(product.model_dump()),)
    )
# If you have 1000 products = 1000 separate database calls! 😰
```

✅ **Efficient way (executemany):**
```python
# This makes 1 database round-trip!
cur.executemany(
    "INSERT INTO products_raw (product) VALUES (%s)",
    [(Json(product.model_dump()),) for product in products]
)
# 1000 products = 1 single database call! 🚀
```

#### **List comprehension explanation**
```python
[(Json(product.model_dump()),) for product in products]
```

This creates a list of tuples:
```python
[
    (Json({'product_id': 'SKU-001', 'name': 'Mouse', ...}),),
    (Json({'product_id': 'SKU-002', 'name': 'Keyboard', ...}),),
    (Json({'product_id': 'SKU-003', 'name': 'Monitor', ...}),),
    ...
]
```

**Why a tuple with one element `(value,)`?**
- `executemany()` expects a list of tuples
- Each tuple represents parameters for one insert operation
- Even though we only have one parameter, we still need a tuple
- `,` after the value makes it a tuple: `(value,)` vs `(value)`

#### **`Json()` wrapper**
```python
Json(product.model_dump())
```

- `product.model_dump()` → converts Pydantic model to dictionary
- `Json()` → wrapper from psycopg that tells PostgreSQL to store this as JSONB
- PostgreSQL can then index and query within the JSON structure

### 4. **Commit transaction**
```python
conn.commit()
```

- Saves all inserts permanently to the database
- Without `commit()`, changes would rollback when the connection closes

### 5. **Response**
```python
return {"inserted": len(products)}
```

Returns the number of products that were inserted:
```json
{
  "inserted": 100
}
```

---

## Complete Example with Test Data

### Database schema
```sql
CREATE TABLE products_raw (
    id SERIAL PRIMARY KEY,
    product JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Request example (Postman/curl)
```json
POST http://localhost:8000/products/bulk

[
  {
    "product_id": "SKU-001",
    "name": "Wireless Mouse",
    "price": 299.0,
    "currency": "SEK",
    "tags": ["wireless", "ergonomic"]
  },
  {
    "product_id": "SKU-002",
    "name": "Mechanical Keyboard",
    "price": 899.0,
    "currency": "SEK",
    "tags": ["mechanical", "rgb"]
  },
  {
    "product_id": "SKU-003",
    "name": "USB-C Hub",
    "price": 449.0,
    "currency": "SEK",
    "tags": ["usb-c", "adapter"]
  }
]
```

### Response
```json
{
  "inserted": 3
}
```

### Data in database after insert
```sql
SELECT id, product FROM products_raw;
```

| id | product |
|----|---------|
| 1 | `{"product_id": "SKU-001", "name": "Wireless Mouse", ...}` |
| 2 | `{"product_id": "SKU-002", "name": "Mechanical Keyboard", ...}` |
| 3 | `{"product_id": "SKU-003", "name": "USB-C Hub", ...}` |

---

## Performance Comparison

### Scenario: Insert 1000 products

#### ❌ **With loop and execute() (inefficient):**
```python
# Slow method
for product in products:  # 1000 iterations
    cur.execute(...)      # 1000 database round-trips
    
# Total time: ~10-30 seconds (depending on network latency)
```

**Why slow?**
- Each `execute()` = a separate database round-trip
- Network latency per request: ~10-30ms
- 1000 requests × 20ms = 20 seconds just in wait time!

#### ✅ **With executemany() (efficient):**
```python
# Fast method
cur.executemany(...)  # 1 database round-trip with all values

# Total time: ~0.5-2 seconds
```

**Why fast?**
- Only ONE database round-trip
- All data sent in the same packet
- PostgreSQL optimizes batch insert internally

**Performance gain:** 10-50x faster! 🚀

---

## Error Handling and Transactions

### What happens if one insert fails?

```python
@app.post("/products/bulk")
def products_bulk(products: list[ProductSchema]):
    try:
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.executemany(
                    "INSERT INTO products_raw (product) VALUES (%s)",
                    [(Json(product.model_dump()),) for product in products]
                )
            conn.commit()  # ← If this succeeds: all inserts saved
        return {"inserted": len(products)}
    
    except Exception as e:
        # If something goes wrong: ALL inserts are rolled back (transaction rollback)
        return {"error": str(e), "inserted": 0}
```

**IMPORTANT:** `executemany()` is atomic:
- Either **ALL** products are saved
- Or **NO** products are saved
- There is no middle ground!

---

## Improvements and Best Practices

### 1. **Add error handling**
```python
from fastapi import HTTPException

@app.post("/products/bulk")
def products_bulk(products: list[ProductSchema]):
    if not products:
        raise HTTPException(status_code=400, detail="Products list cannot be empty")
    
    try:
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.executemany(
                    "INSERT INTO products_raw (product) VALUES (%s)",
                    [(Json(product.model_dump()),) for product in products]
                )
            conn.commit()
        return {"inserted": len(products)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
```

### 2. **Add max quantity validation**
```python
@app.post("/products/bulk")
def products_bulk(products: list[ProductSchema]):
    MAX_BULK_SIZE = 1000
    
    if len(products) > MAX_BULK_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Maximum {MAX_BULK_SIZE} products per bulk insert"
        )
    
    # ... rest of code
```

### 3. **Return more detailed info**
```python
@app.post("/products/bulk")
def products_bulk(products: list[ProductSchema]):
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.executemany(
                "INSERT INTO products_raw (product) VALUES (%s) RETURNING id",
                [(Json(product.model_dump()),) for product in products]
            )
            inserted_ids = [row[0] for row in cur.fetchall()]
        conn.commit()
    
    return {
        "inserted": len(products),
        "ids": inserted_ids,
        "first_id": inserted_ids[0] if inserted_ids else None,
        "last_id": inserted_ids[-1] if inserted_ids else None
    }
```

---

## Complete Annotated Code

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from psycopg_pool import ConnectionPool
from psycopg.types.json import Json

app = FastAPI()
pool = ConnectionPool("postgresql://postgres:password@localhost:5432/demo_5")

class ProductSchema(BaseModel):
    product_id: str
    name: str
    price: float
    currency: str = "SEK"

@app.post("/products/bulk")
def products_bulk(products: list[ProductSchema]):
    """
    Bulk insert endpoint for inserting multiple products simultaneously.
    
    Args:
        products: List of ProductSchema objects to insert
        
    Returns:
        Dictionary with number of inserted products
        
    Raises:
        HTTPException: If database operation fails
    """
    # Validate input
    if not products:
        raise HTTPException(status_code=400, detail="Empty products list")
    
    try:
        # Open connection from pool
        with pool.connection() as conn:
            # Create cursor to execute operations
            with conn.cursor() as cur:
                # executemany: Efficient bulk insert
                # - Takes SQL query with placeholder (%s)
                # - Takes list of tuples with values
                # - Executes all inserts in a single database round-trip
                cur.executemany(
                    "INSERT INTO products_raw (product) VALUES (%s)",
                    [
                        # For each product:
                        # 1. product.model_dump() → convert Pydantic to dict
                        # 2. Json(...) → wrapper for JSONB serialization
                        # 3. (...,) → tuple with one element (required by executemany)
                        (Json(product.model_dump()),) 
                        for product in products
                    ]
                )
            # Save all changes permanently
            conn.commit()
        
        # Return success message
        return {
            "inserted": len(products),
            "status": "success"
        }
        
    except Exception as e:
        # On error: transaction is automatically rolled back
        raise HTTPException(
            status_code=500,
            detail=f"Failed to insert products: {str(e)}"
        )
```

---

## Summary

| Aspect | Description |
|--------|-------------|
| **What does it do?** | Inserts multiple products simultaneously (bulk operation) |
| **Why efficient?** | `executemany()` = 1 database round-trip instead of N |
| **Data format** | Products saved as JSONB in PostgreSQL |
| **Transaction safety** | Either all or none are saved (atomic) |
| **Performance gain** | 10-50x faster than loop with `execute()` |
| **Use case** | Importing large datasets, batch processing |

**Key Insight:** When you need to insert many rows, ALWAYS use `executemany()` instead of looping with `execute()`. It's one of the biggest performance optimizations you can make! 🎯

---

## Final Notes

These three code analysis examples demonstrate fundamental patterns in FastAPI and PostgreSQL development:

1. **Resource management** - Using context managers (`with`) to ensure proper cleanup
2. **Data transformation** - Converting between Pydantic models and dictionaries with `model_dump()`
3. **Performance optimization** - Using bulk operations (`executemany()`) for efficiency

Mastering these patterns will help you build robust, efficient data platform applications! 🚀
