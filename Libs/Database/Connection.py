'''
    Library used by Heeto bot to access it's PostgreSQL database
    Author: Haato
'''

import psycopg2 as PostgreSQL
import os
from dotenv import load_dotenv
from Core.Logger import Logger

class Database():
    def __init__(self, username: str, password: str, host: str, port: str, db_name: str):

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

    def AddToTable(self, tableName: str, values: tuple):
        '''
            Adds values to a table
            :param tableName: Table name
            :param values: Tuple with values to add
            :return: True if values were added, false if not
        '''
        query = f'''
            INSERT INTO {tableName} VALUES {values};
        '''
        if self.isConnected():
            try:
                self.Cursor.execute(query)
                self.Connection.commit()
                Logger.Log(f"Added {values} to {tableName}")
                return True
            except Exception as err:
                Logger.Log(err, Logger.ERROR)
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