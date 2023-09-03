import json
from typing import Optional

import vk_api
from fastapi import HTTPException

from constants import API_TOKEN
from utils.db_utils import subscribe_everywhere, get_user_unsubscribed_mailing_ids, subscribe_user, unsubscribe_user, \
    get_user_mailing_ids
from utils.keyboard_utlis import build_keyboard_subscribe, build_keyboard_unsubscribe


def message_new(obj):
    print("Message new")

    user_id = obj['user_id']
    start_screen = json.dumps(json.load(open("resources/SubscribeScreen.json")))

    if 'payload' in obj and 'command' in obj['payload']:
        meeting_screen(start_screen, user_id)
    elif str(obj['text']).lower().strip() == 'подписаться на рассылки':
        subscribe_list_screen(user_id)
    elif str(obj['text']).lower().strip() == 'отписаться от рассылки':
        unsubscribe_list_screen(user_id)
    elif str(obj['text']).lower().strip() == 'отмена':
        send_message("Выберите действие", user_id, start_screen)
    elif 'payload' in obj and 'type' in obj['payload']:
        mailing_operation(obj, user_id)


def meeting_screen(start_screen, user_id):
    subscribe_everywhere(user_id)
    send_message("Вы подписаны на все, ЛООЛ лол", user_id, start_screen)


def mailing_operation(obj, user_id):
    start_screen = json.dumps(json.load(open("resources/SubscribeScreen.json")))

    mailing_id = obj['payload']['mailing_id']
    if obj['payload']['type'] == 'subscribe':
        subscribe_user(user_id, mailing_id)
        send_message("Подписка добавлена", user_id, start_screen)
    elif obj['payload']['type'] == 'unsubscribe':
        unsubscribe_user(user_id, mailing_id)
        send_message("Подписка удалена", user_id, start_screen)
    else:
        raise HTTPException(status_code=400, detail=f"Wrong payload type {obj['payload']['type']}")


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
