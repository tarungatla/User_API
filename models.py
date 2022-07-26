from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator

class User(models.Model):
    user_id = fields.IntField(pk=True)
    email = fields.CharField(max_length=250,unique=True)
    phone = fields.CharField(max_length=250,unique=True)
    password = fields.CharField(max_length=250)
    first_name = fields.CharField(max_length=250)
    last_name =  fields.CharField(max_length=250)
    middle_name = fields.CharField(max_length=250)
    created = fields.CharField(max_length=250)
    updated = fields.CharField(max_length=250)
    accessed = fields.CharField(max_length=250)
    status = fields.IntField()
    

User_Pydantic = pydantic_model_creator(User, name="User") #pydantic model for tortoise
UserIn_Pydantic = pydantic_model_creator(User, name="UserIn", exclude_readonly=True)  #does not take read only values

