import os


def build_path_for_user_picture(user, filename):
    user_hash = str(hash(f"{user.full_name}|{user.email_address}"))

    return os.path.join(user_hash, filename)
