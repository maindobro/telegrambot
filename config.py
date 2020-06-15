from enum import Enum

stickerid = 'CAACAgIAAxkBAALw0V7lSBNGhZhKOitOujQf5P3mffKkAAIGAAOyju0GFhth3rnAZ68aBA'
token = '1292750296:AAEkzxcONPKkkD0R8OtFoSGhMcBhqajucYg'
owmToken = 'e4a33984cbd30fc7290abc839ebf46bd'
db_file = "database.vdb"

name = ""
age = int()


class States(Enum):
    S_START = "0"
    S_ENTER_NAME = "1"
    S_ENTER_AGE = "2"
    S_END = "3"
