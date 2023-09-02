from sqlalchemy import Column, Integer, String, ForeignKey, create_engine
from sqlalchemy.orm import relationship, DeclarativeBase

SQLALCHEMY_DATABASE_URL = "sqlite:///../sql_app.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)


class Base(DeclarativeBase):
    pass


class MailingTypes(Base):
    __tablename__ = "mailing_types"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String)
    children = relationship("UserMailings", back_populates="parent")


class UserMailings(Base):
    __tablename__ = "user_mailings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    mailing_type_id = Column(Integer, ForeignKey("mailing_types.id", ondelete="CASCADE"))
    parent = relationship("MailingTypes", back_populates="children")
