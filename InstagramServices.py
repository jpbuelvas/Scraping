from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import requests
from selenium.webdriver.support.ui import WebDriverWait
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import os
import hashlib
from elasticsearch import Elasticsearch
from datetime import datetime
es_local = Elasticsearch()
es_cloud = Elasticsearch(
    
es1 = Elasticsearch()
USERNAME = "example"
PASSWORD="1234"
options = Options()
#options.add_argument('--headless')
options.binary_location = r'C:/Program Files/Mozilla Firefox/firefox.exe'
print("Initializing ...")
#C:\Users\jbuel\Desktop\InstagramSelenium
ser= Service('C:/Users/Administrator/Documents/OSINTTool-master/instagramService/geckodriver.exe')
driver = webdriver.Firefox(service=ser,options=options)
driver.get("https://www.instagram.com")
def getProfile(link):
    user_profile=[]
    desc_text=username=full_name_user=followings_user=followers_user=numberlikes=poststime=profile_url=''
    try:
        # GET USER PROFILE LINK
        driver.get(link)
        profile_url = driver.find_element(By.XPATH,'//div[@class="e1e1d"]').find_element(By.XPATH,'.//a').get_attribute("href")
        time.sleep(3)
        poststime = driver.find_element(By.XPATH,'//div[@class="k_Q0X I0_K8  NnvRN"]').find_element(By.XPATH,'.//time').get_attribute("datetime")
        numberlikes = driver.find_element(By.XPATH,'//section[@class="EDfFK ygqzn"]').find_element(By.XPATH,'.//span').text
        desc_text = driver.find_element(By.XPATH,'//*[@id="react-root"]/section/main/div/div[1]/article/div/div[2]/div/div[2]/div[1]/ul/div/li/div/div/div[2]/span').text
    except:
        print("Dont locate element but its okay")
    
    # OPEN USER PROFILE VIA REQUEST
    if(profile_url):
        response = s.get(profile_url)
        content = response.text
        # EXTRACTING DATA USING REGEX FROM JSON
        # "graphql":{"user":{     -     ,"edge_felix_video_timeline"
        start = '"graphql":{"user":{'
        end = ',"edge_felix_video_timeline"'
        r = content[content.find(start)+len(start):content.rfind(end)]
        regex = []
        # followers:  ,"edge_followed_by":{"count":183401},"fbid":"17841410439120825"
        regex.append({'start':'"edge_followed_by":{"count":', 'end':'},"fbid"'})
        # followings:  ,"edge_follow":{"count":1},"follows_viewer"
        regex.append({'start':'"edge_follow":{"count":','end':'},"follows_viewer"'})
        # fullname:  "full_name":"Cats \u0026 Kitties","has_ar_effects":false
        regex.append({'start':'"full_name":"','end':'","has_ar_effects"'})
        # username:  ,"username":"meowflow","connected_fb_page"
        regex.append({'start':',"username":"','end':'","connected_fb_page"'})
        user_data = []
        # USE REGEX TO EXTRACT ALL THE REQUIRED FIELDS
        for i in regex:
            data = r[r.find(i['start'])+len(i['start']):r.rfind(i['end'])]
            user_data.append(data)
        followers_user = user_data[0]
        followings_user= user_data[1]
        full_name_user=user_data[2]
        username=user_data[3]
        user_profile=[profile_url,numberlikes,poststime,followers_user,followings_user,full_name_user,username,desc_text]
        return user_profile

def extractPost(hashTag):
    print("Search for {0}".format(hashTag))
    keyword = hashTag
    link_hashtag=f'https://www.instagram.com/explore/tags/{keyword}/'
    driver.get(link_hashtag)
    postLinks=[]
    numscrolled=0
    previous_height = driver.execute_script('return document.body.scrollHeight')
    print("Extracting posts ...")
    while True:
        p=driver.find_elements(By.XPATH,'//div[@class="v1Nh3 kIKUG  _bz0w"]')
        for e in p:
            if((e.find_element(By.XPATH,'.//a').get_attribute("href")) not in postLinks):
                postLinks.append(e.find_element(By.XPATH,'.//a').get_attribute("href"))
        driver.execute_script('window.scrollTo(0,document.body.scrollHeight);')
        time.sleep(9)
        new_height = driver.execute_script('return document.body.scrollHeight')
        if new_height==previous_height:
            break
        previous_height= new_height
        numscrolled += 1
        print("Scrolled",(numscrolled))
        time.sleep(7)
    return postLinks
#get keywords to search urls
def Getkeywords(ProjectName):
    txt = open('W:/OSINTTOOL/'+ProjectName+'/keywords_to_monitor.txt')
    lines= txt.readlines()
    return lines  
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

try:
    WebDriverWait(driver,5).until(EC.presence_of_all_elements_located((By.NAME,'username')))
except:
    print("Cant Load")

# LOGIN
try:
    print("Logging in as {0} ...".format(USERNAME))
    username = driver.find_element(By.XPATH,'//input[@aria-label="Teléfono, usuario o correo electrónico"]').send_keys(USERNAME)
    password = driver.find_element(By.XPATH,'//input[@aria-label="Contraseña"]').send_keys(PASSWORD)
    log_in = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"button[type='submit']"))).click()
    time.sleep(50)
    not_now = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Ahora no")]'))).click()
    not_now = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Ahora no")]'))).click()
except: 
    print("Cant Load")

# Saving auth cookies and header.
print("Saving session ...")
headers = {
"User-Agent":
    "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"
}
s = requests.session()
s.headers.update(headers)

for cookie in driver.get_cookies():
    c = {cookie['name']: cookie['value']}
    s.cookies.update(c)
    
while True:
    dir = 'W:/OSINTTOOL'
    with os.scandir(dir) as files:
        for file in files:
            if(file.is_dir()):  
                keywords=Getkeywords(file.name)
                for i in range(len(keywords)):
                    users_data=[]
                    print("\nPLEASE WAIT... THIS PROCESS WILL TAKE SOME TIME") 
                    key=keywords[i].rstrip()
                    postLinks = extractPost(key)
                    print('                  WEB SCRAPING PROCESS')
                    print('--------------------keyword: '+key+' ------------------------')
                    for link in postLinks:
                        id = hashlib.sha224(link.encode()).hexdigest()
                        if(link): 
                            try:
                                user=getProfile(link)
                                if user is not None:
                                    doc={
                                    'id' : id,
                                    'urlpost' : link,
                                    'project' : file.name,
                                    'authorUsername': user[6],
                                    'engine' : 'instagram',
                                    'likesOrReproductions': user[1],
                                    'addedDate' : datetime.now(),
                                    'updatedDate': user[2],
                                    'urlProfile' : user[0],
                                    'followers': user[3],
                                    'followings': user[4],
                                    'description': user[7]
                                            }
                                    if(Searchid(file.name,id)==False):
                                        res_local = es_local.index(index=file.name, id=id , document=doc)
                                        print('New Post successfully scraped... '  +id)    
                                        print('The API instagram is inserting records for the site: '+file.name + ' Time '+str(datetime.now())+' Result: '+res_local['result'])
                                    if(Searchid_cloud(file.name,id)==False):   
                                        res_cloud = es_cloud.index(index=file.name, id=id , document=doc)
                                        print('New Post successfully scraped... '  +id)    
                                        print('The API instagram is inserting records for the site in cloud: '+file.name + ' Time '+str(datetime.now())+' Result: '+res_cloud['result'])     
                            except requests.exceptions.RequestException as e: 
                                raise SystemExit(e)
        print("-------------------------------------\n")
        print("data successfully saved ")    
    time.sleep(7200)        