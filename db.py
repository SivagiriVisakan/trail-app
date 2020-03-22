import pymysql
from flask import g, current_app

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
