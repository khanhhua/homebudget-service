from os import urandom
import binascii
from time import time

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, CHAR
from sqlalchemy.dialects.postgresql import JSON

from datetime import datetime

from hashids import Hashids

Base = declarative_base()

hasher = Hashids(min_length=16)

class Serializable(object):
    def to_dict(self, extra_fields=None):
        fields = type(self). __dict__.get('__serialize__')

        result = dict()
        for field in fields:
            if hasattr(self, field):
                value = getattr(self, field)
                if type(value) is datetime:
                    result[field] = value.isoformat()
                else:
                    result[field] = value

        if extra_fields is not None:
            for field, value in extra_fields.items():
                result[field] = value

        return result


class User(Base):

    __tablename__ = "users"

    id = Column(String(255), primary_key=True) # id is the email
    name = Column(String(50), nullable=False)
    facebook = Column(JSON(), nullable=False)

    # Financial settings
    currency = Column(String(3), nullable=False, default='USD')

    # Licensing
    access_key = Column(CHAR(8), nullable=False)


class Category(Serializable, Base):

    __tablename__ = "categories"
    __serialize__ = ['id', 'label']

    id = Column(CHAR(16), primary_key=True)
    access_key = Column(CHAR(8), nullable=False)

    label = Column(String(50))
    parent_id = Column(String(16), ForeignKey('categories.id'))

    subcategories = relationship("Category")


class Entry(Serializable, Base):

    __tablename__ = "entries"
    __serialize__ = ['id', 'type', 'accounted_on', 'amount', 'category_id']

    INCOME = 'income'
    EXPENSE = 'expense'

    id = Column(Integer, autoincrement=True, primary_key=True)
    access_key = Column(CHAR(8), nullable=False)

    type = Column(String(8), nullable=False)
    amount = Column(Float, nullable=False)
    category_id = Column(String(16), ForeignKey('categories.id'))
    created_on = Column(DateTime(timezone=True), default=datetime.utcnow)
    accounted_on = Column(DateTime(timezone=True), nullable=False)

    category = relationship("Category")


def setup_new_user(db, user_data):
    access_key = binascii.hexlify(urandom(4))
    if access_key is None:
        raise Exception('Could not create access key')

    user = User(id=user_data['email'],
                name=user_data['name'],
                access_key=access_key)
    db.add(user)

    categories = ['Housing',
                  'Departmental',
                  'Utilities',
                  'Food',
                  'Education',
                  'Transportation',
                  'Entertainment',
                  'Home Office']
    for label in categories:
        id_ = hasher.encode(int(time() * 1000000))
        category = Category(id=id_,
                            access_key=access_key,
                            label=label)
        db.add(category)

    db.commit()

    return user