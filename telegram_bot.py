import logging
import time
from threading import Thread

import argparse
import sqlite3

from telegram.ext import Updater
from telegram.ext import CommandHandler

import ege_parser

class Data():
    """Работа с данными, удаление/добавление паспортов"""

    con = sqlite3.connect('bot_data.db')
    cur = None

    def __init__(self):
        self.cur = self.con.cursor()


class EgeThread():
    """docstring for EgeThread."""

    _serial = 0
    _passport = 0

    def __init__(self, arg):
        super(EgeThread, self).__init__()
        self.arg = arg


def addPassport(update, context):
    text_caps = ' '.join(context.args).upper()

    passport_data = text_caps.split(" ", 2)

    serial = 0
    number = 0

    try:
        serial = int(passport_data[0])
        number = int(passport_data[1])
    except Exception:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Неккоректный формат паспорта, попробуйте ещё раз")
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Формат: 1234 12345678")
        return

    egeObj = ege_parser.Ege(passport_data[0], passport_data[1])
    try:
        if not egeObj.isPassportValid():
            context.bot.send_message(chat_id=update.effective_chat.id, text="Участника с таким паспортом не существует.\nПопробуйте ещё раз")
            return
    except Exception as e:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Проблемы с получением доступа к ege.spb.ru.\nПопробуйте позднее")
        print(e)
        return

    context.bot.send_message(chat_id=update.effective_chat.id, text="Добавлен паспорт: " + str(serial) + " " + str(number))


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Здравствуйте, Я бот ЕГЭ!")
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Я буду сообщать вам о новых результатах экзамена, пожалуйста, введите свою серию и номер паспорта")


def getExams(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Результаты ваших экзаменов:")

def main():

    parser = argparse.ArgumentParser(description='Telegram bot')
    parser.add_argument('token', type=str, help='Bot token')
    args = parser.parse_args()

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    updater = Updater(token=args.token, use_context=True)
    dispatcher = updater.dispatcher

    # Handlers
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)
    caps_handler = CommandHandler('addPassport', addPassport)
    dispatcher.add_handler(caps_handler)
    exams_handler = CommandHandler('getExams', getExams)
    dispatcher.add_handler(exams_handler)

    updater.start_polling()


if __name__ == "__main__":
    main()
