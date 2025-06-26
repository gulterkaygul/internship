from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy import create_engine
from passlib.context import CryptContext

Base = declarative_base()

engine = create_engine('postgresql://postgres:supersecret@my-postgres:5432/postgres', echo=True)
Session = sessionmaker(bind=engine)
session = Session()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

class Admin(Base):
    __tablename__ = 'admins'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password = Column(String)  # hashed password

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    password = Column(String)  # hashed password
    email = Column(String, unique=True)

class Book(Base):
    __tablename__ = 'books'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    is_borrowed = Column(Boolean, default=False)
    borrowed_by = Column(Integer, ForeignKey('users.id'), nullable=True)

    user = relationship("User")