
# Task 1.
#### The goal of this task is to generate some random data, store it in Postgresql and than create a Python script for moving the data from Postgresql to [Amazon Redshift](https://aws.amazon.com/documentation/redshift/)

_____
###### To accomplish that task we need to complete four steps:
+ **a.** Create a Python script that generates some random data and stores it into a Postgresql table with 5 million random rows.
+ **b.** Create a python script or a shell script which dumps the data from the table ​apps in Postgresql to a CSV file with GZIP compression.
+ **c.** Create an account on [Amazon AWS](https://aws.amazon.com/) and implement a python script for uploading the file created in step b. to Amazon S3.
+ **d.** Create a Python script that loads the data from Amazon S3 to Redshift. (AWS provides free trial for both S3 and Redshift).
___

### Part a
_Create sql table acording to the following schema:_
###### Table name: 
- **apps**
###### Columns:
- **pk**: Primary key (integer)
- **id**: A unique identifier of the app on the app market (varchar(256))
- **title**: Title of the app (varchar(256))
- **description**: Description of the app (varchar(2000))
- **published_timestamp**: Timestamp when the app was published on the app market (TIMESTAMP)
- **last_update_timestamp**: Timestamp when the app was last updated on the app market (TIMESTAMP)

After installing [PostgreSQL](https://www.postgresql.org) we have default server with database.  
Credentials are:
- dbname __postgres__ 
- login __postgres__
- password __password__

To be able using psql tool via Terminal:
- install the package
- add PATH to the ~/.bash_profile (in my case echo 'export PATH="/Library/PostgreSQL/10/bin:$PATH"' >> ~/.bash_profile)

We can inspect our base with pgAdmin4 

We have **task1_sql.py** python scrip that create and add table into psql (I am using psycopg2 package)

```Python
#!/usr/bin/env python3
import sys
import psycopg2

# create connection using given arguments
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
    # All these arguments are given as default in shell script
    create_table()
    sys.argv[1] # database
    sys.argv[2] # username
    sys.argv[3] # password
```

_run PostgreSQL server with pgAdmin 4 tool or Terminal before using script_.  

Having both files in your folder **execute in bash** (cd to directory with files):  
___
### **`bash task1.sh`**  
___

*containing:*
```bash
#!/usr/bin/env bash

python task1_sql.py "${1:-postgres}" "${2:-postgres}" "${3:-password}";
echo "table apps has been created";
```

Table with specified parameters would be created!

Next - generating and inserting data to the created table **apps**  
> in the previous way with two files - Shell and python files.  
We could do it with one, python, but I use this approach in my daily practice.  
using **task1_2.py**

```Python
#!/usr/bin/env python3

import sys
import psycopg2
import random
import string
import datetime
import pandas as pd

# generating random text
def random_string(size=250, chars='string.ascii_lowercase' + 'string.digits' + ' '):
    yield ''.join(random.choice(chars) for x in range(random.randrange(5, size)))

# generating dates
def random_date(start, l):
    current = start
    while l >= 0:
        current = current + datetime.timedelta(minutes=random.randrange(1000000))
        yield current
        l-=1
        
# initializing date when app was created
def start_date():
    return datetime.datetime(
        random.randrange(2013, 2016),
        random.randrange(1, 13),
        random.randrange(1, 28),
        random.randrange(0, 24),
        random.randrange(0, 60)
    )

# generating the whole row
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

# generating dates to fill update column in apps
def date_upd(x):
    return next(random_date(datetime.datetime.strptime(x, "%Y-%m-%d %H:%M"), 10)).strftime("%Y-%m-%d %H:%M")

# first created rows. These apps would be living in our table.
d = [next(first_app_row()) for _ in range(1000)]

# rows of updated apps. Here present argument that defines number of added rows. By default after executing there will be 5_000_000 rows. 
du = pd.DataFrame([random.choice(d) for _ in range(int(sys.argv[4]))])

d = pd.DataFrame(d)

# fill update column
du[4] = du[4].apply(date_upd)

# concat tables
df_total = d.append(du, ignore_index=True)

df_total.sort_values(by=[4], inplace=True)

df_total.reset_index(drop=True, inplace=True)

df_total.columns = ['id', 'title', 'description', 'published_timestamp', 'last_update_timestamp']

# These part adds our data to dbase

def create_conn(dbname=sys.argv[1], user=sys.argv[2], password=sys.argv[3]):
    conn = psycopg2.connect(database=dbname, user=user, password=password)
    return conn

def insert_apps(df):
    """ insert a new vendor into the apps table """
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
```

__Shell script that runs python task1_2.py file:__
> use optional parameters to change database, user, password and number of random rows respectively.

**execute in Bash:**
___
### `bash task1_2.sh`
___


*containing*
```Bash
#!/usr/bin/env bash

echo "script generating and inserting data into table apps";
python task1_2.py "${1:-postgres}" "${2:-postgres}" "${3:-password}" "${4:-4999000}";
echo "done";
```

Check the progress with the query tool via pgAdmin
```SQL
SELECT COUNT(*) 
FROM apps;
```
___
```SQL
SELECT * 
FROM apps
LIMIT 100;
```

### Part b

*I choose to use shell scripts as they are convenient for next type of tasks*

To dump gzip compressed table **apps** from psql use **task1_3.sh** (prompt password **password**)  
### **`bash task1_3.sh`**

containing:  
```bash
#!/usr/bin/env bash

psql -U postgres -d postgres -c "COPY apps TO STDOUT WITH CSV DELIMITER','" | gzip > dat.csv.gz
```

### Part c

[Amazon AWS](https://s3.console.aws.amazon.com/s3/buckets/tasktest/?region=us-east-1&tab=overview, 'here I've created my bucket')  
To deal with our goal we need to set up a bunch of things.  
First we register our account specifying all needed data. 

Then, as process was not quite intuitive I'll give all the things we need to set to set up to uploading data to **s3** bucket and then migrate them into **Redshift** base.  
So here we merge c & d parts.

Let's begin.  

- Go to Identity and Access Management. Create individual IAM user (mine `testuser`).  
In that section we need to generate Access keys. Get the csv file with credentials. 
- Call `pip install awscli`. After installation,  
- Call and fill the prompt:  
```bash
aws configure
AWS Access Key ID [****************JWTA]: 
AWS Secret Access Key [****************LlG0]: 
Default region name [us-east-1]: 
Default output format [CSV]: 
```

I created **tasktest** bucket. We need to specify its Policy.  
Go >> tasktest >> Permissions >> Bucket Policy.  
Here we need ot generate and then save that policy in JSON format:
```JSON
{
    "Version": "2012-10-17",
    "Id": "Policy1531727353557",
    "Statement": [
        {
            "Sid": "Stmt1531727352105",
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::400119671200:role/redshiftfull"
            },
            "Action": "s3:*",
            "Resource": "arn:aws:s3:::tasktest"
        }
    ]
}
```

- You ready to upload data to s3 bucket. Call  
```bash
aws s3 cp dat.csv.gz s3://tasktest/
```
check bucket. data is there.

### Part d

- Create [IAM Role](https://console.aws.amazon.com/iam/home?region=us-east-1#/roles). (mine `redshiftfull`) (IAM section).  
Role allows Redshift clusters to call AWS services on your behalf.
- Attach policies (I've used predefined: AmazonDMSRedshiftS3Role, AmazonS3FullAccess, AmazonRedshiftFullAccess)
- Create and launch cluster on [Amazon Redshift](https://console.aws.amazon.com/redshift/home?region=us-east-1#) (mine `redshift89`). 
- Add to the cluster defined earler Role. That it can get data from s3 bucket. Also there you can see ARN that would be needed for authorisation. (mine `arn:aws:iam::400119671200:role/redshiftfull`)
- Security Group Rules - *there was my stone in the shoe* - have to be sure that your database publicly accessible. Find [here](https://console.aws.amazon.com/redshift/home?region=us-east-1#subnet-groups:cluster=).  

Time to connect to our Redshift base by calling:
```bash
psql -h redshift89.cvbpycanmszl.us-east-1.redshift.amazonaws.com -U redshift -d test_redshift -p 5439
```
also by: 
### **`bash task1_4.sh` ** 


+ here we use our Endpoint - `-h redshift89.cvbpycanmszl.us-east-1.redshift.amazonaws.com` (we can find in cluster description).
+ `-U redshift` - Cluster Database Properties >> Master Username.
+ `-d test_redshift` - Database Name.
+ `-p 5439` - Port.  
Providing password to the prompt and we at the place.

#### Preparing table to get data from s3 bucket

via bash executing sql query
```sql
CREATE TABLE apps
(
    pk integer,
    id varchar(255),
    title varchar(255),
    description varchar(2000),
    published_timestamp timestamp,
    last_update_timestamp timestamp

);
```
can check that table was created by command `\dt`  
test_redshift-# `\dt`  
and get - List of relations:  

 schema | name | type  |  owner   
--------|------|-------|----------  
public | apps | table | redshift

At last notheng stop us end this task by copying our table **apps** from **s3 bucket** to the **Redshift** database.

Call
```sql
copy apps from 's3://tasktest/dat.csv.gz' credentials 'aws_iam_role=arn:aws:iam::400119671200:role/redshiftfull' region 'us-east-1' DELIMITER ',' GZIP;
```

Here we use:  
- `s3://tasktest/dat.csv.gz` - s3 bucket path to the needed file.
- `aws_iam_role=arn:aws:iam::400119671200:role/redshiftfull` - Role we've created previously.  
 Load into table 'apps' completed, 5000000 record(s) loaded successfully.  
 Yey!
