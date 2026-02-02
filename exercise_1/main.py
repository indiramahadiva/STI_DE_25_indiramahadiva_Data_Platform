from typing import Union
from fastapi import FastAPI

app = FastAPI(title="My First API")


@app.get("/")
def root():
    return {"Hello": "World"}
