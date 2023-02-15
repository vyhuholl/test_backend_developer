"""
SQL-запросы.
"""

query = """
SELECT metric, SUM(fact), SUM(forecast)
FROM table
GROUP BY metric, date
"""
