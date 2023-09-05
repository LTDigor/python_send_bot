from typing import Optional, List

from sqlalchemy import select, insert, delete, and_
from sqlalchemy.orm import Session

from db.create_tables import engine
from db.db_declaration import UserMailings, MailingTypes
from utils.validation_utils import validate_users


def get_user_ids(mailing_type: int, user_ids: Optional[List[int]]) -> List[int]:
    db = Session(engine)
    if user_ids:
        data = db.execute(
            select(UserMailings.user_id).where(
                and_(
                    UserMailings.mailing_type_id == mailing_type,
                    UserMailings.user_id.in_(user_ids)
                )
            )
        )
    else:
        data = db.execute(
            select(UserMailings.user_id).where(
                and_(
                    UserMailings.mailing_type_id == mailing_type,
                )
            )
        )

    data_ids = list(data.scalars().all())
    if user_ids:
        validate_users(data_ids, user_ids)
    return data_ids


def subscribe_user(user_id, mailing_type):
    if mailing_type == -1:
        subscribe_everywhere(user_id)
    else:
        db = Session(engine)
        if len(list(db.execute(select(UserMailings).where(
                and_(
                    UserMailings.mailing_type_id == mailing_type,
                    UserMailings.user_id == user_id
                )
        )).scalars())) == 0:
            db.execute(insert(UserMailings).values(
                user_id=user_id,
                mailing_type_id=mailing_type,
            ))

            db.commit()


def subscribe_everywhere(user_id):
    db = Session(engine)

    mailing_ids = db.execute(select(MailingTypes.id))
    for mailing_type in list(mailing_ids):
        subscribe_user(user_id, mailing_type[0])


def get_user_mailing_ids(user_id):
    db = Session(engine)
    return db.execute(select(UserMailings.mailing_type_id).where(
        and_(
            UserMailings.user_id == user_id,
        )
    )).scalars().all()


def get_mailings(mailing_ids):
    db = Session(engine)

    return db.execute(
        select(MailingTypes)
        .where(
            and_(
                MailingTypes.id.in_(mailing_ids),
            )
        )).scalars().all()


def get_user_unsubscribed_mailing_ids(user_id):
    user_mailing_ids = get_user_mailing_ids(user_id)

    db = Session(engine)
    return db.execute(
        select(MailingTypes.id)
        .where(
            and_(
                ~MailingTypes.id.in_(user_mailing_ids),
            )
        )).scalars().all()


def unsubscribe_user(user_id, mailing_type):
    if mailing_type == -1:
        unsubscribe_user_everywhere(user_id)
    else:
        db = Session(engine)
        db.execute(delete(
            UserMailings
        ).where(
            and_(
                UserMailings.user_id == user_id,
                UserMailings.mailing_type_id == mailing_type,
            )
        ))
        db.commit()


def unsubscribe_user_everywhere(user_id):
    db = Session(engine)
    db.execute(delete(
        UserMailings
    ).where(
        and_(
            UserMailings.user_id == user_id,
        )
    ))
    db.commit()


def get_mailing_description(mailing_id):
    db = Session(engine)
    mailing_description = db.execute(select(
        MailingTypes.description
    ).where(
        and_(
            MailingTypes.id == mailing_id,
        )
    )).scalars().one()

    return mailing_description
