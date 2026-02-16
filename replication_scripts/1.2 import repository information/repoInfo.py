#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from dotenv import load_dotenv
load_dotenv()

from github import Github, RateLimitExceededException
import csv, json, os.path, pandas as pd, requests, time
from datetime import datetime
import psycopg2

def run_query(query): 
    request = requests.post('https://api.github.com/graphql', json={'query': query}, headers=headers)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))       

def query_composer(owner,repo):
    query = """query {
                repositoryOwner (login:\"""" + owner + """\") {
                    repository(name:\"""" + repo + """\") {
                        isFork
                        forkCount
                        stargazerCount
                        pullRequests {
                            totalCount
                        }         
                        updatedAt
                        issues {
                            totalCount
                        }
                        watchers {
                            totalCount
                        }
                    }
                }
            }
"""

    return query   

def getConnection():
    db = psycopg2.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        dbname=os.environ.get("DB_NAME", "gh_graphql_api"),
        user=os.environ.get("DB_USER", "postgres"),
        password=os.environ.get("DB_PASSWORD", "")
    )
    return db     

def getRepositories():

    query = """ select owner_repo 
                from repositories 
                where scorebased_org = 1 
                  and randomforest_org = 1 
                  and scorebased_utl = 1 
                  and randomforest_utl = 1 
                  and language = 'Java' 
                  and watchers is null              
            """

    db = getConnection()
    
    cursor = db.cursor()

    cursor.execute(query)

    repositories = []

    for (repoInfo) in cursor: 
        repositories.append(repoInfo[0])

    return repositories    

def updateRepositories():  

    count = 0     
    
    repositories = getRepositories()

    for (repository) in repositories:    
        processRepository(repository)
        count += 1
        if (count % 100 == 0):
            print("Count "+str(count))
            time.sleep(5)

    
def processRepository(repository): 
    owner = repository.split("/")[0]
    repo = repository.split("/")[1]

    try:
        result = run_query(query_composer(owner, repo))

        # Handle null repository (deleted, renamed, or private)
        if result.get("data") is None:
            print("did not import " + repository + ": no data in response")
            return
        if result["data"].get("repositoryOwner") is None:
            print("did not import " + repository + ": repository owner not found")
            return
        repo_data = result["data"]["repositoryOwner"].get("repository")
        if repo_data is None:
            print("did not import " + repository + ": repository not found")
            return

        isFork = repo_data["isFork"]
        forkCount = repo_data["forkCount"]
        stargazerCount = repo_data["stargazerCount"]
        pullRequests = repo_data["pullRequests"]["totalCount"]
        updatedAt = datetime.strptime(repo_data["updatedAt"], '%Y-%m-%dT%H:%M:%SZ')
        issues = repo_data["issues"]["totalCount"]
        watchers = repo_data["watchers"]["totalCount"]

        # Convert boolean to 0/1 for SMALLINT column (importPullRequests filters by "isFork" = 0)
        isForkInt = 1 if isFork else 0

        sql = """ UPDATE repositories 
                    set stars = %s,
                        "isFork" = %s,
                        "pullRequests" = %s,
                        forks = %s,
                        "lastUpdate" = %s,
                        "numberIssues" = %s,
                        watchers = %s                 
                    where owner_repo = %s                
        """
        
        db = getConnection()
        cursor = db.cursor()    

        cursor.execute(sql, (stargazerCount, isForkInt, pullRequests, forkCount, updatedAt, issues, watchers, repository))
        db.commit()   

    except Exception as e:
        print("did not import", repository, ":", type(e).__name__, str(e))
    
################# STEP 1
# REST API v3 / GraphQL API v4 - using access token from .env
#################
access_token = os.environ.get("GITHUB_ACCESS_TOKEN", "")
headers = {'Authorization': 'Bearer '+ access_token}


updateRepositories()
