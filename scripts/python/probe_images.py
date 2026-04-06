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
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

print("Navigating to login...")
driver.get("https://smartcasn.com/login")
time.sleep(3)
driver.find_element(By.NAME, "email").send_keys("ikainjiliahalada@gmail.com")
driver.find_element(By.NAME, "password").send_keys("gykU!2T7xV.xfrh")
driver.find_element(By.ID, "submitbtn").click()
time.sleep(3)

print("Navigating to module 63...")
driver.get("https://smartcasn.com/result/1171126/63")

try:
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "table")))
except Exception as e:
    print("Timeout waiting for table:", e)

time.sleep(3)
html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')

images = soup.find_all('img')
print(f"Total images found: {len(images)}")
for idx, img in enumerate(images[:10]):  # Print first 10
    src = img.get('src', 'NO_SRC')
    print(f"Image {idx}: {src[:100]}...")

driver.quit()
