from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class MailingTypes(Base):
    __tablename__ = "mailing_types"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, unique=True)
    children = relationship("UserMailings", back_populates="parent")


class UserMailings(Base):
    __tablename__ = "user_mailings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    mailing_type_id = Column(Integer, ForeignKey("mailing_types.id", ondelete="CASCADE"))
    parent = relationship("MailingTypes", back_populates="children")
