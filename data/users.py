import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class User(SqlAlchemyBase):
    __tablename__ = 'users'
    # Информация о аккаунте
    user_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    is_admin = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True)
    listened = sqlalchemy.Column(sqlalchemy.Float, nullable=True)

    # Информация о выборах пользователя
    model = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    last_messages = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    story = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    def __repr__(self):
        return f"{self.user_id}"
