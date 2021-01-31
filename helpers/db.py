from redis import Redis
from config import CLICKHOUSE_DATABASE
import pymysql
from flask import g, current_app
from clickhouse_driver import Client
import redis

"""
Returns the connection to a database if one already exists, or creates a new connection and 
returns the new connection
"""
def get_database_connection(cursorclass=pymysql.cursors.DictCursor):
    if 'db_connection' not in g:
        DATABASE = current_app.config["DATABASE"]
        g.db_connection = pymysql.connect(host=DATABASE["HOST"],
                             user=DATABASE["USER"],
                             password=DATABASE["PASSWORD"],
                             db=DATABASE["NAME"],
                             charset='utf8mb4',
                             cursorclass=cursorclass)

    return g.db_connection

"""
Closes the connection created to the database.
This has to be registered with `Flask.teardown_appcontext`
Refer: https://flask.palletsprojects.com/en/1.1.x/api/#flask.Flask.teardown_appcontext
"""
def close_database_connection(error):
    db_connection = g.pop('db_connection', None)
    if db_connection is not None:
        db_connection.close()

def get_redis_connection():
    if 'db_redis' not in g:
        client = Redis()
        g.db_redis = client
    return g.db_redis

def get_clickhouse_client():
    if 'db_clickhouse_client' not in g:
        client = Client(host=CLICKHOUSE_DATABASE["HOST"],
                             user=CLICKHOUSE_DATABASE["USER"],
                             password=CLICKHOUSE_DATABASE["PASSWORD"],
                             database=CLICKHOUSE_DATABASE["DATABASE_NAME"],)
        g.db_clickhouse_client = client
    return g.db_clickhouse_client

def get_user(username, with_password=False):
    db_conn = get_database_connection()
    with db_conn.cursor() as cursor:
        sql = 'SELECT * FROM `user` WHERE `username`=%s'
        cursor.execute(sql, (username, ))
        result = cursor.fetchone()
        if result and not with_password:
            result.pop("password")
        return result
