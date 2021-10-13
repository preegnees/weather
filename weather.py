#!/usr/bin/python
import requests
import subprocess
from pprint import pprint
# from ipdata import ipdata
import json
import ast
import os.path
from sys import platform
from decimal import Decimal
from sys import platform


def init_platform():
    os_android = "android"
    os_other = "other"
    path_os = os.path.normpath("os.txt")
    bool_os = os.path.exists(path_os)
    if not bool_os:
        try:
            cmd_for_init = "termux-open"
            out = subprocess.Popen(cmd_for_init, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            out.communicate()[0].decode().rstrip("\n")
            with open("os.txt", "w") as file:
                file.write(os_android)
            return os_android
        except:
            with open("os.txt", "w") as file:
                file.write(os_other)
            return os_other
    else:
        try:
            with open("os.txt", "r") as file:
                out = file.readline()
            if out == os_android and (platform != "win32" and (platform == "linux" or platform == "linux2")):
                return os_android
            elif out == os_other:
                return os_other
            else:
                os.remove("os.txt")
                init_platform()
        except:
            print("Error: ошибка инициализации")
            raise SystemExit


def get_ip(path_ip, cmd_for_ip):
    try:
        # out = subprocess.Popen(cmd_for_ip, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        # ip = out.communicate()[0].decode().rstrip("\n")
        ################################
        ip = "5.18.199.35"
        ################################
        ip_test = ip.split(".")
        if len(ip_test) != 4:
            print("ip is not valid")
            raise Exception()
        with open("ip.txt", "w") as file:
            file.write(ip)
        return ip
    except:
        print("Error: ошибка в выполнении команды-демона (невозможно получить ip, проверим в файле)")
        if os.path.exists(path_ip):
            with open("ip.txt", "r") as file:
                ip = file.readline()
        else:
            print("Error: файла нет, ip невозможно получить")
            raise SystemExit
        return ip


def get_coordinates(path_lat, path_lon, ip, key):
    if (not os.path.exists(path_lon)) or (not os.path.exists(path_lat)):
        try:
            # ipdata = ipdata.IPData(key)
            # response = ipdata.lookup(ip)
            # latitude = response.get("latitude")
            # longitude = response.get("longitude")
            ##########################################
            latitude = "59.8983"
            longitude = "30.2618"
            ##########################################
            with open("lat.txt", "w") as file:
                file.write(latitude)
            with open("lon.txt", "w") as file:
                file.write(longitude)
            return latitude, longitude
        except:
            print(
                "Error: возможно у вас отсутствует интернет соединение "
                "(невозможно получить широту и долготу, данные возьмутся из файла, если он есть)"
            )
            if os.path.exists(path_lat) and os.path.exists(path_lon):
                with open("lat.txt", "r") as file:
                    latitude = file.readline()
                with open("lon.txt", "r") as file:
                    longitude = file.readline()
                return latitude, longitude
            else:
                print("Error: к сожелаению, файлов нет")
                raise SystemExit
    else:
        if os.path.exists(path_lat) and os.path.exists(path_lon):
            with open("lat.txt", "r") as file:
                latitude = file.readline()
            with open("lon.txt", "r") as file:
                longitude = file.readline()
            return latitude, longitude
        else:
            print("Error: к сожелаению, файлов нет")
            raise SystemExit


def get_weather(latitude, longitude, lang, api_key_weather, system):
    try:
        json_weather = requests.get(
            "https://api.openweathermap.org/data/2.5/weather?lat={}&lon={}&lang={}&appid={}&units={}"
                .format(latitude, longitude, lang, api_key_weather, system))
        data = json.loads(json_weather.text)
    except:
        print("Error: возможно у вас отсутствует интернет соединение (невозможно получить данные о погоде)")
        raise SystemExit
    try:
        city = data.get("name")
        country = data["sys"]["country"]
        description = data["weather"][0]["description"]
        temp = str(round(float((data["main"]["temp"]) - 273.0), 2))  # температура С
        humidity = str(round(data["main"]["humidity"], 2))  # влажность %
        speed = str(round(data["wind"]["speed"], 2))  # скорость м/с
        clouds = str(round(data["clouds"]["all"], 2))  # облачность %
        return city, country, description, temp, humidity, speed, clouds
    except:
        print("Error: ошибка в парсинге данных")
        raise SystemExit


################################################################
def get_png():
    try:
        print("get png")
        #  http://openweathermap.org/img/wn/10d@2x.png get png
    except:
        print("png default")
        # png default


#################################################################


def get_full_data(path_ip, path_lat, path_lon, cmd_for_ip, api_key_ip, api_key_weather, lang, system):
    ip = get_ip(path_ip=path_ip, cmd_for_ip=cmd_for_ip)
    (latitude, longitude) = get_coordinates(path_lat=path_lat, path_lon=path_lon, ip=ip, key=api_key_ip)
    (city, country, description, temp, humidity, speed, clouds) = get_weather(latitude=latitude,
                                                                              longitude=longitude,
                                                                              lang=lang,
                                                                              api_key_weather=api_key_weather,
                                                                              system=system)
    return ip, latitude, longitude, city, country, description, temp, humidity, speed, clouds


def notification_android(latitude, longitude, ip, city, country, description, temp, humidity, speed, clouds):

    content = \
        "Широта: {}; ".format(latitude)+\
        "Долгота: {}; \n".format(longitude)+\
        "IP: {}; \n".format(ip)+\
        "Город: {}; ".format(city)+\
        "Старна: {}; \n".format(country)+\
        "Описание: {}; \n".format(description)+\
        "Температура: {} C; \n".format(temp)+\
        "Влажность: {} %; \n".format(humidity)+\
        "Скорость ветра: {} м/с; \n".format(speed)+\
        "Oблачность: {} %; ".format(clouds)
    
    message = \
        "termux-notification "+\
        "--id 0 "+\
        "--group weather "+\
        "--button1 \"обновить\" "+\
        "--button1-action \"update\" "+\
        "--button2 \"стоп\" "+\
        "--button2-action \"stop\" "+\
        "--button3 \"обновить все\" "+\
        "--button3-action \"update_all\" "+\
        "--priority high "+\
        "--title \"Погода\" "+\
        "--content \"{}\" --button1-action \"{}\" --button2-action \"{}\" --button3-action \"{}\" "
    subprocess.Popen([
        message.format(content, update(), stop(), update_all())
    ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    


def update():
    subprocess.Popen(["termux-notification-remove 0"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    return "python3 /data/data/com.termux/files/home/myPython/trackIP/main_weather/weather.py"
def update_all():
    os.remove("ip.txt")
    os.remove("os.txt")
    os.remove("lat.txt")
    os.remove("lon.txt")
    subprocess.Popen(["termux-notification-remove 0; termux-vibrate -d 25"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    return "python3 /data/data/com.termux/files/home/myPython/trackIP/main_weather/weather.py; termux-vibrate -d 25"
def stop():
    return "termux-notification-remove 0; termux-vibrate -d 150"
    raise SystemExit


def main():
    cmd_for_ip = ["wget -q -O - ifconfig.me/ip"]
    api_key_ip = "f46a15796b4a9aacc6ca4bafaa2bf0e9c6430cd0c9fba7d7b93258fa"
    path_ip = os.path.normpath("ip.txt")
    api_key_weather = "25d1e5f60773532ffa0f649508fc8b32"
    lang = "ru"
    system = "standard"
    path_lat = os.path.normpath("lat.txt")
    path_lon = os.path.normpath("lon.txt")

    init = init_platform()
    if init == "android":
        (ip, latitude, longitude, city, country, description, temp, humidity, speed, clouds) = \
            get_full_data(path_ip=path_ip,
                          path_lat=path_lat,
                          path_lon=path_lon,
                          cmd_for_ip=cmd_for_ip,
                          api_key_ip=api_key_ip,
                          api_key_weather=api_key_weather,
                          lang=lang,
                          system=system)
        notification_android(latitude=latitude,
                             longitude=longitude,
                             ip=ip,
                             city=city,
                             country=country,
                             description=description,
                             temp=temp,
                             humidity=humidity,
                             speed=speed,
                             clouds=clouds)
        print("Широта: ", latitude)
        print("Долгота ", longitude)
        print("IP: ", ip)
        print("город: ", city)
        print("страна: ", country)
        print("описание: ", description)
        print("температра: ", temp)
        print("влажность: ", humidity)
        print("скорость: ", speed)
        print("облачность: ", clouds)
        #  cmd for termux + icon weather
    else:
        (ip, latitude, longitude, city, country, description, temp, humidity, speed, clouds) = \
            get_full_data(path_ip=path_ip,
                          path_lat=path_lat,
                          path_lon=path_lon,
                          cmd_for_ip=cmd_for_ip,
                          api_key_ip=api_key_ip,
                          api_key_weather=api_key_weather,
                          lang=lang,
                          system=system)
        print("Широта: ", latitude)
        print("Долгота ", longitude)
        print("IP: ", ip)
        print("город: ", city)
        print("страна: ", country)
        print("описание: ", description)
        print("температра: ", temp, "C")
        print("влажность: ", humidity, "%")
        print("скорость: ", speed, "м/с")
        print("облачность: ", clouds, "%")


if __name__ == '__main__':
    main()
