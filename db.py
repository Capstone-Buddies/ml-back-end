import mysql.connector
import pandas as pd
import os

db = mysql.connector.connect(
    host=os.environ.get('MYSQL_DB_HOST'),
    user=os.environ.get('MYSQL_DB_USER'),
    passwd=os.environ.get('MYSQL_DB_PASSWORD'),
    database=os.environ.get('MYSQL_DB_NAME')
)


def runQuery(sql, columnDefinitions):
    cursor = db.cursor()
    cursor.execute(sql)

    results = cursor.fetchall()
    df = pd.DataFrame(results, columns=columnDefinitions)
    return df
