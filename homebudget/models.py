from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, Float, String, ForeignKey

Base = declarative_base()


class Category(Base):

    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    access_key = Column(String(8), nullable=False)

    label = Column(String(50))
    parent_id = Column(Integer, ForeignKey('categories.id'))

    subcategories = relationship("Category")


class Entry(Base):

    __tablename__ = "entries"

    id = Column(Integer, primary_key=True)
    access_key = Column(String(8), nullable=False)

    type = Column(String(8), nullable=False)
    amount = Column(Float, nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'))

    category = relationship("Category")