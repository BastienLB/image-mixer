from fastapi import FastAPI, UploadFile, Response, Request, Form, HTTPException
from PIL import Image, ImageDraw
from fastapi.templating import Jinja2Templates
from pathlib import Path
from utils.manipulating_images import *
from utils.utils import *
from typing import List, Optional
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

import os

app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get("/")
async def index(request: Request):
    """
    Index function, deliver webpage to place gif over background_image_copy
    :param request:
    :return:
    """
    service_ip = os.getenv("SERVICE_IP") if os.getenv("SERVICE_IP") is not None else "127.0.0.1:8000"
    endpoint = "append_gif"
    generate_gif_url = f"http://{service_ip}/{endpoint}"

    return templates.TemplateResponse("index.html", {"request": request, "url": generate_gif_url})


@app.post("/two_images_mix")
async def two_images_mix(
        background: UploadFile,
        front_image: UploadFile
):
    """
    Place one static image on top of another <br>
    Still experimental. <br>
    """
    background = Image.open(background.file)
    front_image = Image.open(front_image.file).convert("RGBA")

    background.paste(front_image, mask=front_image)

    Path("frames").mkdir(parents=True, exist_ok=True)
    image_name = f"frames/{get_random_string(8)}.png"
    background.save(image_name)
    image_bytes = open(image_name, 'rb').read()
    os.remove(image_name)

    return Response(content=image_bytes, media_type="image/png")


@app.post("/append_gif")
async def append_gif(
        background: UploadFile,
        gif: UploadFile,
        gif_starting_x: int = Form(),
        gif_starting_y: int = Form(),
        gif_width: int = Form(),
        gif_height: int = Form(),
        image_width: int = Form(),
        image_height: int = Form(),
        adapt_background_to_gif: Optional[bool] = Form(False)
):
    """
    Add a gif on top of a static background image <br><br>
    :param background: Background image <br>
    :param gif: Gif to place. Everything outside the background image will get cut <br>
    :param gif_starting_x: gif starting position in X axis relative to background image.
    Background image top left corner is x = 0 and y = 0 <br>
    :param gif_starting_y: gif starting position in Y axis relative to background image.
    Background image top left corner is x = 0 and y = 0 <br>
    """

    base_name = get_random_string(5)
    gif = Image.open(gif.file)
    number_frames = gif.n_frames
    frames_duration = gif.info["duration"]
    background_image = Image.open(background.file)

    gif_size = (gif_width, gif_height)
    image_size = (image_width, image_height)

    print(f"Original image size: ({background_image.width}, {background_image.height})")
    print(f"Current image size: ({image_width}, {image_height})")

    background_image = background_image.resize(image_size)
    # Split gif frames
    frames = []
    for i in range(number_frames):
        gif.seek(i)
        resized_frame = gif.resize(gif_size)
        frames.append(resized_frame)

    # Define if a new background is needed
    dimensions_background = None
    if adapt_background_to_gif:
        dimensions_background = define_background_image_size(gif_starting_x, gif_starting_y, frames[0], background_image)

    # Add each frame on top of the backgrou,d
    new_frames = []
    for frame in frames:
        background_image_copy = background_image.copy().convert("RGBA")

        frame = frame.convert("RGBA")

        # Transform white pixels to transparent
        frame = set_all_white_pixels_transparents(frame)

        if dimensions_background is None:
            background_image_copy.paste(frame, (gif_starting_x, gif_starting_y), mask=frame)
            new_frames.append(background_image_copy)
        else:
            generated_background_image = Image.new(
                "RGBA",
                dimensions_background,
                (255,255,255)
            )

            generated_background_image.paste(
                background_image_copy,
                (
                    0 if gif_starting_x > 0 else abs(gif_starting_x),
                    0 if gif_starting_y > 0 else abs(gif_starting_y)
                ),
                mask=background_image_copy
            )

            generated_background_image.paste(
                frame,
                (
                    0 if gif_starting_x < 0 else gif_starting_x,
                    0 if gif_starting_y < 0 else gif_starting_y
                ),
                mask=frame
            )
            new_frames.append(generated_background_image)

    gif_name = f"{base_name}.gif"
    new_frames[0].save(
        gif_name,
        save_all=True,
        append_images=new_frames[1:],
        duration=frames_duration,
        disposal=2,
        loop=0
    )

    gif_bytes = open(gif_name, 'rb').read()
    os.remove(gif_name)
    return Response(content=gif_bytes, media_type='image/gif')


@app.post("/set-pixels-transparent")
async def turn_pixels_transparent(
    image_to_transform: UploadFile,
    rgb_code: List[str] = Form(),
    accuracy_percentage: int = Form(default=100)
):
    """
    Transform specific image's pixels into transparent pixels. <br>
    :param image_to_transform: Image to turn pixels transparent. <br>
    :param rgb_code: rgb code of pixels the app will turn transparent. <br>
    :param accuracy_percentage: The percentage of accuracy that the pixel has to match to get transparent.
    for example, if rgb_code is (100,100,100) and liberty_percentage is 90, pixels between (90,90,90) and (110,110,110)
    will get transformed. Default value is 100.
    """
    rgb_code = [int(number) for number in (rgb_code[0].split(","))]
    if len(rgb_code) != 3:
        return HTTPException(status_code=HTTP_422_UNPROCESSABLE_ENTITY)

    value_pool = define_value_pool(rgb_code=rgb_code, accuracy_percentage=accuracy_percentage)

    image_to_transform = Image.open(image_to_transform.file)
    image_to_transform = image_to_transform.convert("RGBA")
    datas = image_to_transform.getdata()
    new_data = []

    if accuracy_percentage == 100:
        for item in datas:
            if rgb_code == item[:3]:
                new_data.append(tuple(item[:3] + [0]))
            else:
                new_data.append(item)
    else:
        for item in datas:
            if pixel_is_in_value_pool(value_pool=value_pool, pixel=item):
                data_to_append = item[:3] + (0,)
                print(data_to_append)
                new_data.append(data_to_append)
            else:
                new_data.append(item)

    image_to_transform.putdata(new_data)

    image_name = f"{get_random_string(8)}.png"
    image_to_transform.save(image_name)
    image_bytes = open(image_name, 'rb').read()
    os.remove(image_name)

    return Response(content=image_bytes, media_type=f"image/png")

