"""
Вспомогательные функции.
"""

from datetime import date
from random import choice
from typing import Tuple


def get_two_dates() -> Tuple[date, date]:
    """
    Генерирует две даты – первая это сегодняшний день, а вторая – случайный
    день текущего месяца, отличный от сегодняшнего.

    Returns:
        две даты
    """
    data1 = date.today()

    if data1.month == 2:
        possible_days = list(range(1, 29))
    elif data1.month in [4, 6, 9, 11]:
        possible_days = list(range(1, 31))
    else:
        possible_days = list(range(1, 32))

    possible_days.remove(data1.day)
    return data1, date(data1.year, data1.month, choice(possible_days))
