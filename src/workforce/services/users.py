from workforce.models import User


def get_user_object_from_email(email_address):
    ''' Returns the object and a boolean stating if
        the user is new.
    '''
    if not email_address:
        return User(), True

    try:
        return User.objects.get(email_address=email_address), False
    except User.DoesNotExist:
        return User(email_address=email_address), True


def has_missing_fields(user: User):
    return (
        not bool(user.photo)
        or user.pk is None
        or user.full_name is None
    )
