"""
Модель таблицы.
"""

from sqlalchemy import CheckConstraint, Column, Date, Integer, String
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Table(Base):
    """
    Класс для таблицы, где мы будем хранить данные.
    """

    __tablename__ = "table"
    id = Column("id", Integer, primary_key=True)
    company = Column("company", String, nullable=False)

    metric = Column(
        "metric", String, CheckConstraint('metric = "Qliq" or metric = "Qoil"')
    )

    date = (Column("date", Date),)
    fact = Column("fact", Integer)
    forecast = Column("forecast", Integer)

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
