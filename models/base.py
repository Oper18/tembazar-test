# coding: utf-8

import json
import datetime

from typing import Union

from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy.types as types
from enum import Enum


Base = declarative_base()


class ChoiceType(types.TypeDecorator):

    impl = types.Integer
    DEFAULT = 1

    def __init__(self, choices, **kw):
        self.choices = dict(choices)
        super(ChoiceType, self).__init__(**kw)

    def process_bind_param(self, value, dialect):
        return [k for k, v in self.choices.items() if v == value][0]

    def process_result_value(self, value, dialect):
        return self.choices[value]

    def __hash__(self):
        return hash(json.dumps(self.choices))


class BaseDataObj(object):
    __fields__ = list()

    def __init__(self, obj):
        self.obj = obj
        self.__fields__ = [c.name for c in obj.__table__.columns]
        self.add_attrs()

    def add_attrs(self):
        for f in self.__fields__:
            setattr(self, f, getattr(self.obj, f, None))

    def as_dict(self):
        res = dict()
        for field in self.__fields__:
            if isinstance(getattr(self, field), datetime.datetime) or \
                isinstance(getattr(self, field), datetime.date):
                res[field] = getattr(self, field).isoformat()
            else:
                res[field] = getattr(self, field)

        return res


class BaseModel:

    def as_dict(self):
        res = {}
        for c in self.__table__.columns:
            try:
                if c in ["salt", "password"]:
                    continue
                if isinstance(getattr(self, c.name), datetime.datetime) or \
                    isinstance(getattr(self, c.name), datetime.date):
                    res[c.name] = getattr(self, c.name).isoformat()
                else:
                    res[c.name] = getattr(self, c.name)
            except:
                continue
        return res

    def as_data_obj(self):
        return BaseDataObj(obj=self)


class AnonymousUser(BaseModel):
    id = None
    admin = False
    username = "anonymous"

    @property
    def is_anonymous(self):
        return True
