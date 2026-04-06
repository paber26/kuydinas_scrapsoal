import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--no-sandbox")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

print("Navigating to login...")
driver.get("https://smartcasn.com/login")
time.sleep(3)
driver.find_element(By.NAME, "email").send_keys("ikainjiliahalada@gmail.com")
driver.find_element(By.NAME, "password").send_keys("gykU!2T7xV.xfrh")
driver.find_element(By.ID, "submitbtn").click()
time.sleep(3)

print("Navigating to result page...")
driver.set_page_load_timeout(10)
try:
    driver.get("https://smartcasn.com/result/1171126/63")
except TimeoutException:
    print("Page load timed out, continuing...")

time.sleep(3)

html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')

print("--- SEARCH RESULT FOR 'Sub-Modul' ---")
# Menemukan tag yang mengandung teks 'Sub-Modul'
texts = soup.find_all(string=lambda text: text and 'Sub-Modul' in text)
for t in texts:
    parent = t.parent
    grandparent = parent.parent if parent else None
    greatgrandparent = grandparent.parent if grandparent else None
    
    print(f"Text block: '{t.strip()}'")
    if parent:
        print("PARENT:", parent.prettify())
        sib = parent.find_next_sibling()
        if sib:
            print("NEXT SIBLING:", sib.text.strip())
    if grandparent:
        print("GRANDPARENT:", grandparent.prettify())

driver.quit()
