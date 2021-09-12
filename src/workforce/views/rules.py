import functools
from django.http import HttpResponseRedirect
from django.shortcuts import reverse
from workforce.services.users import get_user_object_from_email, has_missing_fields


def finished_registration_required(view_func):

    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('email_address', False):
            return HttpResponseRedirect(reverse('welcome'))

        user, is_new = get_user_object_from_email(
            request.session['email_address'])
        missing_fields = has_missing_fields(user)

        if missing_fields or is_new:
            return HttpResponseRedirect(reverse('welcome'))

        return view_func(request, user, *args, **kwargs)

    return wrapper
