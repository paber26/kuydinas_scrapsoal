import time
import pickle
from selenium import webdriver
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
driver.set_page_load_timeout(10) # 10 seconds timeout

driver.get("https://smartcasn.com")
time.sleep(2)

with open("../../data/misc/cookies.pkl", "rb") as f:
    cookies = pickle.load(f)
    for cookie in cookies:
        driver.add_cookie(cookie)

target_url = "https://smartcasn.com/result/1171126/544"
print(f"Mengakses {target_url}...")
try:
    driver.get(target_url)
except TimeoutException:
    print("Page load timed out, getting source anyway...")
    
time.sleep(5)  # Wait for JS to render the react components

with open("../../logs/result_page.html", "w", encoding="utf-8") as f:
    f.write(driver.page_source)

driver.quit()
print("Saved result_page.html successfully.")
