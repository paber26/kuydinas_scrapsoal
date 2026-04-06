import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException

EMAIL = "ikainjiliahalada@gmail.com"
PASSWORD = "gykU!2T7xV.xfrh"

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--no-sandbox")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
driver.set_page_load_timeout(30)

print("Memulai Chrome dalam mode Headless untuk login...")
driver.get("https://smartcasn.com/login")
time.sleep(3)
driver.find_element(By.NAME, "email").send_keys(EMAIL)
driver.find_element(By.NAME, "password").send_keys(PASSWORD)
driver.find_element(By.ID, "submitbtn").click()
time.sleep(5)  # Make sure login fully processes and sets session tokens

# Now limit page load time for the result page so it doesn't hang forever
driver.set_page_load_timeout(10)
target_url = "https://smartcasn.com/result/1171126/544"
print(f"Mengakses {target_url}...")
try:
    driver.get(target_url)
except TimeoutException:
    print("Page load timed out (expected), extracting HTML anyway...")

time.sleep(5)  # Give JS components time to dynamically render elements

with open("../../logs/result_page.html", "w", encoding="utf-8") as f:
    f.write(driver.page_source)

driver.quit()
print("Saved result_page.html successfully.")
