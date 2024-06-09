from random import choices
from string import ascii_letters, digits


def get_unique_short_id():
    return ''.join(choices(ascii_letters + digits, k=6))
