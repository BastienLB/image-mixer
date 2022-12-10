import string
import random
from PIL import Image

def get_random_string(length):
    """
    Generate random string length long
    :param length:
    :return:
    """
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str


def extract_frames_from_gif(gif: Image, size: tuple):
    """
    Extract frames for a given gif and resize it if needed
    :param gif: pillow.Image - Gif to extract frame of
    :param size: Tuple - Gif (new) size. (width, height)
    """
    frames = []
    for i in range(gif.n_frames):
        gif.seek(i)
        resized_frame = gif.resize(size)
        frames.append(resized_frame)
    return frames