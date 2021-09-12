import os
from shutil import rmtree
from django.test import Client
from io import BytesIO
from PIL import Image
from django.core.files.base import File

from workforce.models import User


def delete_created_user_photos():
    users_with_photos = [
        user for user in User.objects.all() if bool(user.photo)]
    uploads = {os.path.dirname(user.photo.path) for user in users_with_photos}
    for upload in uploads:
        rmtree(upload)


def create_some_image():
    file_obj = BytesIO()
    image = Image.new("RGBA", size=(25, 25), color=(255, 0, 0))
    image.save(file_obj, 'png')
    file_obj.seek(0)
    return File(file=file_obj, name="bla.png")


def get_client_with_user_in_session(user):
    client = Client()
    session = client.session
    session['email_address'] = user.email_address
    session.save()

    return client
