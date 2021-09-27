from django.contrib.auth.backends import ModelBackend, UserModel
from django.core.exceptions import MultipleObjectsReturned
from django.db.models import Q


class EmailUsernameBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = UserModel.objects.get(
                Q(username__iexact=username) | Q(email__iexact=username)
            )

        except UserModel.DoesNotExist:
            # mitigating timing attack
            UserModel().set_password(password)
            return None

        except MultipleObjectsReturned:
            user = UserModel.objects.filter(
                email=username).order_by('id').first()

        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
