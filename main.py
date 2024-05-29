import telebot
from config import TELEGRAM_TOKEN, HOTELS_TOKEN, MAX_HOTELS_COUNT, MAX_PHOTOS_COUNT, no_cities
import db
import buffers
import hotelsapi
from datetime import datetime
import logging

logging.basicConfig(filename='error.log', level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(message)s')

bot = telebot.TeleBot(TELEGRAM_TOKEN)


@bot.message_handler(commands=['start'])
def start(message: telebot.types.Message):
    try:
        if message.from_user.id not in [i[0] for i in db.get_data()]:
            db.register(message)

        markup = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        itembtn1 = telebot.types.KeyboardButton('/lowprice')
        itembtn2 = telebot.types.KeyboardButton('/highprice')
        itembtn3 = telebot.types.KeyboardButton('/bestdeal')
        itembtn4 = telebot.types.KeyboardButton('/history')

        markup.add(itembtn1, itembtn2, itembtn3, itembtn4)

        bot.send_message(message.from_user.id,
                         'Вы в главном меню! \n\n'
                         'С помощью этого бота вы сможете: \n'
                         '·Найти недорогие отели в городе \n'
                         '·Найти дорогие отели в городе \n'
                         '·Найти отель по вашим параметрам \n\n'
                         'Справка по боту /help', reply_markup=markup)
    except Exception as e:
        logging.error(f"Error in start command: {e}")


@bot.message_handler(commands=['help'])
def help(message: telebot.types.Message):
    try:
        bot.send_message(message.from_user.id,
                         'Команды: \n'
                         '/lowprice — вывод самых недорогих отелей в городе \n'
                         '/highprice — вывод самых дорогих отелей в городе \n'
                         '/bestdeal — вывод отелей, наиболее подходящих по цене \n'
                         '/history — вывод истории поиска отелей')
    except Exception as e:
        logging.error(f"Error in help command: {e}")


@bot.message_handler(commands=['lowprice'])
def lowprice(message: telebot.types.Message):
    bot.send_message(message.from_user.id, 'Введите город для поиска:')
    buffers.buffer[message.from_user.id] = dict()
    buffers.buffer[message.from_user.id]['command'] = '/lowprice'
    buffers.buffer[message.from_user.id]['sort'] = 'PRICE_LOW_TO_HIGH'

    c_d = datetime.now()
    date = f'{c_d.date()} {c_d.hour}:{c_d.minute}'

    buffers.buffer[message.from_user.id]['time'] = date
    bot.register_next_step_handler(message, get_city)


@bot.message_handler(commands=['highprice'])
def highprice(message: telebot.types.Message):
    bot.send_message(message.from_user.id, 'Введите город для поиска:')
    buffers.buffer[message.from_user.id] = dict()
    buffers.buffer[message.from_user.id]['command'] = '/highprice'
    buffers.buffer[message.from_user.id]['sort'] = 'PRICE_HIGH_TO_LOW'

    c_d = datetime.now()
    date = f'{c_d.date()} {c_d.hour}:{c_d.minute}'

    buffers.buffer[message.from_user.id]['time'] = date
    bot.register_next_step_handler(message, get_city)


@bot.message_handler(commands=['bestdeal'])
def bestdeal(message: telebot.types.Message):
    bot.send_message(message.from_user.id, 'Введите город для поиска:')
    buffers.buffer[message.from_user.id] = dict()
    buffers.buffer[message.from_user.id]['command'] = '/bestdeal'

    c_d = datetime.now()
    date = f'{c_d.date()} {c_d.hour}:{c_d.minute}'

    buffers.buffer[message.from_user.id]['time'] = date
    bot.register_next_step_handler(message, get_city, 2)


@bot.message_handler(commands=['history'])
def history(message: telebot.types.Message):
    data = db.get_data(id=message.from_user.id)[0][1]

    if data:
        data = db.get_data(id=message.from_user.id)[0][1].split(';')[-12:]

        bot.send_message(message.from_user.id, '\n\n'.join(data), parse_mode='MARKDOWN')
    else:
        bot.send_message(message.from_user.id, 'Ваша история пуста')

    bot.send_message(message.from_user.id, 'Введите команду /start для запуска бота.')


@bot.message_handler(content_types=['text'])
def other_messages(message: telebot.types.Message):
    bot.send_message(message.from_user.id, 'Введите команду /start для запуска бота.')


def get_city(message: telebot.types.Message, mode=1):
    try:
        if message.text == '/start':
            bot.send_message(message.from_user.id,
                             'Вы в главном меню! \n\n'
                             'С помощью этого бота вы сможете: \n'
                             '·Найти недорогие отели в городе \n'
                             '·Найти дорогие отели в городе \n'
                             '·Найти отель по вашим параметрам \n\n'
                             'Справка по боту /help')
            return

        if message.text.lower() not in no_cities:
            preccesing = bot.send_message(message.from_user.id, 'Ищу город..')
            city_id = hotelsapi.get_region_id(message.text)
            print(city_id)
            if city_id:
                buffers.buffer[message.from_user.id]['city'] = city_id
                if mode == 1:
                    bot.edit_message_text(chat_id=message.from_user.id,
                                          message_id=preccesing.message_id,
                                          text=f'Отлично! \n'
                                               f'Теперь укажите, сколько отелей необходимо выводить в результате?'
                                               f' (не более {MAX_HOTELS_COUNT})')

                    bot.register_next_step_handler(message, get_hotels_count)
                else:
                    bot.edit_message_text(chat_id=message.from_user.id,
                                          message_id=preccesing.message_id,
                                          text=f'Отлично! \n'
                                               f'Теперь укажите диапазон цен для поиска'
                                               f' (РУБ) \n\nНапример: 2000-5000')

                    bot.register_next_step_handler(message, get_price)

            else:
                bot.edit_message_text(chat_id=message.from_user.id,
                                      message_id=preccesing.message_id,
                                      text=f'Не удается найти данный город. \n'
                                           f'Убедитесь, что вы вводите существующий город!')

                if mode == 2:
                    bot.register_next_step_handler(message, get_city, 2)
                else:
                    bot.register_next_step_handler(message, get_city)

        else:
            bot.send_message(message.from_user.id,
                             'К сожалению, сайт временно не предоставляет информации по России, выберите другой город')
            if mode == 2:
                bot.register_next_step_handler(message, get_city, 2)
            else:
                bot.register_next_step_handler(message, get_city)
    except Exception as e:
        logging.error(f'Error in get_city def command: {e}')


def get_price(message: telebot.types.Message):
    if message.text == '/start':
        bot.send_message(message.from_user.id,
                         'Вы в главном меню! \n\n'
                         'С помощью этого бота вы сможете: \n'
                         '·Найти недорогие отели в городе \n'
                         '·Найти дорогие отели в городе \n'
                         '·Найти отель по вашим параметрам \n\n'
                         'Справка по боту /help')
        return

    try:
        prices = message.text.split('-')

        min_p = int(prices[0]) // 70
        max_p = int(prices[1]) // 70

        buffers.buffer[message.from_user.id]['min_p'] = min_p
        buffers.buffer[message.from_user.id]['max_p'] = max_p

        bot.send_message(chat_id=message.from_user.id,
                         text=f'Теперь укажите расстояние для центра (КМ): \n\n'
                              f'Например: 2-3 \n'
                              f'Например: 0.1-1')

        bot.register_next_step_handler(message, get_distance)

    except:
        bot.send_message(message.from_user.id, f'Укажите диапазон цен для поиска'
                                               f' (РУБ) \n\nНапример: 2000-5000')

        bot.register_next_step_handler(message, get_price)


def get_distance(message: telebot.types.Message):
    if message.text == '/start':
        bot.send_message(message.from_user.id,
                         'Вы в главном меню! \n\n'
                         'С помощью этого бота вы сможете: \n'
                         '·Найти недорогие отели в городе \n'
                         '·Найти дорогие отели в городе \n'
                         '·Найти отель по вашим параметрам \n\n'
                         'Справка по боту /help')
        return

    try:
        distance_range = message.text.split('-')
        min_distance = float(distance_range[0])
        max_distance = float(distance_range[1])

        buffers.buffer[message.from_user.id]['min_distance'] = min_distance
        buffers.buffer[message.from_user.id]['max_distance'] = max_distance

        bot.send_message(message.from_user.id,
                         'Укажите кол-во отелей в результате \n'
                         f'(не более {MAX_HOTELS_COUNT})')

        bot.register_next_step_handler(message, get_hotels_count)

    except:
        bot.send_message(chat_id=message.from_user.id,
                         text=f'укажите расстояние до центра (КМ): \n\n'
                              f'Например: 2-3 \n'
                              f'Например: 0.1-1')
        bot.register_next_step_handler(message, get_distance)


def get_hotels_count(message: telebot.types.Message):
    if message.text == '/start':
        bot.send_message(message.from_user.id,
                         'Вы в главном меню! \n\n'
                         'С помощью этого бота вы сможете: \n'
                         '·Найти недорогие отели в городе \n'
                         '·Найти дорогие отели в городе \n'
                         '·Найти отель по вашим параметрам \n\n'
                         'Справка по боту /help')
        return

    try:
        hotels_count = int(message.text)

        if hotels_count <= MAX_HOTELS_COUNT:
            buffers.buffer[message.from_user.id]['hotels_count'] = hotels_count

            bot.send_message(message.from_user.id,
                             f'Введите даты проживания в отеле \n'
                             f'(гггг.мм.дд) \n\n'
                             f'Например: 2023.04.25 - 2023.05.01\n'
                             f'Перед и после тире поставьте пробел')

            bot.register_next_step_handler(message, get_date)

        else:
            bot.send_message(message.from_user.id, f'Введите число не более {MAX_HOTELS_COUNT}')
            bot.register_next_step_handler(message, get_hotels_count)

    except:
        bot.send_message(message.from_user.id, 'Введите целое число!')
        bot.register_next_step_handler(message, get_hotels_count)


def get_date(message: telebot.types.Message):
    if message.text == '/start':
        bot.send_message(message.from_user.id,
                         'Вы в главном меню! \n\n'
                         'С помощью этого бота вы сможете: \n'
                         '·Найти недорогие отели в городе \n'
                         '·Найти дорогие отели в городе \n'
                         '·Найти отель по вашим параметрам \n\n'
                         'Справка по боту /help')
        return

    try:
        if len(message.text.split('.')[0]) == 4:
            data = message.text.split(' - ')
            data_split = data[0].split('.')
            data2_split = data[1].split('.')

            if len(data_split[0] + data_split[1] + data_split[2]) != 8 or len(
                    data2_split[0] + data2_split[1] + data2_split[2]) != 8:

                bot.send_message(message.from_user.id,
                                 f'Введите даты проживания в отеле \n'
                                 f'(гггг.мм.дд) \n\n'
                                 f'Например: 2023.04.25 - 2023.05.01\n'
                                 f'Перед и после тире поставьте пробел')
                bot.register_next_step_handler(message, get_date)
                return

            elif int(data_split[1]) > 12 or int(data2_split[1]) > 12:
                bot.send_message(message.from_user.id,
                                 'Введите корректный месяц!')
                bot.register_next_step_handler(message, get_date)
                return

            elif int(data_split[2]) > 31 or int(data2_split[2]) > 31:
                bot.send_message(message.from_user.id,
                                 'Введите корректный день!')
                bot.register_next_step_handler(message, get_date)
                return

            buffers.buffer[message.from_user.id]['checkIn'] = data[0]
            buffers.buffer[message.from_user.id]['checkOut'] = data[1]

            check_in_date = datetime(int(data_split[0]), int(data_split[1]), int(data_split[2]))
            check_out_date = datetime(int(data2_split[0]), int(data2_split[1]), int(data2_split[2]))

            date_now = datetime.now()

            if (check_out_date - check_in_date).days < 0:
                bot.send_message(message.from_user.id,
                                 'Дата выезда не может быть раньше даты заезда!')
                bot.register_next_step_handler(message, get_date)
                return

            elif check_out_date == check_in_date:
                bot.send_message(message.from_user.id,
                                 'Дата заезда и выезда не могут быть равны!')
                bot.register_next_step_handler(message, get_date)
                return

            elif (check_in_date - date_now).days < 0:
                bot.send_message(message.from_user.id, 'Дата заезда не может ранее сегодняшней!')
                bot.register_next_step_handler(message, get_date)
                return

            elif (check_out_date - date_now).days < 0:
                bot.send_message(message.from_user.id, 'Дата выезда не может ранее сегодняшней')
                bot.register_next_step_handler(message, get_date)
                return

            delta = (check_out_date - check_in_date).days
            buffers.buffer[message.from_user.id]['delta'] = delta

            yes = telebot.types.KeyboardButton('Да')
            no = telebot.types.KeyboardButton('Нет')
            menu = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True).add(yes, no)

            bot.send_message(message.from_user.id,
                             f'Выводить фотографии отеля?',
                             reply_markup=menu)

            bot.register_next_step_handler(message, load_photo)
        else:
            bot.send_message(message.from_user.id,
                             f'Введите корректные даты проживания в отеле \n'
                             f'(гггг.мм.дд) \n\n'
                             f'Например: 2023.04.25 - 2023.05.0\n'
                             f'Перед и после тире поставьте пробел')
            bot.register_next_step_handler(message, get_date)

    except:
        bot.send_message(message.from_user.id,
                         f'Введите корректные даты проживания в отеле \n'
                         f'(гггг.мм.дд) \n\n'
                         f'Например: 2023.04.25 - 2023.05.01\n'
                         f'Перед и после тире поставьте пробел')

        bot.register_next_step_handler(message, get_date)


