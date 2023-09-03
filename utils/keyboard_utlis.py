import json

from bot_text.bot_text import *
from constants import APP_ID
from utils.db_utils import get_mailings


def build_keyboard(mailing_objects, subscribe_type, subscribe_everywhere_text):
    bottoms = []
    for mailing in mailing_objects:
        bottoms.append(
            [{
                "action": {
                    "type": "text",
                    "label": mailing.description,
                    "payload": {
                        "type": subscribe_type,
                        "mailing_id": mailing.id,
                    }
                }
            }]
        )

    if len(mailing_objects) > 1:
        bottoms.append(
            [{
                "action": {
                    "type": "text",
                    "label": subscribe_everywhere_text,
                    "payload": {
                        "type": subscribe_type,
                        "mailing_id": -1,
                    }
                }
            }]
        )

    bottoms.append(
        [{
            "action": {
                "type": "text",
                "label": CANCEL,
            },
            "color": "negative"
        }]
    )

    return json.dumps({"buttons": bottoms})


def build_keyboard_subscribe(mailing_ids):
    return build_keyboard(get_mailings(mailing_ids), SUBSCRIBE_PAYLOAD, SUBSCRIBE_EVERYWHERE)


def build_keyboard_unsubscribe(mailing_ids):
    return build_keyboard(get_mailings(mailing_ids), UNSUBSCRIBE_PAYLOAD, UNSUBSCRIBE_EVERYWHERE)


def build_keyboard_start_screen():
    return json.dumps({
        "buttons": [
            [
                {
                    "action": {
                        "type": "open_app",
                        "app_id": APP_ID,
                        "payload": "",
                        "label": OPEN_APP,
                        "hash": ""
                    }
                }
            ],
            [
                {
                    "action": {
                        "type": "text",
                        "label": WANT_SUBSCRIBE,
                        "payload": ""
                    },
                    "color": "positive"
                }
            ],
            [
                {
                    "action": {
                        "type": "text",
                        "label": WANT_UNSUBSCRIBE,
                        "payload": ""
                    },
                    "color": "negative"
                }
            ]
        ]
    })
