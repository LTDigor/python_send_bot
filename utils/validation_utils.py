from sqlalchemy import select, and_
from sqlalchemy.orm import Session

from constants.bot_constants import BOT_SECRET
from db.create_tables import engine
from db.db_declaration import MailingTypes

from urllib.parse import urlparse, parse_qsl, urlencode
from collections import OrderedDict
from fastapi import HTTPException, Header
from base64 import b64encode
from hashlib import sha256
from hmac import HMAC
from pydantic import BaseModel
from typing import Annotated

from utils.BetterDict import BetterDict


class VKUserCredentials(BaseModel):
    auth: str


def get_url_query(url):
    query = dict(parse_qsl(urlparse(url).query, keep_blank_values=True))
    for k, v in query.items():
        if k == '?vk_access_token_settings':
            query.update({'vk_access_token_settings': v})
            break
    auth = OrderedDict(sorted(x for x in query.items() if x[0][:3] == "vk_"))
    for key in query.copy().keys():
        if key[:3] == "vk_":
            query.pop(key)
    data = BetterDict({'subset': auth, 'sign': query.get('sign', None)})
    return BetterDict(data)


def validate_data(data):
    hash_code = b64encode(
        HMAC(BOT_SECRET.encode(), urlencode(data['subset'], doseq=True).encode(), sha256).digest())
    decoded_hash_code = hash_code.decode('utf-8')[:-1].replace('+', '-').replace('/', '_')
    if data["sign"] != decoded_hash_code:
        raise HTTPException(status_code=400, detail="Authentication failed")


async def validate_vk_user(credentials: Annotated[str, Header()]):
    validate_data(get_url_query(credentials))
    return True


def validate_users(data_ids, user_ids):
    if set(data_ids) != set(user_ids):
        raise HTTPException(
            status_code=400,
            detail=f"Users {set(user_ids).difference(set(data_ids))} have no subscription"
        )


def validate_mailing_id(mailing_id):
    db = Session(engine)
    mailing_descriptions = db.execute(select(
        MailingTypes.description
    ).where(
        and_(
            MailingTypes.id == mailing_id,
        )
    )).scalars().all()

    if len(mailing_descriptions) == 0:
        raise HTTPException(status_code=400, detail=f"Mailing with id {mailing_id} doesn't exist")
