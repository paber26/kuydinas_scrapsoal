import os
import requests
import pickle
import json
import time
import base64
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Konfigurasi Options
chrome_options = Options()
# chrome_options.add_argument("--headless") # Jalankan dengan UI agar terlihat jika ada masalah
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--no-sandbox")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
# Tidak membatasi page_load_timeout agar ChromeDriver terhindar dari crash ketika jaringan me-request gambar/JS

# Kredensial
EMAIL = "ikainjiliahalada@gmail.com"
PASSWORD = "gykU!2T7xV.xfrh"

print("Memulai proses scraping pembahasan...")

# Login Manual
print("Melakukan Login Manual...")
driver.get("https://smartcasn.com/login")
time.sleep(3)
driver.find_element(By.NAME, "email").send_keys(EMAIL)
driver.find_element(By.NAME, "password").send_keys(PASSWORD)
driver.find_element(By.ID, "submitbtn").click()
time.sleep(5)
print("Berhasil Login!")


# --- KONFIGURASI URL & MODUL ---
ATTEMPT_ID = "1173152"

def process_html_with_images(html_content, prefix_name, folder_path):
    """
    Ekstrak gambar dari konten HTML, download, simpan secara lokal,
    lalu gantikan tag img dengan referensi file lokal.
    """
    if not html_content:
        return ""
        
    soup = BeautifulSoup(html_content, 'html.parser')
    img_tags = soup.find_all('img')
    
    for idx, img in enumerate(img_tags):
        img_url = img.get('src')
        if img_url:
            if not img_url.startswith('http') and not img_url.startswith('data:image'):
                img_url = "https://smartcasn.com" + (img_url if img_url.startswith('/') else '/' + img_url)
            
            img_filename = f"{prefix_name}_img{idx+1}.png"
            img_path = os.path.join(folder_path, img_filename)
            
            try:
                if img_url.startswith("data:image"):
                    header, encoded = img_url.split(",", 1)
                    with open(img_path, "wb") as f:
                        f.write(base64.b64decode(encoded))
                    new_text = soup.new_string(f"\n[GAMBAR: {img_path}]\n")
                    img.replace_with(new_text)
                else:
                    session_cookies = {c['name']: c['value'] for c in driver.get_cookies()}
                    response = requests.get(img_url, cookies=session_cookies)
                    if response.status_code == 200:
                        with open(img_path, 'wb') as f:
                            f.write(response.content)
                        new_text = soup.new_string(f"\n[GAMBAR: {img_path}]\n")
                        img.replace_with(new_text)
                    else:
                        print(f"Gagal download gambar {img_url}. Status: {response.status_code}")
            except Exception as e:
                print(f"Error download gambar {img_url}: {e}")
                
    return soup.get_text(separator='\n', strip=True)


