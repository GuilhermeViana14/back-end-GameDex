from pydantic import BaseModel

class UserCreate(BaseModel):
    first_name: str
    email: str
    password: str

class UserResponse(BaseModel):
    first_name: str
    email: str

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: str
    password: str