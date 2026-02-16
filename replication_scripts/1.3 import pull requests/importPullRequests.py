#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import random
from dotenv import load_dotenv
load_dotenv()

from github import Github, RateLimitExceededException

REPLICATION_REPO_COUNT = 5
random.seed(43)
import csv, json, os.path, pandas as pd, requests, time
from datetime import datetime
import psycopg2

def getConnection():
    db = psycopg2.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        dbname=os.environ.get("DB_NAME", "gh_graphql_api"),
        user=os.environ.get("DB_USER", "postgres"),
        password=os.environ.get("DB_PASSWORD", "")
    )
    return db

def run_query(query): 
    request = requests.post('https://api.github.com/graphql', json={'query': query}, headers=headers)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))       

def query_composer(keyword,repo):
    query = """query { 
                  search(query: " """+ keyword + ' repo:' + repo + """ is:pr is:merged review:approved", 
                    type: ISSUE, 
                        first: 100) {  
                            issueCount 
                            edges { 
                                node {  
                                    ... on PullRequest {  
                    			        number
                                        url  
                                        title 
                                        body 
                    	                mergedAt
                                        mergedBy {
                                            login
                                        }
                                        author {
                                            login
                                        }
                                        pullRequestcommits: 
                                            comments(last:100) {                       
                                                edges { 
                                                    node { 
                                                        createdAt
                                                        bodyText 
                                                        author {
                               			                    login
                          	    		                }
                                                    } 
                                                } 
                                            } 
                                            commits(last: 100) { 
                                                totalCount 
                                                edges { 
                                                    node { 
                                                        commit {                                                 
                                                            author {                                                  
                                                                user {
                                                                    login
                                                                }                                                  
                                                            }
                                                            commitUrl 
                                                            message 
                                                        } 
                                                    }    
                                                } 
                                            } 
                                    } 
                                } 
                            }          
                        } 
                }"""

    return query   

def getRepositories():

    query = """ select owner_repo 
                from repositories 
                where scorebased_org = 1 
                  and randomforest_org = 1 
                  and scorebased_utl = 1 
                  and randomforest_utl = 1
                  and watchers is not null 
                  and "isFork" = 0 
                  and stars > 100 
                  and "pullRequests" > 0
 """

    db = getConnection()
    cursor = db.cursor()  

    cursor.execute(query)

    repositories = []

    for (url) in cursor: 
        repositories.append(url[0])

    return repositories    

def getReadabilityPullRequestsRepositories():       
    count = 0    
    repositories = getRepositories()
    # Limit to 5 repos for replication
    if len(repositories) > REPLICATION_REPO_COUNT:
        repositories = random.sample(repositories, REPLICATION_REPO_COUNT)
    print(f"Processing {len(repositories)} repos (replication limit: {REPLICATION_REPO_COUNT})")

    for (repository) in repositories:    
        data = getReadabilityPullRequests(repository)
        count += 1
        print(repository+" count "+str(count)+" of "+str(len(repositories)))
        
    return data            

def insertRepositorySearch(owner_repo,keyword,number_results,error):
    sqlPR = """INSERT INTO repository_search_log (owner_repo, keyword, number_results, error) 
               VALUES (%s, %s, %s, %s) ON CONFLICT (owner_repo, keyword) DO NOTHING"""

    db = getConnection()
    cursor = db.cursor()    
    cursor.execute(sqlPR,(owner_repo,keyword,number_results,error))

    db.commit()

    
def getReadabilityPullRequests(repository): 
    keywords = ('readability','readable','understandability','understandable','clarity','legibility','easier to read','comprehensible')

    sqlPR = """INSERT INTO "pullRequests" (owner_repo, pr_number, url, title, body, "mergedAt", "mergedBy", author) 
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (owner_repo, pr_number) DO NOTHING"""

    sqlComments = """INSERT INTO comments (owner_repo, pr_number, "createdAt", "bodyText", author) 
                     VALUES (%s, %s, %s, %s, %s) ON CONFLICT (owner_repo, pr_number, "createdAt") DO NOTHING"""

    sqlCommits = """INSERT INTO commits (owner_repo, pr_number, author, url, message) 
                    VALUES (%s, %s, %s, %s, %s) ON CONFLICT (owner_repo, pr_number, url) DO NOTHING"""

    for (keyword) in keywords:
        try:            
            result = run_query(query_composer(keyword,repository))
            issueCount = result["data"]["search"]["issueCount"]
            insertRepositorySearch(repository,keyword,issueCount,"")
            for pr in result["data"]["search"]["edges"]:   
                
                dataPR = ()
                dataComments = []
                dataCommits = []

                pr_number = pr["node"]["number"]
                pr_url = pr["node"]["url"]
                pr_title = pr["node"]["title"]
                pr_body = pr["node"]["body"]
                pr_mergedAt = datetime.strptime( pr["node"]["mergedAt"], '%Y-%m-%dT%H:%M:%SZ')
                pr_mergedBy = pr["node"]["mergedBy"]["login"]
                pr_author = pr["node"]["author"]["login"]

                dataPR = (repository,pr_number,pr_url,pr_title,pr_body,pr_mergedAt,pr_mergedBy,pr_author)

                for comments in pr["node"]["pullRequestcommits"]["edges"]:
                    comment_createdAt = datetime.strptime(comments["node"]["createdAt"], '%Y-%m-%dT%H:%M:%SZ')
                    comment_bodyText = comments["node"]["bodyText"]
                    comment_author = comments["node"]["author"]["login"]

                    dataComments.append((repository,pr_number,comment_createdAt,comment_bodyText,comment_author))

                for commits in pr["node"]["commits"]["edges"]:
                    commit_author = ""
                    if commits["node"]["commit"]["author"]["user"] is not None:
                        commit_author = commits["node"]["commit"]["author"]["user"]["login"]
                    commit_url = commits["node"]["commit"]["commitUrl"]
                    commit_message = commits["node"]["commit"]["message"]

                    dataCommits.append((repository,pr_number,commit_author,commit_url,commit_message))

                db = getConnection()
                cursor = db.cursor()    
                cursor.execute(sqlPR,dataPR)
                cursor.executemany(sqlComments,dataComments)
                cursor.executemany(sqlCommits,dataCommits)
        
                db.commit()
            
        except Exception as e:
            insertRepositorySearch(repository,keyword,0,str(e))

    
################# STEP 1
# REST API v3 / GraphQL API v4 - using access token from .env
#################
access_token = os.environ.get("GITHUB_ACCESS_TOKEN", "")
headers = {'Authorization': 'Bearer '+ access_token}


data = getReadabilityPullRequestsRepositories()
