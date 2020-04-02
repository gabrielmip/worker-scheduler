from workforce.models import User


def get_user_by_email_address(email_address):
    return User.objects.filter(email_address=email_address).first()
