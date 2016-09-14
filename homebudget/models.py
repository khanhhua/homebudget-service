from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, Float, String, ForeignKey
from sqlalchemy.dialects.postgresql import JSON

Base = declarative_base()


class Serializable(object):
    def to_dict(self):
        fields = type(self). __dict__.get('__serialize__')

        result = dict()
        for field in fields:
            if hasattr(self, field):
                result[field] = getattr(self, field)

        return result


class User(Base):

    __tablename__ = "users"

    id = Column(String(255), primary_key=True) # id is the email
    name = Column(String(50), nullable=False)
    facebook = Column(JSON(), nullable=False)


class Category(Serializable, Base):

    __tablename__ = "categories"
    __serialize__ = ['id', 'label']

    id = Column(String(16), primary_key=True)
    access_key = Column(String(8), nullable=False)

    label = Column(String(50))
    parent_id = Column(String(16), ForeignKey('categories.id'))

    subcategories = relationship("Category")


class Entry(Serializable, Base):

    __tablename__ = "entries"
    __serialize__ = ['id', 'type', 'amount', 'category_id']

    id = Column(Integer, autoincrement=True, primary_key=True)
    access_key = Column(String(8), nullable=False)

    type = Column(String(8), nullable=False)
    amount = Column(Float, nullable=False)
    category_id = Column(String(16), ForeignKey('categories.id'))

    category = relationship("Category")
