from enum import Enum


class RequestsTypes(str, Enum):
    CONFIRMATION = 'confirmation'
    MESSAGE_ALLOW = 'message_allow'
    MESSAGE_NEW = 'message_new'
