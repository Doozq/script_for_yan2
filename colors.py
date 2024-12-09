import io
import logging
import time
from PIL import Image
from templates import templates, tournament_templates
from config import t_size

import logger_setup
import numpy as np

def color_from_template(template_path, pixel_coords, start):
    try:
        path = "C:\\Users\\Administrator\\Downloads\\" + template_path
        start_x, start_y = start
        image = Image.open(path)
        template_coolors = [[image.getpixel((coord[0] - start_x, coord[1] - start_y))[:3] for coord in row] for row in pixel_coords]
        if len(image.getpixel((0, 0))) == 3:
            opacity = 0
        else:
            opacity = [[image.getpixel((coord[0] - start_x, coord[1] - start_y))[3] for coord in row] for row in pixel_coords]

        return template_coolors, opacity



        # path = "templates\\" + template_path
        # start_x, start_y = template["start"]
        # t_x, t_y = x - start_x, y - start_y

        # # Загружаем изображение шаблона
        # image = Image.open(path)

        # # Получаем цвет пикселя из изображения
        # color = image.getpixel((t_x, t_y))

        # return color[:3]

    except KeyError as e:
        logging.error(f"Template or its start coordinates not found: {e}")
        raise
    except FileNotFoundError as e:
        logging.error(f"Template image file not found: {e}")
        raise
    except Exception as e:
        logging.error(f"An unexpected error occurred in color_from_template: {e}")
        raise


def color_from_screen(canvas_coords, canvas):
    try:
        width = canvas.size["width"]
        height = canvas.size["height"]
        s_coords = [[(coord[0] + width // 2, coord[1] + height // 2) for coord in row] for row in canvas_coords]
        screen = canvas.screenshot_as_png
        image = Image.open(io.BytesIO(screen))
        colors = [[image.getpixel(coord) for coord in row] for row in s_coords]
        return colors


        # # Определяем координаты пикселя на скриншоте
        # s_x = x + canvas.size["width"] // 2 + 1
        # s_y = y + canvas.size["height"] // 2 + 1

        # # Снимаем скриншот с canvas
        # screen = canvas.screenshot_as_png
        # image = Image.open(io.BytesIO(screen))

        # # Получаем цвет пикселя на экране
        # color = image.getpixel((s_x, s_y))

        # return color

    except AttributeError as e:
        logging.error(f"Canvas object might be None or incorrect: {e}")
        raise
    except IOError as e:
        logging.error(f"Error while processing the screenshot: {e}")
        raise
    except Exception as e:
        logging.error(f"An unexpected error occurred in color_from_screen: {e}")
        raise
