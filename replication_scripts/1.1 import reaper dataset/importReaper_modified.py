#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from dotenv import load_dotenv
load_dotenv()

from datetime import datetime
import csv, os.path, pandas as pd, requests, time
import psycopg2


def getConnection():
    db = psycopg2.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        dbname=os.environ.get("DB_NAME", "gh_graphql_api"),
        user=os.environ.get("DB_USER", "postgres"),
        password=os.environ.get("DB_PASSWORD", "")
    )
    return db

def sanitize_value(val):
    """Convert 'None', 'null', empty string to Python None for DB NULL."""
    if val is None or val == '' or str(val).strip().lower() in ('none', 'null'):
        return None
    return val

def saveRow(row,count):
    # Sanitize numeric columns: indices 2-15 (architecture through randomforest_utl)
    # "None" in CSV must become Python None for PostgreSQL NULL
    sanitized = list(row)
    for i in range(2, min(16, len(sanitized))):
        sanitized[i] = sanitize_value(sanitized[i])

    sql = """ INSERT INTO repositories 
                  (owner_repo, 
                   language,
                   architecture,
                   community,
                   continuous_integration,
                   documentation,
                   history,
                   issues,
                   license,
                   size,
                   unit_test,
                   stars,
                   scorebased_org,
                   randomforest_org,
                   scorebased_utl,
                   randomforest_utl
                   ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                   ON CONFLICT (owner_repo) DO NOTHING
    """
    
    db = getConnection()
    cursor = db.cursor()    

    cursor.execute(sql, sanitized)
    db.commit()   
    
    if count % 10000 == 0:
        print(count, "was inserted.")     
        
def readCsv(file):

    count = 0

    with open(file, 'r') as file:
        data = csv.reader(file)
        for row in data:
            if row[3].isnumeric():
                saveRow(row,count)   
                count += 1



file = "./reaper-dataset.csv"

readCsv(file)
