from fastapi import FastAPI, HTTPException
from models import User, UserIn_Pydantic, User_Pydantic
from tortoise.contrib.fastapi import HTTPNotFoundError, register_tortoise
from pydantic import BaseModel

class Message(BaseModel):
    message: str

app = FastAPI()

@app.post('/usesr/', response_model = User_Pydantic)
async def create(user: UserIn_Pydantic):
    obj = await User.create(**user.dict(exclude_unset=True))  #exlcudes the unset fields https://pydantic-docs.helpmanual.io/usage/exporting_models/#modeldict
    return await User_Pydantic.from_tortoise_orm(obj)


register_tortoise(
    app,
    db_url="postgres://postgres:nurataltag@localhost:5432/User",
    modules={'models': ['models']},
    generate_schemas=True,
    add_exception_handlers=True,
)