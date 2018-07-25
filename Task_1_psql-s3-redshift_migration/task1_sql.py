#!/usr/bin/env python3

import sys
import psycopg2


def create_conn(dbname, user, password):
    conn = psycopg2.connect(database=dbname, user=user, password=password)
    return conn

def create_table():
    '''create tables in the PostgreSQL database'''
    command = (
'''
CREATE TABLE apps
(
pk serial PRIMARY KEY,
id VARCHAR(255) NOT NULL, -- A unique identifier of the app on the app market
title VARCHAR(255) NOT NULL, -- Title of the app
description VARCHAR(2000) NOT NULL, -- Description of the app
published_timestamp TIMESTAMP NOT NULL DEFAULT NOW(), -- Timestamp when the app was published on the app market
last_update_timestamp TIMESTAMP NOT NULL DEFAULT NOW() -- Timestamp when the app was last updated on the app market
)
'''
    )
    conn = None
    try:

        conn = create_conn(dbname=sys.argv[1],
                           user=sys.argv[2],
                           password=sys.argv[3])
        
        # connect to the PostgreSQL server
        cur = conn.cursor()
        
        # create table one by one
        cur.execute(command)
        
        # close communication with the PostgreSQL database server
        cur.close()
        
        # commit the changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

if __name__ == '__main__':
    create_table()
    sys.argv[1]
    sys.argv[2]
    sys.argv[3]

