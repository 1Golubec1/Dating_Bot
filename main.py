import random
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, KeyboardButton, InlineKeyboardButton
from random import choice
from config import *
from parse_cities import Parse_cities


# ----------------------------Button------------------------

wom_bt = KeyboardButton("жен")
man_bt = KeyboardButton("муж")
profile_bt = KeyboardButton("наша анкета")
edit_profile_bt = KeyboardButton("изменить анкету")
freeze_bt = KeyboardButton("заморозить анкету")
see_profile_bt = KeyboardButton("смотреть анкеты")
defrost_bt = KeyboardButton("разморозить анкету")
wom_gender_bt = KeyboardButton("женский")
man_gender_bt = KeyboardButton("мужской")
menu_back_bt = KeyboardButton("главное меню")
next_profile_bt = KeyboardButton('дальше')
like_bt = KeyboardButton("❤")
dislike_bt = KeyboardButton("✖")

# ----------------------------Keyboard-----------------------

gen_key = ReplyKeyboardMarkup(resize_keyboard=True)
gen_key.add(wom_bt, man_bt)

main_kb = ReplyKeyboardMarkup(resize_keyboard=True)
main_kb.add(profile_bt, edit_profile_bt, freeze_bt, see_profile_bt)

main2_kb = ReplyKeyboardMarkup(resize_keyboard=True)
main2_kb.add(profile_bt, edit_profile_bt, defrost_bt)

gender_kb = ReplyKeyboardMarkup(resize_keyboard=True)
gender_kb.add(wom_gender_bt, man_gender_bt)

find_kb = ReplyKeyboardMarkup(resize_keyboard=True)
find_kb.add(menu_back_bt, next_profile_bt)

rate_kb = ReplyKeyboardMarkup(resize_keyboard=True)
rate_kb.add(like_bt, dislike_bt, menu_back_bt)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# GLOBAL VAR




def save_men(men):
    f = open(MAN, "w", encoding="UTF-8")
    for id, info in men.items():
        f.write(f"{id} {info['STATE']} {info['GEN']} {info['AGE']} {info['DES']} {info['CITY']} {info['NAME']} {info['ENABLE']} {info['FIND_GEN']} {' '.join(info['LIKE_ID'])}\n")


def get_men():
    f = open(MAN, "r", encoding="UTF-8")
    men = {}
    if f != "":
        f.seek(0)
        for i in f:
            s = i.split()
            id, state, gen, age, des, city, name, enable, find_gen, like_id = s[0], s[1], s[2], s[3], s[4], s[5], s[6], s[7], s[8], s[9:]
            men[id] = {"STATE": state, "GEN": gen, "AGE": age, "DES": des, "CITY": city, "NAME": name, "ENABLE": enable, "FIND_GEN": find_gen, 'LIKE_ID': like_id}
        f.close()
    return men


def get_profile(id):
    men_dict = get_men()
    find_gen = men_dict[id]["FIND_GEN"]
    profiles_list = []
    for user_id, info in men_dict.items():
        if info["GEN"] == find_gen and user_id != id :
            profiles_list.append(f"{user_id} {info['NAME']} {info['AGE']} {info['CITY']}  {info['DES']}")
    return choice(profiles_list)


def add_like(my_id, add_id):
    men = get_men()
    if my_id not in men[add_id]["LIKE_ID"]:
        men[add_id]["LIKE_ID"].append(my_id)
        save_men(men)


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    user_id = str(message.from_user.id)
    men = get_men()
    man_add = {}
    man_add[user_id] = {"STATE": "START", "GEN": None, "AGE": None, "DES": None, "CITY": None, "NAME": None, "ENABLE": "NO", "FIND_GEN": None, "LIKE_ID": []}
    men.update(man_add)
    save_men(men)
    await message.answer(f"выберите пол", reply_markup=gen_key)
    print(type(man_add[user_id]['LIKE_ID']))

