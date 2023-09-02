import logging
from typing import Optional

import vk_api
from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse

from constants import API_TOKEN, GROUP_ID
from models.CallbackReq import CallbackReq
from models.SensMessagesReq import SendMessagesReq
from utils.db_utils import get_user_ids, subscribe_everywhere

app = FastAPI()


@app.post("/")
async def callback(req: CallbackReq):
    if req.type == "confirmation":
        return confirm_server()
    elif req.type == "message_new":
        message_new(req.object)
        return "Done"


@app.post("/send/")
async def send_messages(message_req: SendMessagesReq):
    vk = create_vk_api_connection()
    user_ids = get_user_ids(mailing_type=message_req.mailing_type, user_ids=message_req.user_ids)

    try:
        # todo execude for 100k users
        vk.messages.send(
            access_token=API_TOKEN,
            random_id=0,
            user_ids=user_ids,
            message=message_req.message,
        )
    except Exception as error_msg:
        raise HTTPException(status_code=500, detail=str(error_msg))

    return "Done"


def create_vk_api_connection():
    vk_session = vk_api.VkApi(API_TOKEN)
    try:
        vk_session.auth(token_only=True)
    except vk_api.AuthError as error_msg:
        raise HTTPException(status_code=500, detail=str(error_msg))
    vk = vk_session.get_api()
    return vk


def message_new(obj):
    logging.info('message new')
    user_id = obj['user_id']
    if obj['payload'] == '{"command":"start"}':
        subscribe_everywhere(user_id)
        send_message("Вы подписаны на все, ЛООЛ лол", user_id)
    elif str(obj['text']).lower().strip() == 'подписаться на рассылку':
        # вернуть список доступных рассылок как кнопки
        pass
    elif str(obj['text']).lower().strip() == 'отписаться от рассылки':
        # удалить юзера из бд
        # сказать, что удалили
        pass
    elif str(obj['text']).lower().strip() == 'отмена':
        # на стартовый экран
        pass


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


def confirm_server():
    vk = create_vk_api_connection()
    code = vk.groups.getCallbackConfirmationCode(
        access_token=API_TOKEN,
        group_id=GROUP_ID,
    )['code']
    return PlainTextResponse(code)
