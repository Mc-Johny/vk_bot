import os
import random
import sqlite3
import t_w
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id
import time
from datetime import datetime as dt
import requests
from PIL import Image, ImageDraw, ImageFont
import threading
import json

token = ''
vk_session = vk_api.VkApi(token=token)

vk = vk_session.get_api()
longpool = VkBotLongPoll(vk_session, id_группы)

user_class = []  # В дальнейшем сюда запишется класс

__connection = None


def get_connection():  # Производится соединение с базой
    global __connection
    if __connection is None:
        __connection = sqlite3.connect('quick.db')
    return __connection


def check_reg(user_id):  # Проверка пользователя. Есть ли он в базе
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT user_id FROM user WHERE user_id = %d' % user_id)
    result = c.fetchone()
    if result is None:
        return False
    return True


def register_new_user(user_id: int):  # Регистрация пользователя в базу
    conn = get_connection()
    c = conn.cursor()
    c.execute('INSERT INTO user (user_id, class, state) VALUES (?,?,?)',
              (user_id, '', 'no_ready'))  # Включение рассылки(1) и добавление пустой строки в колонку class
    conn.commit()


def check_state(user_id):  # Включена ли у пользователя рассылка. Возвращает True, если включена и False если выключена
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT state FROM user WHERE user_id = %d' % user_id)
    result = c.fetchone()
    return result[0]


def add_class(class_name, state, user_id: int):  # Обновление значения колонки class
    conn = get_connection()
    c = conn.cursor()
    c.execute('UPDATE user SET class = \'%s\', state = \'%s\' WHERE user_id = %d' % (class_name, state, user_id))
    conn.commit()


def create_keyboard(response, user_id):  # Создание inline клавиатуры || response - текст, вводимый пользователем
    keyboard = VkKeyboard(one_time=False, inline=True)
    if response.lower() == 'старт':
        keyboard.add_button('10-а', color=VkKeyboardColor.DEFAULT)
        keyboard.add_button('10-г', color=VkKeyboardColor.DEFAULT)
        keyboard.add_button('10-е', color=VkKeyboardColor.DEFAULT)
    elif response.lower() == 'расписание на завтра':
        keyboard.add_button('Текстом📝', color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button('Картинкой🖼', color=VkKeyboardColor.POSITIVE)
    elif check_state(user_id) == 'ready':
        keyboard.add_button('Расписание на завтра', color=VkKeyboardColor.PRIMARY)
    else:
        if check_state(user_id) == 'ready':
            keyboard.add_button('Расписание на завтра', color=VkKeyboardColor.PRIMARY)
        elif check_state(user_id) == 'no_ready':
            keyboard.add_button('10-а', color=VkKeyboardColor.DEFAULT)
            keyboard.add_button('10-г', color=VkKeyboardColor.DEFAULT)
            keyboard.add_button('10-е', color=VkKeyboardColor.DEFAULT)
    return keyboard.get_keyboard()


def change_mode(mode, user_id):  # изменение в колонке mode || Зависит от того, на какую кнопку нажал пользователь
    conn = get_connection()
    c = conn.cursor()
    c.execute('UPDATE user SET mode = %d WHERE user_id = %d' % (mode, user_id))
    conn.commit()
    time.sleep(0.2)


def tommorow_day():  # Возвращает завтрашний день цифрой
    if dt.today().weekday() + 1 == 7:
        return 0
    return dt.today().weekday() + 1


def get_class(user_id):  # Проход по колонке с пользователями || Возвращает список с кортежами с пользователями
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT class FROM user WHERE user_id = %d' % user_id)
    res = c.fetchone()
    return res[0]


def lesson(user_id):  # Возвращает уроки на завтра
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT lesson_%d FROM class WHERE class_name = \'%s\'' % (tommorow_day(), get_class(user_id)))
    res = c.fetchall()
    return res[0][0]


def photos(user_id):
    a = vk.meyhod('photos.getMessagesUploadServer')
    b = requests.post(a['upload_url'], files={
        'photo': open('out/%s_class_%d.png'.format(get_class(user_id), tommorow_day()), 'rb')}).json()
    c = vk_session.method('photos.saveMessagesPhoto', {'photo': b['photo'], 'server': b['server'], 'hash': b['hash']})[
        0]
    attachment = "photo{}_{}_{}".format(c['owner_id'], c['id'], c['access_key'])
    return attachment


