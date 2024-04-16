import sqlite3
from typing import List, Union


class SqlWrapper:
    """
    SQL Wrapper to create a connection to the database automatically and handle queries
    """
    def __init__(self, db_file: str = r".\database") -> None:
        self.db_file = db_file
        self.db = sqlite3.connect(self.db_file)
        self.cursor = self.db.cursor()
        
    def execute_query(self, sql_query: str) -> None:
        self.cursor.execute(sql_query)
        
    def select_query(self, table: str, 
                     columns: List[str], 
                     where: str = None, 
                     order_by: str = None,
                     limit: int = None,
                     fetch_all: bool = True) -> Union[str, List[str]]:
        """
        Creates a SELECT query

        Args:
            table: The table to SELECT fields from
            columns: The column(s) to SELECT from
            where: A condition for the values returned
            order_by: Order the values returned. Must be parsed as '{column name} ASC/DESC'
            limit: Limits the number of rows returned
            fetch_all: True to get all values, False to get one value
        """
        sql_query = f"SELECT {', '.join([c for c in columns])} FROM {table}"
        if where is not None:
            sql_query += f" WHERE {where}"
        if limit is not None:
            sql_query += f" ORDER BY {order_by}"
        if limit is not None:
            sql_query += f" LIMIT {limit}"

        self.execute_query(sql_query)
        if fetch_all:
            return self.cursor.fetchall()
        else:
            return self.cursor.fetchone()
        
    def close(self) -> None:
        self.db.close()
    
if __name__ == "__main__":
    sql = SqlWrapper(r"C:\Users\willb\Desktop\Work\Uni\Databases Assessment\database")
    print(sql)