from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Users 스키마
class UserBase(BaseModel):
    user_id: Optional[str] = None
    name: Optional[str] = None
    account: Optional[str] = None
    email: Optional[str] = None
    birthday: Optional[datetime] = None
    gender: Optional[str] = None
    created_date: Optional[datetime] = None

    class Config:
        orm_mode = True

class UserCreate(UserBase):
    name: str
    account: str
    password: str
    email: str
    birthday: datetime
    gender: str

class User(UserBase):
    user_id: str
    name: str
    account: str
    email: str
    birthday: datetime
    gender: str
    created_date: datetime

    class Config:
        orm_mode = True


# Files 스키마
class FileBase(BaseModel):
    CID: Optional[str] = None
    fname: Optional[str] = None
    type: Optional[str] = None
    last_update: Optional[datetime] = None
    is_deleted: Optional[bool] = None
    user_id: Optional[str] = None
    TXHash: Optional[str] = None
    content: Optional[str] = None

    class Config:
        orm_mode = True

class FileCreate(FileBase):
    user_id: str
    fname: str
    type: str
    content: str

class FileUpdate(FileBase):
    user_id: str
    fname: str
    type: str
    content: str
    CID: str

class File(FileBase):
    CID: str
    fname: str
    type: str
    last_update: datetime
    is_deleted: bool
    user_id: str
    TXHash: str
    content: str

    class Config:
        orm_mode = True


# 유저 인증을 위한 스키마
class AuthRequest(BaseModel):
    user_id: str
    user_pw: str

class ReadRequest(BaseModel):
    user_id: str

class chatRequest(BaseModel):
    question: str

class fileDelete(BaseModel):
    cid: str