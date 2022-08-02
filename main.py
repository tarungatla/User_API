import os
from fastapi import FastAPI, HTTPException,status,Depends
from sqlalchemy import false
from models import  User, UserIn_Pydantic, User_Pydantic
from tortoise.contrib.fastapi import HTTPNotFoundError, register_tortoise
from pydantic import BaseModel
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from validate_email import validate_email
from time import time
from datetime import timedelta,datetime
from passlib.context import CryptContext

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

password = os.environ.get('POSTGRESQL_PASSWORD')
class Password(BaseModel):
    old_password: str
    new_password: str

class Token(BaseModel):
    access_token: str    #jwt data
    token_type: str

class Form(BaseModel):
    email: str
    password: str

class Name(BaseModel):
    first_name: str
    middle_name: str
    last_name:str

class User_Details(BaseModel):
    email: str
    phone: str
    password: str
    first_name: str
    last_name: str
    middle_name: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/user/login")

def password_check(passwd):

	SpecialSym =['!','"','#','$','%','&','(',')','*','+',',','-','.','/',':',';','<','=','>','?','@','[',']','^','_','`','{','|','}','~']
	
	if len(passwd) < 8:
		return 'Password should have at least 8 characters'
		
	if len(passwd) > 16:
		return 'Password can have at most 16 characters'
		
	if not any(char.isdigit() for char in passwd):
		return 'Password should have at least one numeral'
		
	if not any(char.isupper() for char in passwd):
		return 'Password should have at least one uppercase letter'
		
	if not any(char.islower() for char in passwd):
		return 'Password should have at least one lowercase letter'
		
	if not any(char in SpecialSym for char in passwd):
		return 'Password should have at least special character'
	
	return 'ok'

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password:str):
    return pwd_context.hash(password)

async def get_user(email:str):
    try:
      user = await User_Pydantic.from_queryset_single(User.get(email=email))
    except:
      return None
    return user

app = FastAPI()

@app.get('/api/v1/users')
async def users( token:str = Depends(oauth2_scheme)):
    users = await User_Pydantic.from_queryset(User.all())
    temp = []
    for user in users:
        if user.status == 1 :
            user.status = "Active"
            temp.append(user)
        if user.status == 2:
            user.status = "Inactive"
            temp.append(user)
    return temp

@app.get('/api/v1/users/{user_id}')
async def get_user(user_id: int, token:str = Depends(oauth2_scheme)):
    user = await User_Pydantic.from_queryset_single(User.get(user_id=user_id))
    if user.status == 3: 
        raise HTTPException(status_code=401, detail="User not found")

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

    return {
        "email": user.email,
        "phone": user.phone,
        # "password": user.password,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "middle_name": user.middle_name,
        # "created": user.created,
        # "updated": user.updated,
        "accessed": round(time()),
        "status": "Active" if user.status==1 else "Inactive"
    }

@app.post('/api/v1/users/')               #created and updated will not be sent to response
async def create(user: User_Details, token:str = Depends(oauth2_scheme)):
    is_valid = validate_email(user.email)
    try:
        user = await User.get(email=user.email) 
        return {"message":"This email is already taken"}  
    except:
        try:
            user = await User.get(phone=user.phone)  
            return {"message":"This phone number is already taken"}
        except:
            if is_valid:
                temp = {
                    "email": user.email,
                    "phone": user.phone,
                    "password": get_password_hash(user.password),
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "middle_name": user.middle_name,
                    "created": round(time()),
                    "updated": round(time()),
                    "accessed": round(time()),
                    "status": 1   #send string valuess like acitve deleted 
                    }
                temp1 = UserIn_Pydantic(**temp)
                obj = await User.create(**temp1.dict(exclude_unset=True))  #exlcudes the unset fields i.e user_id https://pydantic-docs.helpmanual.io/usage/exporting_models/#modeldict
                return {
                    "user_id": obj.user_id,
                    "email": user.email,
                    "phone": user.phone,
                    "password": get_password_hash(user.password),
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "middle_name": user.middle_name,
                    "accessed": round(time()),
                    "status": "active"  #send string valuess like acitve deleted 
                    }
                #    return await User_Pydantic.from_tortoise_orm(obj)            #created and updated will not be returned
            else: raise HTTPException(status_code=400, detail="Email is not valid")


@app.put('/api/v1/users/{user_id}', responses={404: {"model": HTTPNotFoundError}})       #Name...........................
async def update(user_id: int, user: Name, token:str = Depends(oauth2_scheme)):
    try:
      obj = await User_Pydantic.from_queryset_single(User.get(user_id=user_id))
    except:
      raise HTTPException(status_code=404, detail="User not found")

    temp = {
        "email": obj.email,
        "phone": obj.phone,
        "password": obj.password,
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

    return {
        "email": obj.email,
        "phone": obj.phone,
        # "password": obj.password,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "middle_name": user.middle_name,
        "accessed": temp["accessed"],
        "status": "active" 
    }
    # return await User_Pydantic.from_queryset_single(User.get(user_id=user_id))
    

@app.delete('/api/v1/users/{user_id}',response_model=User_Pydantic)
async def delete(user_id: int, token:str = Depends(oauth2_scheme)):
    user = await UserIn_Pydantic.from_queryset_single(User.get(user_id=user_id))
    if user:
         user.status = 3               #3 for delete
         await User.filter(user_id= user_id).update(**user.dict(exclude_unset=True))  
         return await User_Pydantic.from_queryset_single(User.get(user_id=user_id))
    else:
        raise HTTPException(status_code=404, detail="User not found")


@app.post('/api/v1/users/changepassword/{user_id}')
async def changePassword(user_id: int, password:Password, token:str = Depends(oauth2_scheme)):
    try:
        user =  await User_Pydantic.from_queryset_single(User.get(user_id=user_id))
        if(verify_password(password.old_password,user.password )):
            user = await UserIn_Pydantic.from_queryset_single(User.get(user_id=user_id))
            flag = password_check(password.new_password)
            if flag == 'ok':
                user.password = get_password_hash(password.new_password)
                await User.filter(user_id= user_id).update(**user.dict(exclude_unset=True))  
                return {"message":"Passowrd changed successfully","data":await User_Pydantic.from_queryset_single(User.get(user_id=user_id))}   
            else:
                return {"detail" : flag}
        else:
            raise HTTPException(status_code=401, detail="Wrong password")
    except:
        raise HTTPException(status_code=404, detail="User not found")



async def authenticate_user( email: str, password: str):
    try:
      user = await User_Pydantic.from_queryset_single(User.get(email=email))
      if user.status == 3:
        return False
    except:
      return False
    if not verify_password(password, user.password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})          #adding expire time
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt




@app.post("/api/v1/user/login" )
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)   #while using form it is compulsory to use username & password only
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"email": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        user = await User.get(email=payload.get('email'))
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail='Invalid username or password'
        )

    return await User_Pydantic.from_tortoise_orm(user)

@app.get("/api/v1/users/me/", response_model = User_Pydantic)
async def get_user(user: User_Pydantic = Depends(get_current_user)):
    return user   


@app.get("/api/v1/users/forgotpassword/")
async def forgot_password(email:str, token:str = Depends(oauth2_scheme)):
    return {"message": "Password changed successfully","email":email}

register_tortoise(
    app,
    db_url=f"postgres://postgres:{password}@localhost:5432/User",
    modules={'models': ['models']},
    generate_schemas=True,
    add_exception_handlers=True,
)


#Table for adding  extra values
#id    user_id(foreign key)   type(which field ) and the value