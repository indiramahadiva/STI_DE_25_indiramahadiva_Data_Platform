import requests
from typing import Union

from fastapi import FastAPI, status

from schema.fox import FoxSchema
from schema.user import UserSchema, UserSchemaResponse

userList: list[UserSchema] = [
    UserSchema(username="Benny", password="123", is_enabled="True"),
    UserSchema(username="Frida", password="321", is_enabled="True"),
    UserSchema(username="Tommy", password="abc", is_enabled="False"),
]

app = FastAPI(title="My First API APP")


@app.get("/")
def root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")  # localhost: 8000/items/249?color=black
def get_item(item_id: int, color: Union[str, None] = None):
    return {"item_id": item_id, "color": color}


@app.get("/users", response_model=list[UserSchemaResponse])
def get_users() -> list[UserSchemaResponse]:
    return userList


@app.post("/users", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
def post_user(user: UserSchema) -> UserSchema:
    userList.append(user)
    return user


@app.get("/fox", response_model=FoxSchema)
def get_fox():
    response = requests.get("https://randomfox.ca/floof/")
    result_json = response.json()
    print(f"DEBUGGING{result_json}")

    fox = FoxSchema(**result_json)  # Convert JSON -> Python Object
    return fox
