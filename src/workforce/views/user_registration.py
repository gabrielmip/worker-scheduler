from django.http import HttpResponseRedirect
from django.shortcuts import render, reverse

from workforce.forms import Registration
from workforce.repositories.user_repository import get_user_object_from_email, has_missing_fields
from workforce.models import User


def register_user(request):
    user, is_new = ((User(), True)
                    if not request.session.get('email_address', False)
                    else get_user_object_from_email(request.session['email_address']))

    if request.method == 'GET':
        missing_fields = has_missing_fields(user)

        if not is_new and not missing_fields:
            return HttpResponseRedirect(reverse('schedule'))

        registration_form = Registration(instance=user)
        return render(request, 'registration.html', {
            'form': registration_form,
            'is_new': is_new,
            'missing_fields': missing_fields
        })

    if request.method == 'POST':
        user_registration = Registration(request.POST, request.FILES, instance=user)

        if not user_registration.is_valid():
            user, is_new = get_user_object_from_email(
                user_registration.data['email_address'])
            missing_fields = has_missing_fields(user)

            return render(request, 'registration.html', {
                'form': user_registration,
                'is_new': is_new,
                'missing_fields': missing_fields
            })

        saved_user = user_registration.save()
        request.session['email_address'] = saved_user.email_address

        return HttpResponseRedirect(reverse('schedule'))
