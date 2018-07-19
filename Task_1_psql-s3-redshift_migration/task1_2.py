#!/usr/bin/env python3

import sys
import psycopg2
import random
import string
import datetime
import pandas as pd

def random_string(size=250, chars='string.ascii_lowercase' + 'string.digits' + ' '):
    yield ''.join(random.choice(chars) for x in range(random.randrange(5, size)))

def random_date(start, l):
    current = start
    while l >= 0:
        current = current + datetime.timedelta(minutes=random.randrange(1000000))
        yield current
        l-=1

def start_date():
    return datetime.datetime(
        random.randrange(2013, 2016),
        random.randrange(1, 13),
        random.randrange(1, 28),
        random.randrange(0, 24),
        random.randrange(0, 60)
    )

def first_app_row():
    description = next(random_string(2000))
    title = next(random_string(50, description))
    indentifier = next(random_string(20, title))
    st_date = start_date()
    
    yield(indentifier,
          title,
          description,
          st_date.strftime("%Y-%m-%d %H:%M"),
          st_date.strftime("%Y-%m-%d %H:%M")
         )

def date_upd(x):
    return next(random_date(datetime.datetime.strptime(x, "%Y-%m-%d %H:%M"), 10)).strftime("%Y-%m-%d %H:%M")

# first created rows
d = [next(first_app_row()) for _ in range(1000)]

# rows of updated apps
du = pd.DataFrame([random.choice(d) for _ in range(int(sys.argv[4]))])

d = pd.DataFrame(d)

du[4] = du[4].apply(date_upd)

df_total = d.append(du, ignore_index=True)

df_total.sort_values(by=[4], inplace=True)

df_total.reset_index(drop=True, inplace=True)

df_total.columns = ['id', 'title', 'description', 'published_timestamp', 'last_update_timestamp']

def create_conn(dbname=sys.argv[1], user=sys.argv[2], password=sys.argv[3]):
    conn = psycopg2.connect(database=dbname, user=user, password=password)
    return conn

def insert_apps(df):
    """ insert a new vendor into the vendors table """
    sql = """INSERT INTO apps(id, title, description, published_timestamp, last_update_timestamp)
             VALUES(%s, %s, %s, %s, %s);"""
    conn = None
    
    try:      
        conn = create_conn()
        # create a new cursor
        cur = conn.cursor()
        # execute the INSERT statement
        cur.executemany(sql, (df.values.tolist()))
        # commit the changes to the database
        conn.commit()
        # close communication with the database
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

if __name__ == '__main__':
    insert_apps(df_total)
    sys.argv[1]
    sys.argv[2]
    sys.argv[3]
    sys.argv[4]

