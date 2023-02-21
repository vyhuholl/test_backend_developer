"""
Модель таблицы.
"""

from sqlalchemy import CheckConstraint, Column, Date, Integer, String
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Data(Base):
    """
    Класс для таблицы, где мы будем хранить данные.
    """

    __tablename__ = "data"
    id = Column("id", Integer, primary_key=True)
    company = Column("company", String, nullable=False)
    metric = Column("metric", String)
    date = Column("date", Date)
    fact = Column("fact", Integer)
    forecast = Column("forecast", Integer)
    check = CheckConstraint("metric = 'Qliq' or metric = 'Qoil'")

    def __repr__(self) -> str:
        return f"""
        {self.date} {self.company} получила {self.fact} {self.metric}
        Прогноз: {self.forecast}
        """


def create_tables(engine: Engine) -> None:
    """
    Создаёт таблицу (предварительно удалив, если она уже существует).

    Args:
        engine: двигатель SQLAlchemy
    """
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
