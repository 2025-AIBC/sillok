from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, JSON, UUID
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects.postgresql import BYTEA
from sqlalchemy.orm import relationship
from database import Base
import datetime
import pytz
import hashlib

KST = pytz.timezone("Asia/Seoul")

class User(Base):
    __tablename__ = "users"
    user_id = Column(String(64), primary_key=True, index=True)
    name = Column(String)
    account = Column(String, unique=True, index=True)
    password = Column(String)
    created_date = Column(DateTime, default=datetime.datetime.now(datetime.UTC))
    email = Column(String, unique=True)
    birthday = Column(DateTime)
    gender = Column(String)
    
    files = relationship("File", back_populates="owner")

    def __init__(self, name, account, password, email, birthday, gender):
        self.user_id = hashlib.sha3_256(account.encode()).hexdigest()
        self.name = name
        self.account = account
        self.password = password
        self.email = email
        self.birthday = birthday
        self.gender = gender

class File(Base):
    __tablename__ = "files"
    
    CID = Column(String, primary_key=True, index=True)
    fname = Column(String)
    type = Column(String)
    last_update = Column(DateTime, default=lambda: datetime.datetime.now(KST))
    is_deleted = Column(Boolean, default=False)
    user_id = Column(String, ForeignKey("users.user_id"))
    TXHash = Column(String)
    content = Column(String)
    
    owner = relationship("User", back_populates="files")

class LangchainPGEmbedding(Base):
    __tablename__ = "langchain_pg_embedding"
    
    id = Column(String, primary_key=True, nullable=False)  # character varying
    collection_id = Column(UUID, ForeignKey("langchain_pg_collection.uuid", ondelete='CASCADE'))
    embedding = Column(Vector(dim=3072))  # Pgvector의 벡터 타입, 차원(dim)을 데이터에 맞게 설정
    document = Column(String)  # character varying
    cmetadata = Column(JSON)  # JSONB 타입