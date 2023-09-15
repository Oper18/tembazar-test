# config: utf-8

import datetime
from enum import Enum

from sqlalchemy import (
    DateTime,
    String,
    ForeignKey,
    Boolean,
    false,
)
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from .base import (
    Base,
    BaseModel,
    AnonymousUser,
)
from util import password_hash


class Users(Base, AnonymousUser):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(
        postgresql.INTEGER,
        primary_key=True,
        autoincrement=True
    )
    admin: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=false(), default=False
    )
    username: Mapped[str] = mapped_column(
        String(length=64), nullable=False, unique=True
    )
    salt: Mapped[str] = mapped_column(String(length=32), nullable=False)
    password_db: Mapped[str] = mapped_column(String(length=1024), nullable=False)
    points: Mapped[int] = mapped_column(
        postgresql.INTEGER,
        default=0,
        server_default="0",
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=False
    )

    def __repr__(self):
        return '<User(id={}, created_at={}, updated_at={})>'.format(
            self.id, self.created_at, self.updated_at
        )

    @property
    def is_anonymous(self):
        return False

    @property
    def password(self) -> str:
        return self.password_db

    @password.setter
    def password(self, value: str):
        self.password_db = password_hash(value, self.salt)


class Goods(Base, BaseModel):
    __tablename__ = 'goods'

    id: Mapped[int] = mapped_column(
        postgresql.INTEGER,
        primary_key=True,
        autoincrement=True,
    )
    name: Mapped[str] = mapped_column(
        String(length=64), nullable=False, unique=True
    )
    price: Mapped[int] = mapped_column(
        postgresql.INTEGER,
        default=0,
        server_default="0",
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=False,
    )

    def __repr__(self):
        return '<User(name={}, created_at={}, updated_at={})>'.format(
            self.name, self.created_at, self.updated_at
        )


class UserGoods(Base, BaseModel):
    __tablename__ = 'user_goods'

    id: Mapped[int] = mapped_column(
        postgresql.INTEGER,
        primary_key=True,
        autoincrement=True,
    )
    user_id: Mapped[int] = mapped_column(
        postgresql.INTEGER,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    good_id: Mapped[int] = mapped_column(
        postgresql.INTEGER,
        ForeignKey("goods.id", ondelete="CASCADE"),
        nullable=False,
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=False,
    )

    def __repr__(self):
        return '<UserGoods(user_id={}, good_id={} created_at={}, updated_at={})>'.format(
            self.user_id, self.good_id, self.created_at, self.updated_at
        )
