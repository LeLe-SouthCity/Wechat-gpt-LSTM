import mysql.connector
from mysql.connector import Error

class MY_SQL_API:
    """
    
    # 使用示例
    db = MY_SQL_API('localhost', 'your_username', 'your_password', 'your_database')

    # 插入数据
    insert_query = "INSERT INTO your_table (column1, column2) VALUES (%s, %s)"
    db.insert(insert_query, ('value1', 'value2'))

    # 查询数据
    select_query = "SELECT * FROM your_table"
    results = db.select(select_query)
    for result in results:
        print(result)

    # 更新数据
    update_query = "UPDATE your_table SET column1 = %s WHERE column2 = %s"
    db.update(update_query, ('new_value', 'value2'))

    # 删除数据
    delete_query = "DELETE FROM your_table WHERE column2 = %s"
    db.delete(delete_query, ('value2',))
    
    """
    def __init__(self, host, user, password, database=None):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.connect()
            
    def connect(self):
        """
        数据库连接
        """
        try:
            if self.database:
                self.connection = mysql.connector.connect(
                    host=self.host,
                    user=self.user,
                    password=self.password,
                    database=self.database
                )
            else:
                self.connection = mysql.connector.connect(
                    host=self.host,
                    user=self.user,
                    password=self.password
                )
        except Error as e:
            print(f"Error: '{e}'")

    def create_database(self, database_name):
        """
        数据库创建
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute(f"CREATE DATABASE {database_name}")
            print(f"Database `{database_name}` created successfully")
        except Error as e:
            print(f"Error: '{e}'")
        finally:
            cursor.close()
            
    def execute_query(self, query, params=None):
        """
        数据库 —— 执行任何传递给它的 SQL 查询。这个方法可以用来创建、读取、更新或删除数据库中的数据。方法的参数说明如下：
        """
        cursor = self.connection.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self.connection.commit()
            print(f""" Query successful""")
        except Error as e:
            print(f"Error: '{e}'")
        finally:
            cursor.close()

    def insert(self, query, val):
        """向数据库表中插入一条新记录。"""
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, val)
            self.connection.commit()
            print("Record inserted successfully")
        except Error as e:
            print(f"Error: '{e}'")

    def select(self, query):
        """从数据库表中检索数据"""
        
        cursor = self.connection.cursor()
        try:
            cursor.execute(query)
            results = cursor.fetchall()
            return results
        except Error as e:
            print(f"Error: '{e}'")
            return None

    def update(self, query, val):
        """更新数据库表中的现有记录。"""
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, val)
            self.connection.commit()
            print("Record updated successfully")
        except Error as e:
            print(f"Error: '{e}'")

    def delete(self, query, val):
        """从数据库表中删除记录。"""
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, val)
            self.connection.commit()
            print("Record deleted successfully")
        except Error as e:
            print(f"Error: '{e}'")

