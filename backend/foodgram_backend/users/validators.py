import regex as re

from rest_framework.exceptions import ValidationError


def validate_username(value):
    pattern_username = r'^[\w.@+-]+\Z'
    if not re.match(pattern_username, value):
        raise ValidationError(
            'Username должен содержать только буквы, точки,'
            '@, +, -, дефисы.'
        )
