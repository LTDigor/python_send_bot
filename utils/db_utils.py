from typing import Optional, List

from fastapi import HTTPException
from sqlalchemy import select, insert, and_
from sqlalchemy.orm import Session

from db.db_declaration import UserMailings, engine, MailingTypes


def validate(data_ids, user_ids):
    if set(data_ids) != set(user_ids):
        raise HTTPException(
            status_code=400,
            detail=f"Users {set(user_ids).difference(set(data_ids))} have no subscription"
        )


def get_user_ids(mailing_type: int, user_ids: Optional[List[int]]) -> List[int]:
    # get users from db
    db = Session(engine)

    if user_ids:
        data = db.execute(
            select(UserMailings).where(
                and_(
                    UserMailings.mailing_type_id == mailing_type,
                    UserMailings.user_id.in_(user_ids)
                )
            )
        )
    else:
        data = db.execute(
            select(UserMailings).where(
                and_(
                    UserMailings.mailing_type_id == mailing_type,
                )
            )
        )

    data_ids = list(map(lambda user: user.user_id, data.scalars().all()))
    if user_ids:
        validate(data_ids, user_ids)

    return data_ids


def subscribe_user(user_id, mailing_type):
    db = Session(engine)

    if len(list(db.execute(select(UserMailings).where(
            and_(
                UserMailings.mailing_type_id == mailing_type,
                UserMailings.user_id == user_id
            )
    )).scalars())) == 0:
        db.add(
            UserMailings(
                user_id=user_id,
                mailing_type_id=mailing_type,
            )
        )


def subscribe_everywhere(user_id):
    db = Session(engine)

    mailing_ids = db.execute(select(MailingTypes.id))
    for mailing_type in list(mailing_ids):
        subscribe_user(user_id, mailing_type[0])
