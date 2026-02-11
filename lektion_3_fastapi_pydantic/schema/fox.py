from pydantic import BaseModel


# Schema must match API data structure
class FoxSchema(BaseModel):
    image: str
    link: str
