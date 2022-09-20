import string
import random

def get_random_string(length):
    """
    Generate random string length long
    :param length:
    :return:
    """
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str