import json
import time
import smtplib
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options

def readCookies(path):
    with open(path, 'r') as cookies:
        return json.load(cookies)

def loadPage(url):
    options = Options()
    options.add_argument("--headless") 
    options.add_argument("--window-size=1920x1080")  
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    driver.get(url)
    wait = WebDriverWait(driver, 10)
    return driver, wait

def injectCookies(cookiesPath, driver, wait):
    cookies = readCookies(cookiesPath)
    for cookie in cookies:
        cookie.pop('sameSite', None)
        try: driver.add_cookie(cookie)
        except: print(f"FAILED: {cookie}")
    driver.refresh()

def getAllMessages(driver, wait):
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "gv-annotation")))
    messages = driver.find_elements(By.CSS_SELECTOR, 'div[_ngcontent-ng-c2418373746]')
    all = []
    for text in messages[-20:]: #Only reads last 20
        textSplit = text.text.split()
        if isMessage(textSplit):
            all.append(parseMessage(textSplit))
    return all

def parseDateTime(timeStr):
    return datetime.strptime(timeStr.strip(), "%B %d %Y, %I:%M%p")

def parseMessage(messageSplit):
    sender = messageSplit[2]
    time = messageSplit[-2]+messageSplit[-1]
    date = ' '.join(messageSplit[-5:-2])
    datetime = f"{date} {time[:-1]}"
    message = ' '.join(messageSplit[3:-6])[0:-1]
    return {"sender": sender, 
            "datetime": datetime, 
            "message": message}            #MESSAGE FORMAT

def isMessage(messageSplit):
    if len(messageSplit)>2: 
        return (messageSplit[0]+messageSplit[1]=="Messagefrom" and ((messageSplit[-1] == "AM.") or (messageSplit[-1]=="PM.")))
    return False

def send(message, sender, password, number):
    full_message = f"Subject: SMS\n\n{message}"
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender, password)
    server.sendmail(sender, number, full_message)
    server.quit()

def formatMessage(message):
    formated = (f'({message["sender"]} {message["datetime"]})\n{message["message"]}')
    return formated
 
def main():
    running = True

    driver, wait = loadPage(r"https://voice.google.com")
    time.sleep(3)
    injectCookies(r"cookies.json", driver, wait)
    driver.get("THREAD LINK HERE")
    time.sleep(3)
    all = getAllMessages(driver, wait)
    print(all)
    print("\n\n\n_______________________NEW MESSAGES____________________________\n\n\n")

    while running:
        time.sleep(5)
        new = getAllMessages(driver, wait)
        for message in new:
            if not (message in all) and (message["sender"] != "you"):
                formated = formatMessage(message)
                try:
                    send(message = formated,
                        sender = "EMAIL",
                        password = "PASSWORD",
                        number="CARRIER EMAIL TO SMS")
                    print(f"Sent: {formated}")
                except Exception as e: 
                    print(f"FAILED TO SEND: {formated}\n{e}")
                all.append(message)
main()


