import factory

from django.conf import settings
from django.contrib.auth.hashers import make_password


USER_PASSWORD = 'test'


class UserFactory(factory.django.DjangoModelFactory):
    username = factory.Sequence(lambda n: 'Test_User_%s' % n)
    email = factory.Sequence(lambda n: 'email_%s@gmail.com' % n)
    password = make_password(USER_PASSWORD)
    is_active = True

    class Meta:
        model = settings.AUTH_USER_MODEL
