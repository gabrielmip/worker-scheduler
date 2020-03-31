from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse


def get_my_schedule(request):
    if not hasattr(request, 'user') or not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    return HttpResponse(str(request.user))



