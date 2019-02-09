from oauth2_provider.models import Application
from rest_framework.serializers import ValidationError
from API.models import (TITLE_MAX_LENGTH, NAME_MAX_LENGTH, PASSWORD_MAX_LENGTH, PASSWORD_MIN_LENGTH)


def usernameValidator(value):
    if value is None:
        raise ValidationError('username can\'t be null')
    valueStr = str(value)
    if len(valueStr) > NAME_MAX_LENGTH or len(valueStr) < 1:
        raise ValidationError('username error')
    return value


def clientIDValidator(value):
    if value is None:
        raise ValidationError('client ID can\'t be null')
    valueStr = str(value)
    if len(valueStr) != 40:
        raise ValidationError('client ID error')
    if Application.objects.filter(client_id=valueStr).exists() is False:
        raise ValidationError('client ID error')
    return value


def clientSecretValidator(value):
    if value is None:
        raise ValidationError('client Secret can\'t be null')
    valueStr = str(value)
    if len(valueStr) != 128:
        raise ValidationError('client Secret error')
    if Application.objects.filter(client_secret=valueStr).exists() is False:
        raise ValidationError('client Secret error')
    return value


def passwordValidator(value):
    if value is None:
        raise ValidationError('password can\'t be null')
    valueStr = str(value)
    if len(valueStr) > PASSWORD_MAX_LENGTH or len(valueStr) < PASSWORD_MIN_LENGTH:
        raise ValidationError('password error')
    return value


def titleValidator(value):
    if value is None:
        raise ValidationError('title can\'t be null')
    valueStr = str(value)
    if len(valueStr) > TITLE_MAX_LENGTH or len(valueStr) < 1:
        raise ValidationError('title error')
