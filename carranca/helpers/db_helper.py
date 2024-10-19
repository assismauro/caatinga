"""
    Database data retrieve operations helper

    mgd
    Equipe da Canoa -- 2024
"""

# cSpell:ignore psycopg2 sqlalchemy

from typing import Any, Union, Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text

from ..main import shared
from .py_helper import is_str_none_or_empty


def execute_sql(query: str):
    """ Runs an SQL query and returns the result """
    result = None
    if not is_str_none_or_empty(query):
        with shared.sa_engine().connect() as connection:
            _text = text(query)
            result = connection.execute(_text)

    return result


def retrieve_data(query: str) -> Optional[Union[Any, Tuple]]:
  """
  Executes the given SQL query and returns the result in 3 modes:
    1.  N rows c column
    1.  N rows 1 column
    2.  1 row N columns
    3.  1 row 1 column

  Args:
    sql: The SQL query to execute.

  Returns:
    - A tuple of values if the query returns multiple rows with a single column each.
    - A tuple of values if the query returns a single row with multiple columns.
    - A single value if the query returns a single row with a single column.
    - None if an error occurs or the query returns no results.
  """

  try:
    data_rows = execute_sql(query)
    rows = data_rows.fetchall()

    if not rows:
        return None
    elif len(rows) > 1 and len(rows[0]) > 1:
        # Multiple rows with multiple columns
        return tuple(tuple(row) for row in rows)
    elif len(rows) > 1:
        # Multiple rows with one column each
        return tuple(line[0] for line in rows)
    elif len(rows[0]) > 1:
        # Single row with multiple columns
        return tuple(rows[0])
    else:
        # Single row with a single column
        return rows[0][0]
  except Exception as e:
    shared.app_log.error(f"An error occurred retrieving db data [{query}]: {e}")
    return None


def retrieve_dict(query: str):
    """
    Executes the query and attempts to return the result as a dictionary,
    assuming the result consists of two columns (key, value) per row.

    Args:
      query: The SQL query to execute.

    Returns:
      - A dictionary where the first column is the key and the second column is the value.
      - An empty dictionary if the query returns no data or an error occurs.
    """
    data = retrieve_data(query)

    result = {}
    try:
        if data and isinstance(data, tuple):
            # Check if data contains multiple rows of at least two columns
            if all(isinstance(row, tuple) and len(row) >= 2 for row in data):
                result = {row[0]: row[1] for row in data}
            # Handle single row with multiple columns (if returned by retrieve_data)
            elif isinstance(data[0], tuple) and len(data) == 2:
                result = {data[0]: data[1]}
    except Exception as e:
        result = {}
        shared.app_log.error(f"An error occurred loading the dict from [{query}]: {e}")

    # # Check if the result is a tuple of tuples (multiple rows)
    # if isinstance(data, tuple) and all(isinstance(row, tuple) and len(row) >= 2 for row in data):
    #     # We expect at least two columns (key, value) for dictionary creation
    #     return {row[0]: row[1] for row in data}

    return result.copy() # there is a very strange error



def get_str_field_length(table_model: object, field_name: str) -> str:
    """
    Args:
      table_model: Flask SQLAlchemy Table Model
      field_name: the field name (must be string)
    Returns:
      the maximum size defined for the column in the Table Model (*not on the DB*)
    """
    fields = table_model.__table__.columns
    return fields[field_name].type.length


# eof
