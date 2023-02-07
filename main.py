"""
Парсит excel-файл (имя файла задаётся аргументом командной строки, по
умолчанию – table.xlsx). Заменяет в полученной таблице data1 на сегодняшнюю
дату, а data2 – на завтрашнюю. Записывает таблицу в БД. Дополнительно
записывает в таблицу расчётный тотал по Qliq и Qoil, сгрупированный по датам.
"""

import os
from argparse import ArgumentParser
from datetime import date

import pandas as pd
import psycopg2


if __name__ == "__main__":
    parser = ArgumentParser(
        prog="excel_parser", description="Вносит данные из xlsx-таблицы в БД."
    )
