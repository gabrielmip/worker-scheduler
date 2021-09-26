from workforce.models import Patient


def get_user_object_from_email(email_address):
    ''' Returns the object and a boolean stating if
        the user is new.
    '''
    if not email_address:
        return Patient(), True

    try:
        return Patient.objects.get(email_address=email_address), False
    except Patient.DoesNotExist:
        return Patient(email_address=email_address), True


def has_missing_fields(user: Patient):
    return (
        not bool(user.photo)
        or user.pk is None
        or user.full_name is None
    )
