import time
import sqlite3

import ege_parser

from termcolor import colored

# TODO: Custom timeout


def parsePassports():
    egeObject = ege_parser.Ege(0, 0)

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
                    cur.execute("INSERT OR IGNORE INTO passport_data\
                                 VALUES (?, ?)", (serial, number))
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
                    print(colored("Too many errors, waiting 45 seconds\
                                   and skipping...", "red"))
                    lastErrors = 0
                    time.sleep(45)
                else:
                    print(colored("Waiting 15 seconds...", "yellow"))
                    time.sleep(15)
                    lastErrors = lastErrors + 1
                    number = number - 1
                    print("Trying to resend the request...")
