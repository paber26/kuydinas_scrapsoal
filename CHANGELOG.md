# Changelog (Update Terbaru)

## [April 2026] - Reorganisasi Workspace & Struktur Direktori

### ♻️ Refactoring & Perbaikan Struktur
* **Reorganisasi Total (*Clutter Cleanup*)**: Membersihkan lebih dari 300 file `.txt`, ratusan direktori gambar, data cookie, dan log error yang tadinya berceceran di *root directory*. Semuanya kini dikategorikan rapi ke dalam `data/`, `logs/`, dan `scripts/`.
* **Pemisahan Script**: 
  * Kode ekstraksi python dipindahkan ke dalam `scripts/python/`.
  * Folder Javascript untuk unggah soal API ("masukkan soal otomatis") di-*rename* menjadi `scripts/masukkan_soal_otomatis` tanpa spasi untuk kepatuhan standar format rute.
* **Update Referensi Path Otomatis**: Memodifikasi seluruh isi `*.py` dan `index.js` agar menulis output JSON/TXT maupun mengakses error log mengarah ke folder yang baru (`../../data/`, `../../logs/`).

### ✨ Fitur Baru
* **Script Pencarian Global**: Menambahkan `cari_teks.js` (`scripts/masukkan_soal_otomatis/cari_teks.js`) sebagai alat otomatis untuk mencari kalimat spesifik menembus keseluruhan file `.txt`, `.json`, `.js`, dan `.py` di dalam struktur direktori tanpa harus buka IDE pencarian secara manual.

Soal yang sudah dimasukkan
- 
- 