from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, Float, String, ForeignKey
from sqlalchemy.dialects.postgresql import JSON

Base = declarative_base()


class User(Base):

    __tablename__ = "users"

    id = Column(String(255), primary_key=True) # id is the email
    name = Column(String(50), nullable=False)
    facebook = Column(JSON(), nullable=False)


class Category(Base):

    __tablename__ = "categories"

    id = Column(String(16), primary_key=True)
    access_key = Column(String(8), nullable=False)

    label = Column(String(50))
    parent_id = Column(String(16), ForeignKey('categories.id'))

    subcategories = relationship("Category")


class Entry(Base):

    __tablename__ = "entries"

    id = Column(Integer, autoincrement=True, primary_key=True)
    access_key = Column(String(8), nullable=False)

    type = Column(String(8), nullable=False)
    amount = Column(Float, nullable=False)
    category_id = Column(String(16), ForeignKey('categories.id'))

    category = relationship("Category")