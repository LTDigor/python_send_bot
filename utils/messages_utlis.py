import vk_api

from bot_text.bot_text import *
from constants import API_TOKEN
from models.CallbackReq import CallbackObject, Payload
from utils.db_utils import *
from utils.keyboard_utlis import build_keyboard_subscribe, build_keyboard_unsubscribe, build_keyboard_start_screen


def message_new(obj: CallbackObject):
    user_id = obj.message.from_id
    start_screen = build_keyboard_start_screen()

    payload = obj.message.payload
    print(obj)
    if payload and payload.command or obj.message.text.lower().strip() in START_COMMAND_LIST:
        meeting_screen(start_screen, user_id)
    elif obj.message.text.lower().strip() == WANT_SUBSCRIBE.lower():
        subscribe_list_screen(user_id)
    elif obj.message.text.lower().strip() == WANT_UNSUBSCRIBE.lower():
        unsubscribe_list_screen(user_id)
    elif obj.message.text.lower().strip() == CANCEL.lower():
        send_message(CHOOSE_ACTION, user_id, start_screen)
    elif payload and payload.type:
        mailing_operation(payload, user_id)
    else:
        raise HTTPException(status_code=400, detail=f"Unknown text {obj.message.text}")


def meeting_screen(start_screen, user_id):
    subscribe_everywhere(user_id)
    send_message(MEETING_TEXT, user_id, start_screen)


def mailing_operation(payload: Payload, user_id):
    start_screen = build_keyboard_start_screen()

    mailing_id = payload.mailing_id
    if payload.type == SUBSCRIBE_PAYLOAD:
        subscribe_user(user_id, mailing_id)
        send_message(MAILING_ADDED, user_id, start_screen)
    elif payload.type == UNSUBSCRIBE_PAYLOAD:
        unsubscribe_user(user_id, mailing_id)
        send_message(MAILING_DELETED, user_id, start_screen)
    else:
        raise HTTPException(status_code=400, detail=f"Wrong payload type {payload.type}")


def subscribe_list_screen(user_id):
    mailing_ids = get_user_unsubscribed_mailing_ids(user_id)
    if not mailing_ids:
        send_message(ALL_MAILINGS_SUBSCRIBED, user_id)
    else:
        keyboard = build_keyboard_subscribe(mailing_ids)
        send_message(CHOOSE_MAILING_TO_SUBSCRIBE, user_id, keyboard)


def unsubscribe_list_screen(user_id):
    mailing_ids = get_user_mailing_ids(user_id)
    if not mailing_ids:
        send_message(ALL_MAILINGS_UNSUBSCRIBED, user_id)
    else:
        keyboard = build_keyboard_unsubscribe(mailing_ids)
        send_message(CHOOSE_MAILING_TO_UNSUBSCRIBE, user_id, keyboard)


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
