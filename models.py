from enum import unique
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
    created = fields.IntField()
    updated = fields.IntField()
    accessed = fields.IntField()
    status = fields.IntField()
    

class User_Details(models.Model):
    user_id = fields.IntField(pk=True)
    email = fields.CharField(max_length=250,unique = True)
    phone = fields.CharField(max_length=250,unique = True)
    password = fields.CharField(max_length=250)
    first_name = fields.CharField(max_length=250)
    last_name =  fields.CharField(max_length=250)
    middle_name = fields.CharField(max_length=250)


class Name(models.Model):
    user_id = fields.IntField(pk=True)
    first_name = fields.CharField(max_length=250)
    last_name =  fields.CharField(max_length=250)
    middle_name = fields.CharField(max_length=250)

User_Pydantic = pydantic_model_creator(User, name="User") #pydantic model for tortoise
UserIn_Pydantic = pydantic_model_creator(User, name="UserIn", exclude_readonly=True)  #does not take read only values
UserDetails_Pydantic = pydantic_model_creator(User_Details, name="User_Details", exclude_readonly=True)  #does not take read only values
Name_Pydantic = pydantic_model_creator(Name,name="Name",exclude_readonly=True)
