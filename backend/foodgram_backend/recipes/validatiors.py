import regex as re

from rest_framework.exceptions import ValidationError


def validate_slug(value):
    pattern_slug = r'^[-a-zA-Z0-9_]+$'
    if not re.match(pattern_slug, value):
        raise ValidationError(
            'Slug должен содержать только буквы, '
            'числа, дефисы или знаки подчеркивания.'
        )