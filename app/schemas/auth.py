from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    full_name: str
    username: str
    phone_number: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    full_name: str
    username: str
    phone_number: str
    email: str
