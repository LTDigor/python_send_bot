from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse

from constants import API_TOKEN, GROUP_ID
from models.CallbackReq import CallbackReq
from models.SensMessagesReq import SendMessagesReq
from utils.db_utils import get_user_ids
from utils.messages_utlis import message_new, create_vk_api_connection

app = FastAPI()


@app.post("/")
async def callback(req: CallbackReq):
    print(req)
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


def confirm_server():
    vk = create_vk_api_connection()
    code = vk.groups.getCallbackConfirmationCode(
        access_token=API_TOKEN,
        group_id=GROUP_ID,
    )['code']
    return PlainTextResponse(code)