def load_photo(message: telebot.types.Message):
    if message.text == '/start':
        bot.send_message(message.from_user.id,
                         'Вы в главном меню! \n\n'
                         'С помощью этого бота вы сможете: \n'
                         '·Найти недорогие отели в городе \n'
                         '·Найти дорогие отели в городе \n'
                         '·Найти отель по вашим параметрам \n\n'
                         'Справка по боту /help',
                         reply_markup=telebot.types.ReplyKeyboardRemove())
        return

    if message.text == 'Да':
        buffers.buffer[message.from_user.id]['load_photo'] = True
        bot.send_message(message.from_user.id,
                         f'Отлично! Введите кол-во фото для вывода (не более {MAX_PHOTOS_COUNT})',
                         reply_markup=telebot.types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, photo_count)

    elif message.text == 'Нет':
        buffers.buffer[message.from_user.id]['load_photo'] = False
        bot.send_message(message.from_user.id, 'Ищу варианты..', reply_markup=telebot.types.ReplyKeyboardRemove())
        hotelsapi.send_hotels(message.from_user.id)
        return

    else:
        bot.send_message(message.from_user.id, 'Выберите один из вариантов!')
        bot.register_message_handler(message, load_photo)


def photo_count(message: telebot.types.Message):
    if message.text == '/start':
        bot.send_message(message.from_user.id,
                         'Вы в главном меню! \n\n'
                         'С помощью этого бота вы сможете: \n'
                         '·Найти недорогие отели в городе \n'
                         '·Найти дорогие отели в городе \n'
                         '·Найти отель по вашим параметрам \n\n'
                         'Справка по боту /help')
        return

    try:
        photo_c = int(message.text)
    except:
        bot.send_message(message.from_user.id, f'Введите целое число')
        bot.register_next_step_handler(message, photo_count)
        return

    if photo_c <= MAX_PHOTOS_COUNT:
        buffers.buffer[message.from_user.id]['photo_count'] = photo_c
        bot.send_message(message.from_user.id, 'Ищу варианты..', reply_markup=telebot.types.ReplyKeyboardRemove())
        hotelsapi.send_hotels(message.from_user.id)
        return

    else:
        bot.send_message(message.from_user.id, f'Введите число не более {MAX_PHOTOS_COUNT}')
        bot.register_next_step_handler(message, photo_count)


bot.polling(non_stop=True, timeout=25)

print()
