import sqlite3
from typing import List, Union


class SqlWrapper:
    def __init__(self, db_file: str = r".\database") -> None:
        self.db_file = db_file
        self.db = sqlite3.connect(self.db_file)
        self.cursor = self.db.cursor()
        
    def execute_query(self, sql_query: str) -> None:
        self.cursor.execute(sql_query)
        
    def select_query(self, table: str, columns: List[str], where: str = None, fetch_all: bool = True) -> Union[str, List[str]]:
        sql_query = f"SELECT {', '.join([c for c in columns])} FROM {table}"
        if where:
            sql_query += f" WHERE {where}"
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