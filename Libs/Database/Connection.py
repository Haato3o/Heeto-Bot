'''
    Library used by Heeto bot to access its PostgreSQL database
    Author: Haato
'''

import psycopg2 as PostgreSQL
import os
from dotenv import load_dotenv
from Core.Logger import Logger

class Database():
    def __init__(self, username: str, password: str, host: str, port: str, db_name: str):
        '''
            Creates a PostgreSQL database connection
            :param username: Database username
            :param password: Database password
            :param host: Database host
            :param port: Database port
            :param db_name: Database name
        '''
        # Database info
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.db_name = db_name
        # Connection
        self.Connection = None
        self.Cursor = None

    def isConnected(self):
        if self.Connection:
            return True
        else:
            Logger.Log(f"You must connect to the database first!")
            return False

    def DeleteFromTable(self, tableName: str, comp: str):
        query = f'''
            DELETE FROM {tableName} WHERE {comp};
        '''
        if self.isConnected():
            try:
                self.Cursor.execute(query)
                self.Connection.commit()
                return True
            except Exception as err:
                Logger.Log(err, Logger.ERROR)
                self.Cursor.execute("rollback;")
                return False

    def GetFromTable(self, tableName: str, comp: str):
        query = f'''
            SELECT * FROM {tableName} WHERE {comp};
        '''
        if self.isConnected():
            try:
                self.Cursor.execute(query)
                return self.Cursor.fetchall()
            except Exception as err:
                Logger.Log(err, Logger.ERROR)
                self.Cursor.execute("rollback;")

    def CommitCommand(self, command: str):
        '''
            Executes command
            :param command: PostgreSQL command to execute and commit
            :return: True if the command was executed, False if not
        '''
        if self.isConnected():
            try:
                self.Cursor.execute(command)
                self.Connection.commit()
                return True
            except Exception as err:
                Logger.Log(err, Logger.ERROR)
                self.Cursor.execute("rollback;")
                return False

    def AddToTable(self, tableName: str, **kwargs):
        '''
            Adds values to a table
            :param tableName: Table name
            :param kwargs: Table column values
            :return: True if values were added, false if not
        '''
        query = f'''
            INSERT INTO {tableName} VALUES {tuple(kwargs.values())};
        '''.replace("'null'", "null")
        if self.isConnected():
            try:
                self.Cursor.execute(query)
                self.Connection.commit()
                Logger.Log(f"Added {tuple(kwargs.values())} to {tableName}")
                return True
            except Exception as err:
                Logger.Log(err, Logger.ERROR)
                self.Cursor.execute("rollback;")
                return False

    def DeleteTable(self, tableName):
        '''
            Deletes table
            :param tableName: Table to delete
            :return: True if table was deleted, false if not
        '''
        query = f'''
            DROP TABLE {tableName};
        '''
        if self.isConnected():
            try:
                self.Cursor.execute(query)
                self.Connection.commit()
                Logger.Log(f"Deleted table: {tableName}")
                return True
            except Exception as err:
                Logger.Log(err, Logger.ERROR)
                self.Cursor.execute("rollback;")
                return False

    def CreateNewTable(self, tableName: str, values: str):
        '''
            Create new table
            :param tableName: Table name
            :param values: String with the values and its types
            :return: True if table was created, false if it failed
        '''
        query = f'''
            CREATE TABLE {tableName} {values};
        '''
        if self.isConnected():
            try:
                self.Cursor.execute(query)
                self.Connection.commit()
                Logger.Log(f"Created table {tableName} with values {values}")
                return True
            except Exception as err:
                Logger.Log(err, Logger.ERROR)
                self.Cursor.execute("rollback;")
                return False

    def connect(self):
        '''
            Connects to PostgreSQL database
        '''
        if self.Connection == None:
            self.Connection = PostgreSQL.connect(
                user = self.username,
                password = self.password,
                host = self.host,
                port = self.port,
                database = self.db_name
            )
            self.Cursor = self.Connection.cursor()
            Logger.Log(f"Connected to database: {self.db_name}")
    
    def disconnect(self):
        '''
            Disconnects from PostgreSQL database
        '''
        if self.Connection:
            self.Cursor.close()
            self.Connection.close()
            Logger.Log("Connection to database closed!")
            self.Connection = None