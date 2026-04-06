import pickle
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

driver.get("https://smartcasn.com")
time.sleep(2)
with open("../../data/misc/cookies.pkl", "rb") as f:
    cookies = pickle.load(f)
    for cookie in cookies:
        driver.add_cookie(cookie)

driver.get("https://smartcasn.com/result/1171126/544")
time.sleep(5)
with open("../../logs/result_page.html", "w", encoding="utf-8") as f:
    f.write(driver.page_source)

driver.quit()
print("Saved result_page.html")
