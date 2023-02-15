"""
Записывает данные из excel-таблицы в БД.
"""

import os
from argparse import ArgumentParser
from copy import deepcopy

import numpy as np
import pandas as pd
from sqlalchemy import create_engine, URL
from sqlalchemy.types import Date, Integer, String
from tabulate import tabulate

from models import create_tables, Table
from queries import query
from utils import get_two_dates

DB_USER = os.getenv("DB_USER", os.getenv("USER", "postgres"))
DB_PASS = os.getenv("DB_PASS", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "postgres")

url = URl.create(
    "postgresql+psycopg2",
    username=DB_USER,
    password=DB_PASS,
    host=DB_HOST,
    database=DB_NAME,
)


def get_metric_df(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """
    Оставляет в таблице только строки с определённым значением верхнего
    заголовка. Это значение записывает в столбец metric. Верхний уровень
    заголовка убирает.

    Args:
        df: таблица с двумя или более уровнями заголовка
        column: нужное нам название столбцов

    Returns:
        модифицированную таблицу
    """
    df_column = deepcopy(df[[column]])
    df_column["metric"] = column
    df_column.columns = df_column.columns.droplevel()
    return df_column.rename(columns={"": "metric"})


def parse_table(filename: str) -> pd.DataFrame:
    """
    Читает excel-таблицу. Реструктирует её. Приводит к нормальному виду (без
    мультииндексов, одна ячейка хранит одно значение). Заменяет data1 на
    сегодняшнюю дату, а data2 – на другую случайную дату текущего месяца.

    Args:
        filename: название файла с excel-таблицей

    Returns:
        датафрейм с преобразованной таблицей
    """
    # Читаем таблицу. Пока что пропускаем первый ряд – мы и так помним, что в
    # первой половине таблицы у нас fact, а во второй – forecast. Индексом
    # делаем название компании.
    df = pd.read_excel("table.xlsx", header=[0, 1], index_col=1, skiprows=1)
    df = df.drop(columns=df.columns[0])

    # Делаем так, чтобы Qliq и Qoil были не заголовками, а значениями в столбце
    # metric. Тогда у нас станет на один уровень заголовков меньше! Но таблица
    # станет в 2 раза длиннее.
    df = pd.concat([get_metric_df(df, "Qliq"), get_metric_df(df, "Qoil")])

    # Делаем company не индексом, а столбцом
    df = df.reset_index(names="company")

    # Убираем столбец metric в начало таблицы
    df = df[["company", "metric", "data1", "data2", "data1.1", "data2.1"]]

    # Убираем дублирующиеся столбцы с датами. При этом таблица становится в два
    # раза длиннее – в первой половине таблицы у нас fact, а во второй forecast
    df = pd.concat(
        [
            df.drop(columns=["data1.1", "data2.1"]),
            df.drop(columns=["data1", "data2"]).rename(
                columns={"data1.1": "data1", "data2.1": "data2"}
            ),
        ]
    )

    # Делаем из двух столбцов data1 и data2 один столбец date (при этом таблица
    # становится ещё в 2 раза длиннее)
    df = pd.DataFrame(
        {
            "company": ["data1", "data2"] * len(df),
            "metric": ["Qliq"] * len(df) + ["Qoil"] * len(df),
            "date": ["data1", "data2"] * len(df),
            "value": df[["data1", "data2"]].to_numpy().flatten(),
        }
    )

    # И вот теперь мы наконец-то можем добавить столбцы fact и forecast. При
    # этом таблица станет в 2 раза короче.
    forecast = deepcopy(df["value"][len(df) // 2 :])
    df = df.iloc[: len(df) // 2, :].rename(columns={"value": "fact"})
    df["forecast"] = forecast.tolist()

    # Заменяем даты на сегодняшнюю и любую другую этого месяца.
    data1, data2 = get_two_dates()
    df["date"] = pd.to_datetime(np.where(df["date"] == "data1", data1, data2))
    return df


def main(filename: str) -> None:
    """
    Читает excel-таблицу, реструктурирует её, создаёт базу данных и наполняет
    её данными из таблицы. Также подсчитывает и выводит на экран расчётный
    тотал по Qoil и Qliq, сгруппированный по датам.

    Args:
        filename: название файла с excel-таблицей
    """
    df = parse_table(filename)
    engine = create_engine(url)
    create_tables(engine)

    with engine.connect() as connection:
        df.to_sql(
            "table",
            connection,
            dtype={
                "company": String(),
                "metric": String(),
                "date": Date(),
                "fact": Integer(),
                "forecast": Integer(),
            },
        )
        connection.commit()
        result = connection.execute(query)
        print(tabulate(result.fetchall(), headers=result.keys(), tablefmt="psql"))


if __name__ == "__main__":
    parser = ArgumentParser(
        prog="excel_parser", description="Вносит данные из xlsx-таблицы в БД."
    )

    parser.add_argument(
        "filename", nargs="?", default="table.xlsx", help="Excel-файл для парсинга"
    )

    args = parser.parse_args()
    main(args.filename)
