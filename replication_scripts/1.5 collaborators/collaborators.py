import os
from dotenv import load_dotenv
load_dotenv()

import requests
import json
import psycopg2
from github import Github, RateLimitExceededException

class Database():

    def __init__(self, host,database,user,password):
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

    def getRepositoriesWithPullRequests(self):
        query = """ select distinct owner_repo 
                    from "pullRequests" 
                    where (owner_repo) not in (select owner_repo from collaborators)
                """

        db = self.getConnection()
    
        cursor = db.cursor()

        cursor.execute(query)

        pullRequests = []

        for (owner_repo) in cursor: 
            pullRequests.append((owner_repo))

        return pullRequests        

    def save(self,data):
        sql = """INSERT INTO collaborators (owner_repo, id, login, type, site_admin, contributions) 
                 VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (owner_repo, id) DO NOTHING"""

        db = self.getConnection()

        cursor = db.cursor()    

        cursor.execute(sql,data)
        db.commit()   


class ReadChangedFiles():

    def __init__(self, repo,page):
        self._repo = repo
        self._page = page

    def requisicao_api(self):
        resposta = requests.get(
            f'https://api.github.com/repos/{self._repo}/contributors?per_page=100&anon=true&page={self._page}', headers=headers)
        if resposta.status_code == 200:
            return resposta.json()
        else:
            return resposta.status_code

    def getContributors(self):
        contributors = []
        dados_api = self.requisicao_api()
        if type(dados_api) is not int:
            for i in range(len(dados_api)):
                id = -1
                if ("id" in dados_api[i]):
                    id = dados_api[i]['id']
                login = ""
                if ("login" in dados_api[i]):
                    login = dados_api[i]['login']                    
                site_admin = False
                if ("site_admin" in dados_api[i]):
                    site_admin = dados_api[i]['site_admin']
                # Convert boolean to 0/1 for SMALLINT column
                site_admin_int = 1 if site_admin else 0

                contributors.append((self._repo,
                                     id,
                                     login,
                                     dados_api[i]['type'],
                                     site_admin_int,
                                     dados_api[i]['contributions']))
        else:
            print(dados_api)
            return None
        return contributors   

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
repositoriesWithPullRequests = database.getRepositoriesWithPullRequests()

count = 0     

for (repository) in repositoriesWithPullRequests:
     ownerRepo = repository[0]

     page = 1     
     contributorsSize = 100 
     while (contributorsSize == 100):        
        readChangedFiles = ReadChangedFiles(ownerRepo,page)  
        contributors = readChangedFiles.getContributors()   
        contributorsSize = len(contributors)
        for (contributor) in contributors:
            database.save(contributor)
        page += 1        