solid_fill = (50, 50, 50, 255)

__connection = None


def get_conection():
    global __connection
    if __connection is None:
        __connection = sqlite3.connect('quick.db')
    return __connection


def get_lesson_tomorrow(class_name):
    conn = get_conection()
    c = conn.cursor()
    c.execute('SELECT lesson_%d FROM class WHERE class_name = \'%s\'' % (tommorow_day(), class_name))
    res = c.fetchall()
    return res[0][0]


image_list = []


def crate_image(class_name):
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
    # 255 82 82
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


def main():
    for event in longpool.listen():
        user_id = event.obj.from_id
        if event.type == VkBotEventType.MESSAGE_NEW:
            if not check_reg(event.obj.from_id):
                register_new_user(event.obj.from_id)
            # print('Новое сообщение:')
            # print('Для TEST от: ', end='')
            # print(event.obj.from_id)
            # print('Текст:', event.obj.text + '\n')
            # print(event.obj)
            response = str(event.obj.text)
            if response.lower() == 'начать' or response.lower() == 'старт':
                vk.messages.send(
                    user_id=user_id,
                    message='Привет.\nВыбери свой класс',
                    keyboard=create_keyboard(response, user_id),
                    random_id=get_random_id()
                )

            elif response == '10-а' or response == '10-г' or response == '10-е':
                # print(response)
                user_class = response
                add_class(user_class, 'ready', user_id)
                vk.messages.send(
                    user_id=user_id,
                    message='А теперь можешь посмотреть расписание на завтрашний день🎈',
                    keyboard=create_keyboard(response, user_id),
                    random_id=get_random_id()
                )
            elif response.lower() == 'расписание на завтра':
                vk.messages.send(
                    user_id=user_id,
                    message='Выбери подходящий для тебя вариант вывода расписания.\n*Для вывода расписания с помощью картинки потребуется время',
                    keyboard=create_keyboard(response, user_id),
                    random_id=get_random_id()
                )
            elif response.lower() == 'картинкой🖼':

                vk.messages.send(
                    user_id=user_id,
                    message='Секундочку)',
                    # keyboard=create_keyboard(response, user_id),
                    random_id=get_random_id()
                )
                t2 = threading.Thread(target=crate_image, args=(get_class(user_id)))
                
                a = vk_session.method('photos.getMessagesUploadServer')
                b = requests.post(a['upload_url'], files={
                    'photo': open('out/{}_class_{}.png'.format(get_class(user_id), tommorow_day()), 'rb')}).json()
                c = vk_session.method('photos.saveMessagesPhoto',
                                      {'photo': b['photo'], 'server': b['server'], 'hash': b['hash']})[0]
                # print(c)
                attachment = "photo{}_{}_{}".format(c['owner_id'], c['id'], c['access_key'])
                # print(attachment)
                vk.messages.send(
                    user_id=user_id,
                    message='Держи:',
                    attachment=attachment,
                    keyboard=create_keyboard(response, user_id),
                    random_id=get_random_id()
                )
            elif response.lower() == 'текстом📝':
                morning, day = t_w.weather_r()
                vk.messages.send(
                    user_id=user_id,
                    message='Держи:\n' + lesson(user_id) + '\n\nПогода на завтра\n  Утром: ' + str(
                        morning) + '°C\n  Днем: ' + str(day) + '°C',
                    keyboard=create_keyboard(response, user_id),
                    random_id=get_random_id()
                )
            else:
                if check_state(user_id) == 'ready':
                    vk.messages.send(
                        user_id=user_id,
                        message='❌Я тебя не понял. Давай попробуем заново.❌',
                        keyboard=create_keyboard(response, user_id),
                        random_id=get_random_id()
                    )
                elif check_state(user_id) == 'no_ready':
                    vk.messages.send(
                        user_id=user_id,
                        message='Я еще не знаю в каком ты классе.\nВыбери свой класс:',
                        keyboard=create_keyboard(response, user_id),
                        random_id=get_random_id()
                    )

t1 = threading.Thread(target=main)
t2 = threading.Thread(target=crate_image())