@dp.message_handler()
async def dav(message: types.Message):
    user_id = str(message.from_user.id)
    men = get_men()

    if message.text == "смотреть анкеты":
        men[user_id]['STATE'] = "GENDER"
        save_men(men)
        await message.answer("выберети пол", reply_markup=gender_kb)

    elif men[user_id]["STATE"] == "START":
        if message.text == "муж":
            men[user_id]["GEN"] = "man"

        if message.text == "жен":
            men[user_id]["GEN"] = "wom"

        men[user_id]["STATE"] = "AGE"
        save_men(men)
        await message.answer("напишите свой возраст", reply_markup=types.ReplyKeyboardRemove())

    elif men[user_id]["STATE"] == "AGE":

        if message.text.isdigit() and 16 <= int(message.text) <= 100:
            age = message.text
            men[user_id]["AGE"] = age
            men[user_id]["STATE"] = "CITY"
            save_men(men)
            await message.answer("Напишите свой город")
        else:
            await message.answer("Введите коррекный возраст (16 - 100)")

    elif men[user_id]["STATE"] == "CITY" or men[user_id]["STATE"] == "EDIT_PROFILE":
        pc = Parse_cities("russian-cities.json")
        if message.text in pc.get_cities():
            city = message.text
            men[user_id]["CITY"] = city
            men[user_id]["STATE"] = "NAME"
            save_men(men)
            await message.answer("Напишите свое имя")
        else:
            await message.answer("Такого города нет или введите с большой буквы")

    elif men[user_id]["STATE"] == "NAME":
        name = message.text
        men[user_id]["NAME"] = name
        men[user_id]["STATE"] = "DES"
        save_men(men)
        await message.answer("напишите свое описание")

    elif men[user_id]["STATE"] == "DES":
        men[user_id]["DES"] = message.text
        save_men(men)
        if len(men[user_id]["DES"]) > 300:
            des = "many"
            men[user_id]["DES"] = des
            await message.answer("Ваше описание превышает лимит символов (300). Введите новое описание")
        else:
            men[user_id]["STATE"] = "PHOTO"
            await message.answer("Отправьте фото (не документом)")
        save_men(men)
    elif message.text == "наша анкета":
        men[user_id]["STATE"] = "PROFILE"
        name = men[user_id]["NAME"]
        age = men[user_id]["AGE"]
        city = men[user_id]["CITY"]
        des = men[user_id]["DES"]
        photo = open("img/" + str(user_id) + ".jpg", "rb")
        await message.answer(f"{name}\n{age}\n{city}\n{des}", reply_markup=main_kb)
        await bot.send_photo(chat_id=message.chat.id, photo=photo)

    elif message.text == "изменить анкету":
        men[user_id]["STATE"] = "EDIT_PROFILE"
        men[user_id]["ENABLE"] = "NO"
        save_men(men)
        await message.answer("Напишите свой город", reply_markup=types.ReplyKeyboardRemove())
    elif message.text == "смотреть анкеты":
        save_men(men)
    elif message.text == "заморозить анкету":
        men[user_id]["ENABLE"] = "NO"
        save_men(men)
        await message.answer("анкета скрыта", reply_markup=main2_kb)

    elif message.text == "разморозить анкету":
        men[user_id]["ENABLE"] = "YES"
        save_men(men)
        await message.answer("анкета открыта", reply_markup=main_kb)


    elif men[user_id]['STATE'] == "GENDER":
        if message.text == "мужской":
            men[user_id]['FIND_GEN'] = "man"
        elif message.text == "женский":
            men[user_id]['FIND_GEN'] = "wom"

        men[user_id]["STATE"] = "SEARCH"
        save_men(men)
        await message.answer("фильтр настроен", reply_markup=find_kb)

    elif message.text == "главное меню":
        men[user_id]["STATE"] = "MENU"
        save_men(men)
        await message.answer("вы вернулись в главное меню", reply_markup=main_kb)

    elif message.text == "✖" or message.text == "дальше":
        pr = get_profile(user_id).split(" ")
        if abs(int(pr[2]) - int(men[user_id]["AGE"])) <= 2:
            id_ = pr[0]
            ff = open("like_id.txt", "a", encoding="UTF-8")
            ff.write(f'{user_id} {id_}\n')
            ff.close()
            photo = open("img/" + str(id_) + ".jpg", "rb")
            await message.answer(f"{pr[0]}\n{pr[1]}\n{pr[2]}\n{pr[3]}\n{pr[5]}",  reply_markup=rate_kb)
            await bot.send_photo(chat_id=message.chat.id, photo=photo)

    elif message.text == "❤":
        f = open('like_id.txt', 'r', encoding="UTF-8")
        r = f.read()
        rr = r.split("\n")
        print(rr)
        baza = []
        add_id = 0
        if user_id in r:
            for i in rr:
                if i.split()[0] == user_id:
                    add_id = i.split()[1]
                    add_like(user_id, add_id)
                    f.close()
                    break
                elif user_id not in i:
                    baza.append(i)
        print(baza)
        g = open("like_id.txt", "w", encoding="UTF-8")
        for y in baza:
            g.write(f"{y}\n")
        g.close()
        pr = get_profile(user_id).split(" ")
        if abs(int(pr[2]) - int(men[user_id]["AGE"])) <= 2:
            ff = open("like_id.txt", "a", encoding="UTF-8")
            id_ = pr[0]
            photo = open("img/" + str(id_) + ".jpg", "rb")
            ff.write(f'{user_id} {id_}\n')
            ff.close()
            await message.answer(f"{pr[0]}\n{pr[1]}\n{pr[2]}\n{pr[3]}\n{pr[5]}",  reply_markup=rate_kb)
            await bot.send_photo(chat_id=message.chat.id, photo=photo)

@dp.message_handler(content_types=['photo'])
async def get_photo(message: types.Message):
    user_id = str(message.from_user.id)
    men = get_men()
    if men[user_id]["STATE"] == "PHOTO":
        await message.photo[-1].download("img/" + user_id + ".jpg")
        await message.answer("Ваша анкета заполнена", reply_markup=main_kb)
        men[user_id]["ENABLE"] = "YES"
        save_men(men)
    else:
        await message.answer("сейчас фотография не нужна")

executor.start_polling(dp)
