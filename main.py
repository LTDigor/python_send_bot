import time

from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse

from constants import API_TOKEN, GROUP_ID, CALLBACK_SECRET
from models.CallbackReq import CallbackReq
from models.SensMessagesReq import SendMessagesReq
from utils.db_utils import get_user_ids
from utils.messages_utlis import message_new, create_vk_api_connection

app = FastAPI()


@app.post("/")
async def callback(req: CallbackReq):
    if req.type == "confirmation":
        return confirm_server()
    elif req.type == "message_new":
        if req.secret == CALLBACK_SECRET:
            message_new(req.object)
        return PlainTextResponse("ok")


@app.post("/send/")
async def send_messages(message_req: SendMessagesReq):
    vk = create_vk_api_connection()
    user_ids = get_user_ids(mailing_type=message_req.mailing_type, user_ids=message_req.user_ids)

    try:
        # vk.messages.send(
        #     access_token=API_TOKEN,
        #     random_id=0,
        #     user_ids=user_ids,
        #     message=message_req.message,
        # )
        max_users = 99
        user_ids_buckets = [user_ids[i:i + max_users] for i in range(0, len(user_ids), max_users)]
        for user_ids_bucket in user_ids_buckets:
            vk.messages.send(
                access_token=API_TOKEN,
                random_id=0,
                user_ids=user_ids_bucket,
                message=message_req.message,
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
