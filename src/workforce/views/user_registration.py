from django.http import HttpResponseRedirect
from django.shortcuts import render, reverse
from django.views import View

from workforce.forms import Registration
from workforce.services.users import get_user_object_from_email, has_missing_fields


class RegisterUser(View):

    def get(self, request):
        user, is_new = get_user_object_from_email(
            request.session.get('email_address'))
        missing_fields = has_missing_fields(user)

        if not is_new and not missing_fields:
            return HttpResponseRedirect(reverse('schedule'))

        registration_form = Registration(instance=user)
        return render(request, 'registration.html', {
            'form': registration_form,
            'is_new': is_new,
            'missing_fields': missing_fields
        })

    def post(self, request):
        user, is_new = get_user_object_from_email(
            request.session.get('email_address'))
        user_registration = Registration(
            request.POST, request.FILES, instance=user)

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
