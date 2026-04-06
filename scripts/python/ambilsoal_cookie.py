import os
import requests
import pickle
import base64
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

# Setup driver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# EMAIL = "bernaldo.stis@gmail.com"
# PASSWORD = "xaQrwdZ8Wt#W#T4"
EMAIL = "ikainjiliahalada@gmail.com"
PASSWORD = "gykU!2T7xV.xfrh"

# buka halaman login
driver.get("https://smartcasn.com/login")
time.sleep(3)

# isi email & password
driver.find_element(By.NAME, "email").send_keys(EMAIL)
driver.find_element(By.NAME, "password").send_keys(PASSWORD)

# klik tombol login
driver.find_element(By.ID, "submitbtn").click()
time.sleep(5)


# Tentukan rentang modul yang akan discrap (misal 100 sampai 115)
modul_start = 452
modul_end = 500
modul_list = range(modul_start, modul_end + 1)

# List untuk mencatat status
berhasil_list = []
gagal_list = []

for mod in modul_list:
    print(f"\n======================================")
    print(f"=== Mengambil soal Modul {mod} ===")
    print(f"======================================")
    
    # redirect ke halaman soal
    target_url = f"https://smartcasn.com/test/module/{mod}?init=true"
    driver.get(target_url)
    time.sleep(5)
    
    # Cek apakah terlempar ke halaman login
    if "login" in driver.current_url.lower():
        print(f"⚠️ Sesi terputus! Terlempar ke halaman login saat mencoba modul {mod}.")
        print("Mencoba login kembali secara otomatis...")
        try:
            driver.get("https://smartcasn.com/login")
            time.sleep(3)
            driver.find_element(By.NAME, "email").send_keys(EMAIL)
            driver.find_element(By.NAME, "password").send_keys(PASSWORD)
            driver.find_element(By.ID, "submitbtn").click()
            time.sleep(5)
            print("✅ Berhasil login ulang.")
            # Coba akses kembali modul tujuan
            driver.get(target_url)
            time.sleep(5)
        except Exception as e:
            print(f"❌ Gagal login ulang otomatis: {e}")

    hasil = []
    
    img_dir = f"../../data/gambar/gambar_modul_{mod}"
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)
    
    # Periksa apakah halaman Not Found
    if "404 Not Found" in driver.page_source or "Not Found" in driver.title or "not found" in driver.page_source.lower():
        print(f"⚠️ Modul {mod} tidak ditemukan (Not Found). Dihapus/Melompati modul ini...")
        gagal_list.append(str(mod))
        continue

    # Cari tahu jumlah soal dari grid navigasi
    num_cells = driver.find_elements(By.XPATH, "//div[contains(@class, 'num-cell')]")
    total_soal = len(num_cells)
    
    if total_soal == 0:
        print(f"⚠️ Tidak dapat menemukan soal (grid kosong) untuk modul {mod}! Mungkin akses ditolak atau modul kosong. Melompati...")
        gagal_list.append(str(mod))
        continue
        
    print(f"Ditemukan {total_soal} soal.")

    def process_html_with_images(html_content, prefix_name):
        soup = BeautifulSoup(html_content, 'html.parser')
        img_tags = soup.find_all('img')
        
        for idx, img in enumerate(img_tags):
            img_url = img.get('src')
            if img_url:
                img_filename = f"{prefix_name}_img{idx+1}.png"
                img_path = os.path.join(img_dir, img_filename)
                
                try:
                    if img_url.startswith("data:image"):
                        header, encoded = img_url.split(",", 1)
                        with open(img_path, "wb") as f:
                            f.write(base64.b64decode(encoded))
                        new_text = soup.new_string(f"\n(arahkan gambar ke folder penyimpanan gambar: {img_path})\n")
                        img.replace_with(new_text)
                    else:
                        if not img_url.startswith('http'):
                            img_url = "https://smartcasn.com" + (img_url if img_url.startswith('/') else '/' + img_url)
                        
                        selenium_cookies = driver.get_cookies()
                        session_cookies = {c['name']: c['value'] for c in selenium_cookies}
                        
                        response = requests.get(img_url, cookies=session_cookies)
                        if response.status_code == 200:
                            with open(img_path, 'wb') as f:
                                f.write(response.content)
                            
                            new_text = soup.new_string(f"\n(arahkan gambar ke folder penyimpanan gambar: {img_path})\n")
                            img.replace_with(new_text)
                        else:
                            print(f"Gagal download gambar {img_url}, status: {response.status_code}")
                except Exception as e:
                    print(f"Error download gambar {img_url}: {e}")
                    
        return soup.get_text(separator='\n', strip=True)

    # Loop semua nomor soal
    for i in range(1, total_soal + 1):
        try:
            # klik nomor soal
            nomor = driver.find_element(By.XPATH, f"//div[contains(@onclick, '_goToIndex({i})')]")
            driver.execute_script("arguments[0].click();", nomor)
            time.sleep(1.5)

            # ambil HTML soal
            soal_html = driver.find_element(By.ID, "Soal").get_attribute("innerHTML")
            soal = process_html_with_images(soal_html, f"soal_{i}")

            # ambil opsi jawaban
            opsi_elements = driver.find_elements(By.CSS_SELECTOR, "#Options .opt")
            opsi = []
            for opt_idx, opt_el in enumerate(opsi_elements):
                opt_html = opt_el.get_attribute("innerHTML")
                opt_text = process_html_with_images(opt_html, f"soal_{i}_opt_{opt_idx+1}")
                opsi.append(opt_text.replace('\n', '. '))

            hasil.append({
                "no": i,
                "soal": soal,
                "opsi": opsi
            })

            print(f"✔ Soal {i} berhasil diambil")

        except Exception as e:
            print(f"❌ Soal {i} gagal:", str(e).split('\n')[0])

    # simpan ke file txt
    nama_file = f"../../data/soal/soal_tryout_modul_{mod}.txt"
    with open(nama_file, "w", encoding="utf-8") as f:
        for item in hasil:
            f.write(f"Soal {item['no']}:\n")
            f.write(item["soal"] + "\n")
            for opt in item["opsi"]:
                f.write(opt + "\n")
            f.write("\n" + "="*50 + "\n\n")

    print(f"✅ Semua soal dari modul {mod} berhasil disimpan ke {nama_file}")
    berhasil_list.append(str(mod))

print("\n🎉 Proses scraping selesai!")
print("================ Summary ================")
print(f"✅ Disimpan     : {', '.join(berhasil_list) if berhasil_list else 'Tidak ada'}")
print(f"❌ Tidak diakses: {', '.join(gagal_list) if gagal_list else 'Tidak ada'}")
print("=========================================")

driver.quit()
