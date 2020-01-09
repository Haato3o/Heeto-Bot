'''
    Library used by Heeto bot to access its PostgreSQL database
    Author: Haato
'''

import psycopg2 as PostgreSQL
import os
from dotenv import load_dotenv
from Core.Logger import Logger

class Database():
    MAX_MONEY = 92233720368547758.06
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

    def isConnected(self) -> bool:
        '''
            Returns status of current connection
        '''
        if self.Connection:
            return True
        else:
            Logger.Log(f"You must connect to the database first!")
            return False

    def DeleteFromTable(self, tableName: str, comp: str):
        '''
            Deletes element from an existing table
            :param tableName: Table name
            :param comp: Comparision to be made

            e.g:
                # Deletes all entries where ID is 123
                DeleteFromTable("Users", "ID = 123")
        '''
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
                self.Connection.rollback()
                return False

    def GetFromTable(self, tableName: str, comp: str):
        '''
            Returns all table entries that has the comp
            :param tableName: Table name
            :param comp: Comparision to be made

            e.g:
                # Gets all entries where ID is 123
                GetFromTable("Users", "ID = 123")
        '''

        query = f'''
            SELECT * FROM {tableName} WHERE {comp};
        '''
        if self.isConnected():
            try:
                self.Cursor.execute(query)
                return self.Cursor.fetchall()
            except Exception as err:
                Logger.Log(err, Logger.ERROR)
                self.Connection.rollback()

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
                self.Connection.rollback()
                return False

    def AddToTable(self, tableName: str, **kwargs):
        '''
            Adds values to a table
            :param tableName: Table name
            :param kwargs: Table column values
            :return: True if values were added, false if not
        '''
        queryBase = f"INSERT INTO {tableName} VALUES ({', '.join(['%s' for arg in range(len(kwargs))])})"
        if self.isConnected():
            try:
                self.Cursor.execute(queryBase, tuple(kwargs.values()))
                self.Connection.commit()
                Logger.Log(f"Added {tuple(kwargs.values())} to {tableName}")
                return True
            except Exception as err:
                Logger.Log(err, Logger.ERROR)
                self.Connection.rollback()
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
                self.Connection.rollback()
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
                self.Connection.rollback()
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

    # Heeto bot functions
    def GiveUserMoney(self, user_id: int, new_amount: float) -> bool:
        '''
            Updates the user's money
            :param user_id: User to update
            :param new_amount: New money amount

            e.g:
                # Updates user 123 to $500
                GiveUserMoney(123, 500.0)

            > Note: If new_amount is higher than MAX_AMOUNT, user's money will be updated to MAX_AMOUNT
        '''
        query = "UPDATE Users SET Credits = %s WHERE ID = %s;"
        if new_amount > Database.MAX_MONEY:
            new_amount = Database.MAX_MONEY
        try:
            self.Cursor.execute(query, (new_amount, user_id))
            self.Connection.commit()
            Logger.Log(f"Updated user {user_id} credits to {new_amount}")
            return True
        except Exception as err:
            Logger.Log(err)
            self.Cursor.execute('rollback;')
            return False
    
    def UpdateUserDescription(self, user_id: int, new_description: str) -> bool:
        query = "UPDATE Users SET description = %s WHERE ID = %s;"
        try:
            self.Cursor.execute(query, (new_description, user_id))
            self.Connection.commit()
            Logger.Log(f"Updated user {user_id} description.")
            return True
        except Exception as err:
            Logger.Log(err)
            self.Cursor.execute('rollback;')
            return False

    def UpdateUserColor(self, user_id: int, new_color: str) -> bool:
        query = "UPDATE Users SET cardColor = %s WHERE ID = %s;"
        try:
            self.Cursor.execute(query, (new_color, user_id))
            self.Connection.commit()
            Logger.Log(f"Updated user {user_id} color")
            return True
        except Exception as err:
            Logger.Log(err)
            self.Cursor.execute('rollback;')
            return False