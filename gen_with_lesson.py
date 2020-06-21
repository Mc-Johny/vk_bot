from PIL import Image, ImageDraw, ImageFont#, ImageFilter
import os
import random
import t_w
import sqlite3
from datetime import datetime as dt
import asyncio

solid_fill = (50, 50, 50, 255)

__connection = None


def get_conection():
    global __connection
    if __connection is None:
        __connection = sqlite3.connect('quick.db')
    return __connection


def tommorow_day():
    if dt.now().weekday() + 1 == 7:
        return 0
    return dt.now().weekday() + 1


def get_lesson_tomorrow(class_name):
    conn = get_conection()
    c = conn.cursor()
    c.execute('SELECT lesson_%d FROM class WHERE class_name = \'%s\'' % (tommorow_day(), class_name))
    res = c.fetchall()
    return res[0][0]


image_list = []


async def crate_image(class_name):
    directory = 'images'
    list_directory = os.listdir(directory)

    for x in list_directory:
        image_list.append(x)
    image_ = Image.open('images/%s' % random.choice(image_list))
    img = ImageDraw.Draw(image_)
    w, h = image_.size
    x = round(w / 43.75)
    y = round(h / 75.13)
    font_size = round(w * 0.0513406)
    font = ImageFont.truetype('fonts/font3.otf', font_size)
    img_text = get_lesson_tomorrow(class_name) + '\n\n>Для %s класса<' % class_name
    weight = round(w / 2)
    height = round(h / 2)

    pixel = []
    for x_ in range(weight):
        for y_ in range(height):
            r, g, b = image_.getpixel((x_, y_))
            pixel.append([r, g, b])

    avr = [sum(x) // len(x) for x in zip(*pixel)]
    r, g, b = avr
    morning, day = t_w.weather_r()
    temp_morning = morning + ' °C'
    temp_day = day + ' °C'
    img.text((x, y), img_text, fill=(255 - r, 255 - g, 255 - b), font=font)
    x1 = round(w / 1.3)
    y1 = round(h / 75)
    pix = []
    for x_ in range(x1, w):
        for y_ in range(height):
            red, green, blue = image_.getpixel((x_, y_))
            pix.append([red, green, blue])

    avr1 = [sum(x) // len(x) for x in zip(*pix)]
    r1, g1, b1 = avr1

    x_for_line = x1
    y_for_line = round(h / 11.71875)
    img1 = ImageDraw.Draw(image_)
    shape = [(x_for_line, y_for_line), (w, y_for_line)]
    draw_line = img1.line(shape, fill=(255 - r1, 255 - g1, 255 - b1), width=round(h / 750))
    temp_font = ImageFont.truetype('fonts/17575.ttf', round(font_size * 1.5))
    img.text((round(w * 0.56), round(h / 32.6)), 'Утром:', fill=(255 - r1, 255 - g1, 255 - b1), font=font)
    img.text((round(w * 0.585), round(h / 9.375)), 'Днем:', fill=(255 - r1, 255 - g1, 255 - b1), font=font)
    img.text((x1, y1), temp_morning, fill=(255 - r1, 255 - g1, 255 - b1), font=temp_font)
    img.text((x1, round(h / 10.075471698)), temp_day, fill=(255 - r1, 255 - g1, 255 - b1), font=temp_font)
    image_.save('out/%s_class_%d.png' % (class_name, tommorow_day()), 'PNG')
