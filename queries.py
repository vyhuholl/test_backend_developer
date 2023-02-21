"""
SQL-запросы.
"""

from sqlalchemy.sql.expression import text

query = text(
    """
    SELECT metric, date, SUM(fact) AS fact, SUM(forecast) AS forecast
    FROM data
    GROUP BY date, metric
    ORDER BY date, metric
    """
)