for target_modul in range(324, 327):
    MODUL_ID = str(target_modul)
    target_url = f"https://smartcasn.com/result/{ATTEMPT_ID}/{MODUL_ID}"
    
    print(f"\n=============================================")
    print(f"Memproses Modul {MODUL_ID}")
    print(f"Mengakses halaman hasil: {target_url}")
    try:
        driver.get(target_url)
    except TimeoutException:
        print("Timeout saat loading halaman. Melanjutkan ekstraksi...")
    
    time.sleep(5)  # Tunggu rendering JS
    
    # Struktur Folder Utama
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_data_dir = os.path.abspath(os.path.join(script_dir, "../../data/pembahasan"))
    folder_utama = os.path.join(base_data_dir, f"hasil_pembahasan_modul_{MODUL_ID}")
    if not os.path.exists(folder_utama):
        os.makedirs(folder_utama)
        
    # Struktur Folder Gambar (di dalam folder utama)
    folder_gambar = os.path.join(folder_utama, "gambar")
    if not os.path.exists(folder_gambar):
        os.makedirs(folder_gambar)
        
    hasil_json = []

    try:
        print("Menunggu tabel soal dimuat sepenuhnya...")
        # Tunggu maksimal 15 detik sampai setidaknya ada satu <table> (soal) yang ter-render
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "table"))
            )
        except TimeoutException:
            print(f"⚠️ Halaman {target_url} kemungkinan tidak valid atau tidak memiliki soal. Melewati modul ini...")
            continue
        
        # Scroll ke bawah untuk memastikan semua termuat (opsional untuk lazy loading)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        
        html_source = driver.page_source
        soup = BeautifulSoup(html_source, 'html.parser')
        
        # Ekstrak Nama Sub-Modul
        nama_sub_modul = "Sesuai Halaman"
        try:
            sub_modul_label = soup.find('div', class_='label', string=lambda t: t and 'Sub-Modul' in t)
            if sub_modul_label:
                sub_modul_value = sub_modul_label.find_next_sibling('div', class_='value')
                if sub_modul_value:
                    nama_sub_modul = sub_modul_value.get_text(strip=True)
            print(f"Nama Sub-Modul: {nama_sub_modul}")
        except Exception as e:
            print(f"Batal mengekstrak label Sub-Modul: {e}")
        
        # Kita cari tabel-tabel pada halaman
        tables = soup.find_all('table')
        
        if len(tables) == 0:
            print("⚠️ Tidak ada tabel soal ditemukan. Melewati modul ini...")
            continue
        else:
            print(f"Ditemukan {len(tables)} tabel (kemungkinan {len(tables)} soal). Memproses...")
            
            for idx, table in enumerate(tables):
                i = idx + 1
                try:
                    # 1. Ekstrak Teks Pertanyaan
                    pertanyaan_teks = ""
                    for row in table.find_all('tr'):
                        teks_baris = row.get_text().lower()
                        if 'pertanyaan' in teks_baris and 'tidak dijawab' in teks_baris or 'benar' in teks_baris or 'salah' in teks_baris:
                            tds = row.find_all('td')
                            if len(tds) >= 2:
                                pertanyaan_teks = process_html_with_images(str(tds[1]), f"soal_{i}", folder_gambar)
                            else:
                                pertanyaan_teks = process_html_with_images(str(row), f"soal_{i}", folder_gambar)
                            break
                    
                    if not pertanyaan_teks:
                        seluruh_teks = table.get_text(separator='|', strip=True)
                        pertanyaan_teks = seluruh_teks.split('Pilihan')[0]
    
                    # 2. Ekstrak Pilihan dan Jawaban Benar
                    opsi_list = []
                    jawaban_benar = ""
                    
                    for row in table.find_all('tr'):
                        if 'Pilihan' in row.get_text():
                            opsi_blocks = row.find_all('div', recursive=True)
                            for opt_idx, opt in enumerate(opsi_blocks):
                                if len(opt.get_text(strip=True)) > 0 and opt.find_parent('div') is not None:
                                    opt_text = process_html_with_images(str(opt), f"soal_{i}_opt_{opt_idx}", folder_gambar)
                                    if opt_text and len(opt_text) > 2 and opt_text not in opsi_list: 
                                        bersih = opt_text.replace('Benar', '').strip()
                                        opsi_list.append(bersih)
                                    
                                    if 'Benar' in opt.get_text() or 'text-success' in str(opt) or 'true-ans' in str(opt):
                                        jawaban_benar = opt_text.replace('Benar', '').strip()
                            break
                    
                    # 3. Ekstrak Penjelasan Jawaban
                    pembahasan_teks = "Pembahasan tidak ditemukan"
                    for row in table.find_all('tr'):
                        if 'Penjelasan Jawaban' in row.get_text():
                            tds = row.find_all('td')
                            if len(tds) >= 2:
                                pembahasan_teks = process_html_with_images(str(tds[1]), f"soal_{i}_pemb", folder_gambar)
                            else:
                                pembahasan_teks = process_html_with_images(str(row), f"soal_{i}_pemb", folder_gambar)
                            break
                            
                    hasil_json.append({
                        "nomor": i,
                        "sub_modul": nama_sub_modul,
                        "pertanyaan": pertanyaan_teks,
                        "pilihan": [op for op in opsi_list if op],
                        "jawaban_benar": jawaban_benar,
                        "pembahasan": pembahasan_teks
                    })
                    print(f"✔ Pembahasan Soal {i} berhasil diproses dari tabel")
                    
                except Exception as e:
                    print(f"❌ Tabel soal {i} gagal diproses: {e}")
    
    except Exception as e:
        print(f"Error utama saat membedah DOM modul {MODUL_ID}: {e}")
    
    # 3. Export ke JSON
    file_json_name = f"pembahasan_modul_{MODUL_ID}.json"
    file_json_path = os.path.join(folder_utama, file_json_name)
    
    # Safety Check
    if len(hasil_json) > 0:
        with open(file_json_path, "w", encoding="utf-8") as json_file:
            json.dump(hasil_json, json_file, ensure_ascii=False, indent=4)
        print(f"🎉 Modul {MODUL_ID} berhasil! Sebanyak {len(hasil_json)} soal dirangkum dalam folder {folder_utama}")
    else:
        print(f"⚠️ Modul {MODUL_ID} dilewati karena tidak ada data yang berhasil diekstrak.")

driver.quit()
print("\nSemua modul 1-20 telah selesai diproses.")
