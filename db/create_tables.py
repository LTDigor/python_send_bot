from sqlalchemy import delete
from sqlalchemy.orm import Session

from db.db_declaration import Base, MailingTypes, engine

Base.metadata.create_all(bind=engine)
session = Session(engine)

session.execute(delete(MailingTypes))
session.add_all([
    MailingTypes(description="Закрытие подъёмников"),
    MailingTypes(description="Загруженность подъёмников"),
    MailingTypes(description="Экстренные уведомления"),
])

session.commit()
