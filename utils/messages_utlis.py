import json
from typing import Optional

import vk_api
from fastapi import HTTPException

from bot_text.bot_text import WANT_SUBSCRIBE, WANT_UNSUBSCRIBE, CANCEL
from constants import API_TOKEN
from models.CallbackReq import CallbackObject, Payload
from utils.db_utils import subscribe_everywhere, get_user_unsubscribed_mailing_ids, subscribe_user, unsubscribe_user, \
    get_user_mailing_ids
from utils.keyboard_utlis import build_keyboard_subscribe, build_keyboard_unsubscribe


def convert_str_to_payload(payload):
    payload_dict = json.loads(payload)
    return Payload(
        command=payload_dict.get('command'),
        type=payload_dict.get('type'),
        mailing_id=payload_dict.get('mailing_id'),
    )


def message_new(obj: CallbackObject):
    user_id = obj.message.from_id
    start_screen = json.dumps(json.load(open("resources/SubscribeScreen.json")))

    payload = obj.message.payload and convert_str_to_payload(obj.message.payload)

    if payload and 'command' in obj.message.payload:
        meeting_screen(start_screen, user_id)
    elif obj.message.text.lower().strip() == WANT_SUBSCRIBE.lower():
        subscribe_list_screen(user_id)
    elif obj.message.text.lower().strip() == WANT_UNSUBSCRIBE.lower():
        unsubscribe_list_screen(user_id)
    elif obj.message.text.lower().strip() == CANCEL.lower():
        send_message("Выберите действие", user_id, start_screen)
    elif obj.message.payload and 'type' in obj.message.payload:
        mailing_operation(payload, user_id)
    else:
        raise HTTPException(status_code=400, detail=f"Unknown text {obj.message.text}")


def meeting_screen(start_screen, user_id):
    subscribe_everywhere(user_id)
    send_message("Вы подписаны на все, ЛООЛ лол", user_id, start_screen)


def mailing_operation(payload: Payload, user_id):
    start_screen = json.dumps(json.load(open("resources/SubscribeScreen.json")))

    mailing_id = payload.mailing_id
    if payload.type == 'subscribe':
        subscribe_user(user_id, mailing_id)
        send_message("Подписка добавлена", user_id, start_screen)
    elif payload.type == 'unsubscribe':
        unsubscribe_user(user_id, mailing_id)
        send_message("Подписка удалена", user_id, start_screen)
    else:
        raise HTTPException(status_code=400, detail=f"Wrong payload type {payload.type}")


def subscribe_list_screen(user_id):
    mailing_ids = get_user_unsubscribed_mailing_ids(user_id)
    if not mailing_ids:
        send_message("Вы подписаны на все доступные рассылки", user_id)
    else:
        keyboard = build_keyboard_subscribe(mailing_ids)
        send_message("Выберите рассылку для подписки", user_id, keyboard)


def unsubscribe_list_screen(user_id):
    mailing_ids = get_user_mailing_ids(user_id)
    if not mailing_ids:
        send_message("Вы уже отписались от всех рассылок", user_id)
    else:
        keyboard = build_keyboard_unsubscribe(mailing_ids)
        send_message("Выберите рассылку, от который хотите отписаться", user_id, keyboard)


def send_message(message: str, user_id: int, keyboard: Optional[str] = None):
    vk = create_vk_api_connection()
    try:
        vk.messages.send(
            access_token=API_TOKEN,
            user_id=user_id,
            random_id=0,
            message=message,
            keyboard=keyboard,
        )
    except Exception as error_msg:
        raise HTTPException(status_code=500, detail=str(error_msg))


def create_vk_api_connection():
    vk_session = vk_api.VkApi(API_TOKEN)
    try:
        vk_session.auth(token_only=True)
    except vk_api.AuthError as error_msg:
        raise HTTPException(status_code=500, detail=str(error_msg))
    vk = vk_session.get_api()
    return vk
