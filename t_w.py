import requests
import datetime
import time

city = 'Alnashi'
url = 'http://api.openweathermap.org/data/2.5/forecast?&units=metric&q=%s&appid=295f286d77a869327ed8dfae72a0542d'
d = []
l = []
def check_time():
    return str(datetime.date.today() + datetime.timedelta(days=1))
temperatures = []
def weather():
    r = requests.get(url % (city))
    data = r.json()
    temp = data["list"]
    for id in temp:
        tmp = id["main"]["temp"]
        tmp = str(round(tmp))
        dt = id["dt_txt"]
        l.append(dt + ' ' + tmp)
    for x in l:
        if x.split(' ')[0] == str(check_time()):
            temperatures.append(x.split(' ')[2].split())
    morning = temperatures[2][0]
    day = temperatures[5][0]
    return morning, day
def weather_r():
    try:
        temp_t_m, temp_t_d = weather()
        return temp_t_m, temp_t_d
    except:
        time.sleep(2)
        temp_t_m_, temp_t_d_ = weather_r()
        return temp_t_m_, temp_t_d_
    