from time import sleep
import praw 
import praw
from praw.exceptions import PRAWException
import pandas as pd
from prawcore import exceptions
import datetime
import os
import time
jeadlines=set()
import requests as rq
from elasticsearch import Elasticsearch

es_local = Elasticsearch()
#cloud elasticsearch credentials
es_cloud = Elasticsearch(
    
)

#Search id on elasticsearch
def Searchid(ProjectName,id):
    res = es_local.search(index=ProjectName, query= {
         "match": {
              "id.keyword": id
        }
        })
    if(len(res["hits"]["hits"])==0):
        return False
    else:
        return True  
#Search id on elasticsearch in cloud
def Searchid_cloud(ProjectName,id):
    res = es_cloud.search(index=ProjectName, query= {
         "match": {
              "id.keyword": id
    }
    })
    if(len(res["hits"]["hits"])==0):
        return False
    else:
        return True  
def Getkeywords(ProjectName):
        txt = open('W:')
        lines= txt.readlines()
        return lines  

while(True):
    dir = 'w:/'
    with os.scandir(dir) as files:
        for file in files:
            print('------------------------------------------------------------')
            print('-------------------WEB SCRAPING PROCESS-------------------')
            if(file.is_dir()):   
                keywords=Getkeywords(file.name)
                for i in range(len(keywords)):
                    key=keywords[i].rstrip()
                    print('--------------------keyword: '+key+' ------------------------')
                    #credentials to access the reddit API
                    reddit = praw.Reddit(client_id='ABl5wA7g_L_3vbzAZYDQJw', client_secret='KNJEEocMxkU77emium_Dg4uaK55gaA', user_agent='2Secure')
                    try:  
                        submission=reddit.subreddit(key).new(limit=50)
                        for subm in submission:
                            print(subm.id)
                            created = datetime.datetime.fromtimestamp(subm.created)
                            doc={
                                    'id' : subm.id,
                                    'urlpost' : subm.url,
                                    'project' : file.name,
                                    'author': subm.author,
                                    'engine' : 'reddit',
                                    'addedDate' : datetime.now(),
                                    'updatedDate': created,
                                    'title' : subm.title
                                            }
                            if(Searchid(file.name,subm.id)==False):
                                res_local = es_local.index(index=file.name, id=subm.id, document=doc)
                                print('New Post successfully scraped... '  +subm.id,)    
                                print('The API reddit is inserting records for the site: '+file.name + ' Time '+str(datetime.now())+' Result: '+res_local['result'])
                            if(Searchid_cloud(file.name,subm.id)==False):   
                                res_cloud = es_cloud.index(index=file.name, id=subm.id , document=doc)
                                print('New Post successfully scraped... '  +subm.id)    
                                print('The API reddit is inserting records for the site in cloud: '+file.name + ' Time '+str(datetime.now())+' Result: '+res_cloud['result']) 
                    except exceptions.ResponseException as e:
                        print("The engine didn't found results for the keyword: "+key) 
    print("-------------------------------------\n")
    print("data successfully saved ")   
    print("--------------------------------")       
    print("|     See you next time :)     |")
    print("--------------------------------")
    time.sleep(28800)