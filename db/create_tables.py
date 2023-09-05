from sqlalchemy import delete, create_engine
from sqlalchemy.orm import Session

from constants.bot_constants import SQLALCHEMY_DATABASE_URL
from db.db_declaration import Base, MailingTypes

engine = create_engine(SQLALCHEMY_DATABASE_URL)

Base.metadata.create_all(bind=engine)
session = Session(engine)

session.execute(delete(MailingTypes))
session.add_all([
    MailingTypes(description="Закрытие подъёмников"),
    MailingTypes(description="Экстренные уведомления"),
    MailingTypes(description="Изменение режима работы подъемников"),
])

session.commit()
