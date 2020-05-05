import requests,json,os,time,sys
from bs4 import BeautifulSoup
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

#Add base url to the CTFd platform with/
BaseUrl =  "https://www.name.ctfd.com/"
api = BaseUrl+"/api/v1/challenges"

headers = {
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
}

# Add username and password
login_data = {
    'name': '',
    'password': '',
    'nonce': ''
}

with requests.Session() as s:
    url = BaseUrl+'login'
    r = s.get(url, headers=headers,verify=False)
    soup = BeautifulSoup(r.content, 'html5lib')
    login_data['nonce'] = soup.find('input', attrs={'name': 'nonce'})['value']
    r = s.post(url, data=login_data, headers=headers,verify=False)
    try:
        response = s.get(api, verify=False).json()
        
    except ValueError as e:
        print(" API provided doesn't return json OR username and password are not correct")
        exit()
    challenges = []
    for ch in response['data']:
        challengeUrl = api+'/'+str(ch['id'])
        r = s.get(challengeUrl, headers=headers, verify=False).json()
        challenges.append(r['data'])
   
    path = os.getcwd()
    directories = []

    for chal in challenges:
        if chal['category'] not in directories:
            os.mkdir(path+"/"+chal['category'])
            directories.append(chal['category'])
                        
            for challenge in challenges:
                if (challenge['category'] == chal['category']):
                    if(challenge['name'] not in directories):
                        os.mkdir(path+"/"+chal['category']+"/"+challenge['name'])
                        print(chal['category']+"/"+challenge['name']," created")
                        directories.append(challenge['name'])            
                                    
                        with open(path+"/"+chal['category']+"/"+challenge['name']+"/"+"Descripton",'w') as fhandle:
                            fhandle.write("Category: "+challenge['category']+"\n")
                            fhandle.write("Name: "+challenge['name']+"\n")
                            fhandle.write("Description:\n"+challenge['description']+"\n")
                                    
                        if(challenge['files'] is not None):
                            for cfile in challenge['files']:

                                #Some platforms have their file download link with a ?token=randome
                                chalfile = cfile.split('?')[0]
                                with s.get(BaseUrl+chalfile, headers=headers, stream=True, verify=False) as r:
                                    print("Downloading "+chalfile)
                                    r.raise_for_status()

                                    #Get rid of the randome folder name generated to avoid name collision 
                                    #example /files/randome/crackme.zip
                                    filename = chalfile.split('/')[3]
                                    with open(path+"/"+chal['category']+"/"+challenge['name']+"/"+filename, 'wb') as f:
                                        for chunk in r.iter_content(chunk_size=8192):
                                            f.write(chunk)        
        
        
