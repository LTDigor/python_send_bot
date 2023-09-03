import json

from models.CallbackReq import Payload


def convert_str_to_payload(payload):
    payload_dict = json.loads(payload)

    return Payload(
        command=payload_dict.get('command'),
        type=payload_dict.get('type'),
        mailing_id=payload_dict.get('mailing_id'),
    )