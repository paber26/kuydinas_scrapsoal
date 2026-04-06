import requests
import pickle

with open("../../data/misc/cookies.pkl", "rb") as f:
    cookies = pickle.load(f)

# Convert selenium cookies to requests cookies
session = requests.Session()
for cookie in cookies:
    session.cookies.set(cookie['name'], cookie['value'])

url = "https://smartcasn.com/result/1171126/544"
print(f"Fetching {url}...")
response = session.get(url)

with open("../../logs/result_page.html", "w", encoding="utf-8") as f:
    f.write(response.text)

print("Saved result_page.html successfully.")
