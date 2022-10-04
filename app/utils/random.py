import random
import string


def random_lower_string(length: int = 8) -> str:
    """choose from all lowercase letter"""
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str


def random_string_and_number(len: int = 8) -> str:
    characters = string.ascii_uppercase + string.digits
    return "".join(random.choice(characters) for i in range(len))
