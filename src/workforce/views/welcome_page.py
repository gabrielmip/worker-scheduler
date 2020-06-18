from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from workforce.repositories.user_repository import get_user_object_from_email, has_missing_fields


def get_welcome_page(request):
    if request.method == 'GET':
        if request.session.get('email_address', False):
            del request.session['email_address']

        return render(request, 'welcome.html')

    if request.method == 'POST':
        posted_email = request.POST['registered_email']
        request.session['email_address'] = posted_email
        user, is_new = get_user_object_from_email(posted_email)
        missing_fields = has_missing_fields(user)

        if is_new:
            message = f'O email {posted_email} não está registrado. Tem certeza que foi o que usou?'
            return render(request, 'welcome.html', {
                'error_message': message
            })

        if missing_fields:
            return HttpResponseRedirect(reverse('registration'))

        return HttpResponseRedirect(reverse('schedule'))
