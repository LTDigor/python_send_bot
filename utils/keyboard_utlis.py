import json

from utils.db_utils import get_mailings


def build_keyboard(mailing_objects, subscribe_type):
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

    bottoms.append(
        [{
            "action": {
                "type": "text",
                "label": "Отмена",
                "payload": ""
            },
            "color": "negative"
        }]
    )

    return json.dumps({"buttons": bottoms})


def build_keyboard_subscribe(mailing_ids):
    return build_keyboard(get_mailings(mailing_ids), 'subscribe')


def build_keyboard_unsubscribe(mailing_ids):
    return build_keyboard(get_mailings(mailing_ids), 'unsubscribe')
