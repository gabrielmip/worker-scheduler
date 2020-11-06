import os
import datetime
import arrow
from tzlocal import get_localzone


def build_path_for_user_picture(user, filename):
    user_hash = str(hash(f"{user.full_name}|{user.email_address}"))

    return os.path.join(user_hash, filename)


def get_today_date_for_timezone(timezone):
    return arrow.get(datetime.datetime.today()).replace(tzinfo=get_localzone()).to(timezone)
