import time

from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import PlainTextResponse

from constants.RequestsTypes import RequestsTypes
from constants.bot_constants import CALLBACK_SECRET, API_TOKEN, GROUP_ID
from models.CallbackReq import CallbackReq
from models.SensMessagesReq import SendMessagesReq
from utils.admin_utils import build_message
from utils.db_utils import get_user_ids
from utils.messages_utlis import message_new, create_vk_api_connection, allow_messages
from utils.validation_utils import validate_mailing_id, validate_vk_user

app = FastAPI()


@app.post("/")
async def callback(req: CallbackReq):
    if req.type == RequestsTypes.CONFIRMATION:
        return confirm_server()
    elif req.secret != CALLBACK_SECRET:
        pass
    elif req.type == RequestsTypes.MESSAGE_ALLOW:
        allow_messages(req.object)
    elif req.type == RequestsTypes.MESSAGE_NEW:
        message_new(req.object)
    return PlainTextResponse("ok")


@app.post("/send/")
async def send_messages(message_req: SendMessagesReq, is_validated_user: bool = Depends(validate_vk_user)):
    vk = create_vk_api_connection()

    validate_mailing_id(message_req.message)

    user_ids = get_user_ids(mailing_type=message_req.mailing_type, user_ids=message_req.user_ids)
    message = build_message(message_req.message, message_req.mailing_type)
    try:
        max_users = 99
        user_ids_buckets = [user_ids[i:i + max_users] for i in range(0, len(user_ids), max_users)]
        for user_ids_bucket in user_ids_buckets:
            vk.messages.send(
                access_token=API_TOKEN,
                random_id=0,
                user_ids=user_ids_bucket,
                message=message,
            )
            time.sleep(0.1)

    except Exception as error_msg:
        raise HTTPException(status_code=500, detail=str(error_msg))

    return "Done"


def confirm_server():
    vk = create_vk_api_connection()
    code = vk.groups.getCallbackConfirmationCode(
        access_token=API_TOKEN,
        group_id=GROUP_ID,
    )['code']
    return PlainTextResponse(code)
