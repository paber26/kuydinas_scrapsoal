import os
import requests
import pickle
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

chrome_options = Options()
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--no-sandbox")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
driver.get("https://smartcasn.com/login")
time.sleep(3)
driver.find_element(By.NAME, "email").send_keys("ikainjiliahalada@gmail.com")
driver.find_element(By.NAME, "password").send_keys("gykU!2T7xV.xfrh")
driver.find_element(By.ID, "submitbtn").click()
time.sleep(5)

driver.get("https://smartcasn.com/result/1171126/63")
try:
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "table")))
except:
    pass
time.sleep(3)

soup = BeautifulSoup(driver.page_source, 'html.parser')
blocks = soup.find_all(string=lambda text: text and 'Sub-Modul' in text)
for b in blocks:
    print("Found text:", b)
    parent = b.parent
    print("Parent HTML:", parent.prettify() if parent else "")
    grandparent = parent.parent if parent else None
    print("Grandparent HTML:", grandparent.prettify() if grandparent else "")

driver.quit()
