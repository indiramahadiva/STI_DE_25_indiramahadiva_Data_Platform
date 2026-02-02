# Deletion of **name** -why ?

## Servlet Container

- Hosting of Application (locally)
- FastApi introduces this new concept
- Remove tradional 'play/start' button
- Requires FastApi - start command (to run app)

## FastAPI

- Install: $ pip install "fastapi[standard]"
  - Bonus: uv alternative for perfomance
  - Bonus : CTRL + F (Filter for "succes")
- START APP: $ fastapi dev FILENMAE.py
- Keep main.py in root folder (best practice)

## Endpoint

- API & URL related
- Consists of a path: "/example"
- Accompanied by a HTTP-Method (GET, POST, PUT, DELETE)

## Decorator

- Refers to the @ symbol
- (Difference in how function executes)
- Runs logic from external decorator function
  - (Function over function)
- returns JSON data (automatic conversion)

```python
@decorator
def test_function():
```

## URL

Example URL: https://www.google.com/search?q=bananas&

- In this example we see a dynamic parameter
  - q == query (just a variable name)
  - ? == start of query
  - What comes after = is Dynamic_Value (client input)

## Pydantic

- Uses Schema (Define Logical data type structure)
- Class based
- Used for Data Validation
- Facilitates conversion of JSON -> Python objects
- Best pratice - (separated from its own package)
- Includes 'BaseModel' within
