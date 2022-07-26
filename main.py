from fastapi import FastAPI, HTTPException
from models import User, UserIn_Pydantic, User_Pydantic
from tortoise.contrib.fastapi import HTTPNotFoundError, register_tortoise
from pydantic import BaseModel
from validate_email import validate_email

class Message(BaseModel):
    message: str

app = FastAPI()

@app.get('/users')
async def get_user():
    users = await User_Pydantic.from_queryset(User.all())
    # print(users)
    return users

@app.get('/user/{user_id}', response_model=User_Pydantic)
async def get_user(user_id: int):
    return await User_Pydantic.from_queryset_single(User.get(user_id=user_id))

@app.post('/usesr/',response_model=User_Pydantic)
async def create(user: UserIn_Pydantic):
    is_valid = validate_email(user.email)
    if is_valid:
       obj = await User.create(**user.dict(exclude_unset=True))  #exlcudes the unset fields i.e user_id https://pydantic-docs.helpmanual.io/usage/exporting_models/#modeldict
       return await User_Pydantic.from_tortoise_orm(obj)
    else:
        raise HTTPException(status_code=404, detail="Email is not valid")


@app.put('/user/{user_id}', response_model=User_Pydantic, responses={404: {"model": HTTPNotFoundError}})
async def update(user_id: int, user: UserIn_Pydantic):
    await User.filter(user_id= user_id).update(**user.dict(exclude_unset=True))
    return await User_Pydantic.from_queryset_single(User.get(user_id=user_id))

@app.delete('/user/{user_id}',response_model=User_Pydantic)
async def delete(user_id: int):
    user = await UserIn_Pydantic.from_queryset_single(User.get(user_id=user_id))
    if user:
         user.status = 2                #2 for delete
         await User.filter(user_id= user_id).update(**user.dict(exclude_unset=True))  
         return await User_Pydantic.from_queryset_single(User.get(user_id=user_id))
    else:
        raise HTTPException(status_code=404, detail="User not found")
   

register_tortoise(
    app,
    db_url="postgres://postgres:nurataltag@localhost:5432/User",
    modules={'models': ['models']},
    generate_schemas=True,
    add_exception_handlers=True,
)
