import os
from dotenv import load_dotenv
load_dotenv()

import requests
import json
import psycopg2
from github import Github, RateLimitExceededException

class Database():

    def __init__(self, host, database, user, password):
        self._host = host
        self._database = database
        self._user = user
        self._password = password

    def getConnection(self):
        db = psycopg2.connect(
            host=self._host,
            dbname=self._database,
            user=self._user,
            password=self._password
        )
        return db

    def getPullRequests(self):
        query = """ select owner_repo, pr_number 
                    from "pullRequests" 
                    where (owner_repo, pr_number) not in (select owner_repo, pr_number from "changedFiles")
                """

        db = self.getConnection()
    
        cursor = db.cursor()

        cursor.execute(query)

        pullRequests = []

        for (owner_repo,pr_number) in cursor: 
            pullRequests.append((owner_repo,pr_number))

        return pullRequests        

    def save(self,ownerRepo,pullRequestNumber,fileName,typeChange):
        sql = """INSERT INTO "changedFiles" (owner_repo, pr_number, "fileName", "typeChange") 
                 VALUES (%s, %s, %s, %s) ON CONFLICT (owner_repo, pr_number, "fileName") DO NOTHING"""

        db = self.getConnection()

        cursor = db.cursor()    

        cursor.execute(sql,(ownerRepo,pullRequestNumber,fileName,typeChange))
        db.commit()   


class ReadChangedFiles():

    def __init__(self, repo,pullNumber,page):
        self._repo = repo
        self._pullNumber = pullNumber
        self._page = page

    def requisicao_api(self):
        resposta = requests.get(
            f'https://api.github.com/repos/{self._repo}/pulls/{self._pullNumber}/files?per_page=100&page={self._page}', headers=headers)
        if resposta.status_code == 200:
            return resposta.json()
        else:
            return resposta.status_code

    def getFilesChanged(self):
        changedFiles = []
        dados_api = self.requisicao_api()
        if type(dados_api) is not int:
            for i in range(len(dados_api)):
                changedFiles.append((dados_api[i]['filename'],dados_api[i]['status']))
        else:
            print(dados_api)
        return changedFiles   

################# STEP 1
# REST API v3 / GraphQL API v4 - using access token from .env
#################
access_token = os.environ.get("GITHUB_ACCESS_TOKEN", "")
headers = {'Authorization': 'Bearer '+ access_token}                

database = Database(
    os.environ.get("DB_HOST", "localhost"),
    os.environ.get("DB_NAME", "gh_graphql_api"),
    os.environ.get("DB_USER", "postgres"),
    os.environ.get("DB_PASSWORD", "")
)
pullRequests = database.getPullRequests()

count = 0     

for (pullRequest) in pullRequests:
     ownerRepo = pullRequest[0]
     pullRequestNumber = pullRequest[1]

     page = 1     
     contributorsSize = 100 
     while (contributorsSize == 100): 
        readChangedFiles = ReadChangedFiles(ownerRepo,pullRequestNumber,page)     
        changedFiles = readChangedFiles.getFilesChanged()

        contributorsSize = len(changedFiles)

        for (changedFile) in changedFiles:        
            fileName = changedFile[0]
            typeChange = changedFile[1]
            database.save(ownerRepo,pullRequestNumber,fileName,typeChange)

        page += 1     

     count += 1
     if (count % 100 == 0):
        print("Count "+str(count))

print(f"Done. Processed {count} PRs.")