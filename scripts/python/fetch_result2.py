import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

EMAIL = "ikainjiliahalada@gmail.com"
PASSWORD = "gykU!2T7xV.xfrh"

chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

print("Memulai Chrome dalam mode Headless untuk login...")
driver.get("https://smartcasn.com/login")
time.sleep(3)
driver.find_element(By.NAME, "email").send_keys(EMAIL)
driver.find_element(By.NAME, "password").send_keys(PASSWORD)
driver.find_element(By.ID, "submitbtn").click()
time.sleep(5)

target_url = "https://smartcasn.com/result/1171126/544"
print(f"Mengakses {target_url}...")
driver.get(target_url)
time.sleep(10)  # Wait for JS to render results

with open("../../logs/result_page.html", "w", encoding="utf-8") as f:
    f.write(driver.page_source)

driver.quit()
print("Saved result_page.html successfully.")
