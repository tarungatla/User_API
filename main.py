from fastapi import FastAPI, HTTPException
from models import User, User_Details, UserIn_Pydantic, User_Pydantic, UserDetails_Pydantic
from tortoise.contrib.fastapi import HTTPNotFoundError, register_tortoise
from pydantic import BaseModel
from validate_email import validate_email
from time import time

class Password(BaseModel):
    old_password: str
    new_password: str


app = FastAPI()

@app.get('/users')
async def users():
    users = await User_Pydantic.from_queryset(User.all())
    # print(users)
    return users

@app.get('/users/{user_id}', response_model=User_Pydantic)
async def get_user(user_id: int):
    user = await User_Pydantic.from_queryset_single(User.get(user_id=user_id))
    temp = {
        "email": user.email,
        "phone": user.phone,
        "password": user.password,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "middle_name": user.middle_name,
        "created": user.created,
        "updated": user.updated,
        "accessed": round(time()),
        "status": 1
        }
    temp1 = UserIn_Pydantic(**temp)
    await User.filter(user_id= user_id).update(**temp1.dict(exclude_unset=True))
    return await User_Pydantic.from_queryset_single(User.get(user_id=user_id))

@app.post('/users/',response_model=User_Pydantic)
async def create(user: UserDetails_Pydantic):
    is_valid = validate_email(user.email)
    if is_valid:
       temp = {
        "email": user.email,
        "phone": user.phone,
        "password": user.password,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "middle_name": user.middle_name,
        "created": round(time()),
        "updated": round(time()),
        "accessed": round(time()),
        "status": 1
        }
       temp1 = UserIn_Pydantic(**temp)
       obj = await User.create(**temp1.dict(exclude_unset=True))  #exlcudes the unset fields i.e user_id https://pydantic-docs.helpmanual.io/usage/exporting_models/#modeldict
       return await User_Pydantic.from_tortoise_orm(obj)
    else:
        raise HTTPException(status_code=404, detail="Email is not valid")


@app.put('/users/{user_id}', response_model=User_Pydantic, responses={404: {"model": HTTPNotFoundError}})
async def update(user_id: int, user: UserDetails_Pydantic):
    obj = await User_Pydantic.from_queryset_single(User.get(user_id=user_id))

    is_valid = validate_email(user.email)
    if is_valid:
       temp = {
        "email": user.email,
        "phone": user.phone,
        "password": user.password,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "middle_name": user.middle_name,
        "created": obj.created,
        "updated": round(time()),
        "accessed": round(time()),
        "status": 1
        }
       temp1 = UserIn_Pydantic(**temp)
       await User.filter(user_id= user_id).update(**temp1.dict(exclude_unset=True))
       return await User_Pydantic.from_queryset_single(User.get(user_id=user_id))
    else:
      raise HTTPException(status_code=404, detail="Email is not valid")


@app.delete('/users/{user_id}',response_model=User_Pydantic)
async def delete(user_id: int):
    user = await UserIn_Pydantic.from_queryset_single(User.get(user_id=user_id))
    if user:
         user.status = 3               #3 for delete
         await User.filter(user_id= user_id).update(**user.dict(exclude_unset=True))  
         return await User_Pydantic.from_queryset_single(User.get(user_id=user_id))
    else:
        raise HTTPException(status_code=404, detail="User not found")


@app.post('/users/changepassword{user_id}')
async def changePassword(user_id: int, password:Password):
    user =  await User_Pydantic.from_queryset_single(User.get(user_id=user_id))
    if(user.password != password.old_password):
        raise HTTPException(status_code=401, detail="Wrong password")
    else:
     user = await UserIn_Pydantic.from_queryset_single(User.get(user_id=user_id))
     user.password = password.new_password
     await User.filter(user_id= user_id).update(**user.dict(exclude_unset=True))  
     return {"message":"Passowrd changed successfully","data":await User_Pydantic.from_queryset_single(User.get(user_id=user_id))}



   

register_tortoise(
    app,
    db_url="postgres://postgres:nurataltag@localhost:5432/User",
    modules={'models': ['models']},
    generate_schemas=True,
    add_exception_handlers=True,
)
