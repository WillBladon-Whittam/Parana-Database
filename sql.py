import sqlite3
from typing import List, Union, Tuple


class SqlWrapper:
    """
    SQL Wrapper to create a connection to the database automatically and handle queries
    """
    def __init__(self, db_file: str = r".\database") -> None:
        self.db_file = db_file
        self.db = sqlite3.connect(self.db_file)
        self.cursor = self.db.cursor()
        
    def execute_query(self, sql_query: str, sql_parameters: Tuple[str, int] = tuple()) -> None:
        self.cursor.execute(sql_query, sql_parameters)
        
    def select_query(self, sql_query, sql_parameters: Tuple[str, int] = tuple(), fetch_all: bool = True):
        """
        Creates a SELECT query

        Args:
            sql_query: An SQL Query to execute
            sql_parameters: Parameters for an SQL query
            fetch_all: If set to True, fetches all the rows returned, if set to False returns only 1
        """
        if not isinstance(sql_parameters, tuple):
            sql_parameters = (sql_parameters,)
        self.execute_query(sql_query, sql_parameters)
        if fetch_all:
            return self.cursor.fetchall()
        else:
            return self.cursor.fetchone()
        
    def update_table(self, sql_query, sql_parameters: Tuple[str, int] = tuple(), commit=True) -> Union[None, Exception]:
        """
        Creates a INSERT/UPDATE/DELETE query

        Args:
            sql_query: An SQL Query to execute
            sql_parameters: Parameters for an SQL query
            commit: Commit changes to database immediatly
        """
        if not isinstance(sql_parameters, tuple):
            sql_parameters = (sql_parameters,)
        try:
            self.execute_query(sql_query, sql_parameters)
        except sqlite3.IntegrityError as e:
            return e
        if commit:
            self.db.commit()
 
    def close(self) -> None:
        self.db.close()
    
if __name__ == "__main__":
    sql = SqlWrapper(r"C:\Users\willb\Desktop\Work\Uni\Databases Assessment\database")
    print(sql)