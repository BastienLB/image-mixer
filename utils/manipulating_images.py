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







