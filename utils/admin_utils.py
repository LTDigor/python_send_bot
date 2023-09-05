from utils.db_utils import get_mailing_description


def build_message(message, mailing_type):
    mailing_description = get_mailing_description(mailing_type)
    return mailing_description + '\n' + message
