import requests
from bs4 import BeautifulSoup
from datetime import datetime

class Handout:
    def __init__(self, filename: str, content: bytes, updated_time: datetime):
        self.filename = filename
        self.content = content
        self.updated_time = updated_time
    
def last_update(cookie: str, course_id: str):
    headers = {
        'Cookie': cookie,  # 使用標準的 Cookie 標頭
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0 Safari/537.36',
    }
    url = 'https://ncueeclass.ncu.edu.tw/course/material/' + course_id
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to fetch materials: HTTP {response.status_code}")
            return 0
        update=[]
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a', href=True)
        for link in links:
            href = link['href']
            if href[:11]=="/media/doc/":
                file_url = "https://ncueeclass.ncu.edu.tw"+href
                file_response = requests.get(file_url, headers=headers)
                file_soup = BeautifulSoup(file_response.text, 'html.parser')
                spans = file_soup.find_all('span', class_='text')
                filedate = ""
                for span in spans:
                    # 檢查文本是否包含 'pdf' 或 '下載 PDF'
                    text = span.get_text().lower()
                    if 'pdf' in text:
                        file_date = file_soup.find('div', class_='ext2 fs-hint')
                        i=0
                        for date in file_date.get_text():
                            if date=='間':
                                i+=2
                                while(file_date.get_text()[i]!=','):
                                    filedate+=file_date.get_text()[i]
                                    i+=1
                                if len(filedate)==5:
                                    filedate = str(datetime.today().year)+"-"+filedate
                                update.append(filedate)
                                break
                            i+=1               
                        break
        return max(update)
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    return 0


# Return a list of Handout objects
def get_handouts(cookie: str, course_id: str):
    headers = {
        'Cookie': cookie,  # 使用標準的 Cookie 標頭
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0 Safari/537.36',
    }
    url = 'https://ncueeclass.ncu.edu.tw/course/material/' + course_id
    handouts = []
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to fetch materials: HTTP {response.status_code}")
            return handouts
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

          # 找到所有符合條件的 <a> 標籤
        links = soup.find_all('a', href=True)

        for link in links:
            href = link['href']
            if href[:11]=="/media/doc/":
                file_url = "https://ncueeclass.ncu.edu.tw"+href
                # print(file_url)
                file_response = requests.get(file_url, headers=headers)
                # print(file_response.text)
                file_soup = BeautifulSoup(file_response.text, 'html.parser')
                spans = file_soup.find_all('span', class_='text')
                

                for span in spans:
                    # print(span.get_text())
                    # 檢查文本是否包含 'pdf' 或 '下載 PDF'
                    text = span.get_text().lower()
                    if 'pdf' in text:
                        file_div = file_soup.find('div', class_='title pull-left')
                        filename = file_div.get_text()
                        filename = filename.replace(" ", "")
                        filename = filename.replace("\n", "")
                        print(filename)
                        a_tag = span.find_parent('a', href=True)
                        print(a_tag['href'])

                        fileurl = requests.get("https://ncueeclass.ncu.edu.tw"+a_tag['href'], headers=headers).content
                        with open("file_content.txt", 'wb') as f:
                            f.write(fileurl)

                        with open("file_content.txt", 'rb') as f:
                            content=f.read()

                        file_date = file_soup.find('div', class_='ext2 fs-hint')
                        i=0
                        filedate = ""
                        for date in file_date.get_text():
                            if date=='間':
                                i+=2
                                while(file_date.get_text()[i]!=','):
                                    filedate+=file_date.get_text()[i]
                                    i+=1
                                if len(filedate)==5:
                                    filedate = str(datetime.today().year)+"-"+filedate
                                print(filedate)
                                handouts.append(Handout(filename=filename, content=content, updated_time=filedate))
                                break
                            i+=1               
                        break

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

    return handouts


# c = "PHPSESSID=33e5in7bdb09u640h8hh9k8ibo; account=111502504; accesstoken=1668991233"
# get_handouts(c,"28702")
# last_update(c,"28702")
