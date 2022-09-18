from fastapi import FastAPI, UploadFile, Response, Request, Form
from PIL import Image, ImageDraw
from fastapi.templating import Jinja2Templates
from pathlib import Path
from pydantic import BaseModel

import os
import shutil
import random
import string


app = FastAPI()
templates = Jinja2Templates(directory="templates")


def get_random_string(length):
    """
    Generate random string length long
    :param length:
    :return:
    """
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str


@app.get("/")
async def index(request: Request):
    """
    Index function, deliver webpage to place gif over background
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
        gif_starting_y: int = Form()
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

    # Split gif frames
    frames = []
    for i in range(number_frames):
        gif.seek(i)
        frames.append(gif.copy())

    # Create a new gif with background image
    new_frames = []
    for frame in frames:
        background = background_image.copy()

        background = background.convert("RGBA")
        frame = frame.convert("RGBA")

        background.paste(frame, (gif_starting_x, gif_starting_y), mask=frame)
        new_frames.append(background)

    gif_name = f"{base_name}.gif"
    new_frames[0].save(
        gif_name,
        save_all=True,
        append_images=new_frames[1:],
        duration=frames_duration,
        loop=0
    )

    gif_bytes = open(gif_name, 'rb').read()
    os.remove(gif_name)
    return Response(content=gif_bytes, media_type='image/gif')



