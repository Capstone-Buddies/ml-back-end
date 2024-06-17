import mysql.connector
import pandas as pd

db = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="rahasia",
    database="qflare"
)


def runQuery(sql, columnDefinitions):
    cursor = db.cursor()
    cursor.execute(sql)

    results = cursor.fetchall()
    df = pd.DataFrame(results, columns=columnDefinitions)
    return df
