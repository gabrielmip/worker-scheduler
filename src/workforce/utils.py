from collections import defaultdict
from functools import reduce
import os
import datetime
import arrow
from tzlocal import get_localzone


def build_path_for_user_picture(user, filename):
    user_hash = str(hash(f"{user.full_name}|{user.email_address}"))

    return os.path.join(user_hash, filename)


def get_today_date_for_timezone(timezone,
                                requested_date=datetime.datetime.today()):
    return arrow.get(requested_date).replace(tzinfo=get_localzone()).to(timezone)


def group_by(items, key, fn=lambda x: x):
    grouped = defaultdict(list)

    for item in items:
        key_value = item.get(key) if type(item) is dict else getattr(item, key)
        grouped[key_value].append(fn(item))

    return grouped


def index_by(items, key):
    grouped = {}

    for item in items:
        key_value = item.get(key) if type(item) is dict else getattr(item, key)
        grouped[key_value] = item

    return grouped


def get_locale_from_settings(language_code):
    return language_code.split('-')[0]


def partition(items, partition_size):
    for index in range(0, len(items), partition_size):
        yield items[index: index + partition_size]


def enum_entries(enum_class):
    return [(t, t.value) for t in enum_class]
