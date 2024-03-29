import time
import settings
import shutil
import os.path
import pandas as pd
from github import Github
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys

#create Chrome instance
service = Service(executable_path = settings.driver_path)
options = Options()
#True means browser is invisible (issues for some reason)
options.headless = False
options.add_argument("--no-sandbox")
driver = webdriver.Chrome(options = options)
driver.get("https://app.ticketutils.com/")
delay = 600 #seconds

#get username and password elements
SiteUsername = driver.find_element(By.NAME, 'Email')
SitePassword = driver.find_element(By.NAME, 'Password')

#submit login info
SiteUsername.send_keys(settings.TU_username)
SitePassword.send_keys(settings.TU_password)
#click login button
driver.find_element(By.XPATH, "/html/body/div[2]/div/div/form/div/div[3]/button").click()

#click "Reports" button
try:
    Reportsbutton = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.ID, "POS_Reports")))
    driver.find_element(By.ID, "POS_Reports").click()
    print("Reports: Success!")
except TimeoutException:
    print("Reports: Loading took too much time!")

#click "Profit/Loss" button
PLFrame = driver.find_element(By.CSS_SELECTOR, "#WorkArea > div > div.Active > iframe")
try:
    PLbutton = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#WorkArea > div > div.Active > iframe")))
    driver.switch_to.frame(PLFrame)
    driver.find_element(By.XPATH, "/html/body/div[2]/div/div[1]/div/div[1]/div/div/div[2]/ul/li[3]/div/div[1]/a").click()
    print("P/L: Success!")
    driver.switch_to.default_content()
except TimeoutException:
    print("P/L: Loading took too much time!")

#load data table tab
FilterFrame = driver.find_element(By.CSS_SELECTOR, "#WorkArea > div > div.Active > iframe")
try:
    #click next tab
    driver.find_element(By.XPATH, "/html/body/div[2]/nav/div[2]/div[3]/span[3]").click()
except TimeoutException:
    print("Data: Loading took too much time!")
#wait for iframe to load in
ListFrame = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#WorkArea > div > div.Active > iframe")))
driver.switch_to.frame(FilterFrame)
#wait for list of data to load in
ListData = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH, '//*[@id="load_List"][contains(@style, "display: none;")]')))

while(True):
    for i in settings.CompList:
        CompName = i
        try:
            #click filter button
            driver.find_element(By.XPATH, "/html/body/div[1]/div[1]/div[1]/ul/li[1]/a").click()
            #enter filter data
            CustomerFilter = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.ID, "Venue_Value")))
            driver.find_element(By.ID, "Venue_Value").click()
            CustomerFilter.send_keys(Keys.CONTROL, 'A')
            CustomerFilter.send_keys(Keys.BACKSPACE)
            CustomerFilter.send_keys(CompName)
            #filter for past year
            YearFilter = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.ID, "EventDate_Value_Dropdown_ms")))
            driver.find_element(By.ID, "EventDate_Value_Dropdown_ms").click()
            driver.find_element(By.XPATH, "/html/body/div[1]/div[1]/div[2]/div[9]/div/div/ul/li[3]/label").click()
            driver.find_element(By.ID, "EventDate.Value_Year").send_keys("2023")
            #need to click autocomplete for some reason
            time.sleep(1)
            #driver.find_element_by_xpath("/html/body/div[4]/ul/li").click()
            #click search when page is loaded
            driver.find_element(By.ID, "Search").click()
            print("Filter: Success!")
        except TimeoutException:
            print("Filter: Loading took too much time!")
        
        #download excel sheet
        try:
            ListData = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH, '//*[@id="load_List"][contains(@style, "display: none;")]')))
            driver.find_element(By.ID, "MoreActions").click()
            driver.find_element(By.XPATH, "/html/body/div[4]/ul/li[2]").click()
            print("Export: Success!")
        except TimeoutException:
            print("Export: Loading took too long!")
            
        #move new file to correct directory and replace old file
        while os.path.isfile(settings.download_location + "Profit_Loss.xlsx") == False:
            time.sleep(1)
        if os.path.isfile(settings.download_location + "Profit_Loss.xlsx"):
            shutil.move(settings.download_location + "Profit_Loss.xlsx", settings.app_path + CompName + ".xlsx")
        else:
            print("File couldn't be found!")
        
        #convert file to csv
        read_file = pd.read_excel(CompName + ".xlsx")
        read_file.to_csv(CompName + ".csv", index = None, header = True)
        
        #upload csv to github
        g = Github(settings.git_key)

        repo = g.get_user().get_repo(settings.repository_name)
        all_files = []
        contents = repo.get_contents("")
        while contents:
            file_content = contents.pop(0)
            if file_content.type == "dir":
                contents.extend(repo.get_contents(file_content.path))
            else:
                file = file_content
                all_files.append(str(file).replace('ContentFile(path="','').replace('")',''))

        with open(CompName + '.csv', 'r') as file:
            content = file.read()

        # Upload to github
        git_file = CompName + ".csv"
        if git_file in all_files:
            contents = repo.get_contents(git_file)
            repo.update_file(contents.path, "committing files", content, contents.sha, branch="main")
            print(git_file + ' UPDATED')
        else:
            repo.create_file(git_file, "committing files", content, branch="main")
            print(git_file + ' CREATED')
        
#wait 5 minutes then run again
#driver.close()
    time.sleep(300)
