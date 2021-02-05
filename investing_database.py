import pandas as pd
import pymysql
import configparser
import sqlalchemy
from sqlalchemy import create_engine

def database_connect():
    config = configparser.ConfigParser()
    config.read("config.txt")
    user = config.get("configuration","user")
    password = config.get("configuration","password")
    server = config.get("configuration","server")
    sqlEngine = create_engine("mysql+pymysql://" + user + ":" + password + "@127.0.0.1/"+ server, pool_recycle=3600)
    db_connection = sqlEngine.connect()

    return db_connection

class Database:
    def __init__(self, db_connection):
        self.db_connection = db_connection

    def create_table_from_df(self, df, table_name, index_label):
        try:
            #this will fail if there is a new column
            df = df.to_sql(table_name, self.db_connection, if_exists='append', index=False) 
        except:
            data = pd.read_sql('SELECT * FROM '+table_name, self.db_connection)
            df2 = pd.concat([data,df])
            df2.to_sql(table_name, self.db_connection, if_exists = 'replace', index=False)
        return

        # print(df)
        # try:
        #     df = df.to_sql(table_name, self.db_connection, if_exists='append', dtype={None:sqlalchemy.types.VARCHAR(5), 'Dividend date':sqlalchemy.types.VARCHAR(20)})
        # except ValueError as vx:
        #     print(vx)
        # except Exception as ex:   
        #     print(ex)
        # else:
        #     print("Table %s created successfully."%table_name)

    def create_df_from_table(self, table_name):
        df = pd.read_sql('SELECT * FROM '+table_name, self.db_connection)
        return df