import json

from PIL import Image


def set_all_white_pixels_transparents(image: Image):
    datas = image.getdata()

    # Convert white pixels
    new_data = []
    for item in datas:
        if item[0] == 255 and item[1] == 255 and item[2] == 255:
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(item)
    image.putdata(new_data)
    return image


def define_background_image_width(
    gif_starting_x: int,
    frame: Image,
    background: Image
):
    if gif_starting_x + frame.width > background.width:
        return gif_starting_x + frame.width
    else:
        if gif_starting_x < 0:
            return abs(gif_starting_x) + background.width
        else:
            return background.width


def define_background_image_height(
    gif_starting_y: int,
    frame: Image,
    background: Image
):
    if gif_starting_y + frame.height > background.height:
        return gif_starting_y + frame.height
    else:
        if gif_starting_y < 0:
            return abs(gif_starting_y) + background.height
        else:
            return background.height


def define_background_image_size (
    gif_starting_x: int,
    gif_starting_y: int,
    frame: Image,
    background: Image,
):

    if gif_starting_x < 0 or gif_starting_y < 0 or (gif_starting_x + frame.width) > background.width or (gif_starting_y + frame.height) > background.height:
        width = define_background_image_width(
            gif_starting_x,
            frame,
            background
        )

        height = define_background_image_height(
            gif_starting_y,
            frame,
            background
        )
        return width, height
    return None


def define_value_pool(rgb_code, accuracy_percentage):
    """
    Define min and max value a color can be to be replaced.

    :param rgb_code: pixel rgb code
    :param accuracy_percentage: accuracy percentage
    :return: Array list containing min and max color value
    """
    min_percentage_multiplier = round(accuracy_percentage/100, 1)
    max_percentage_multiplier = round(1+(1-min_percentage_multiplier), 1)
    value_pool = []
    for color in rgb_code:
        min_color = int(color * min_percentage_multiplier)
        max_color = int(color * max_percentage_multiplier)
        value_pool.append({
            "min_color": min_color,
            "max_color": max_color
        })
    return value_pool


def pixel_is_in_value_pool(
    pixel: list[int],
    value_pool: list
):
    """
    Verify if pixel is in the defined value pool. Value pool defined using the accuracy percentage
    :param pixel: integer list, the current pixel that is examined
    :param value_pool: the min and max value that the pixel can have for Red, Green and Blue
    :return: boolean
    """

    for i in range(3):
        if pixel[i] < value_pool[i]["min_color"] or pixel[i] > value_pool[i]["max_color"]:
            return False
    return True
