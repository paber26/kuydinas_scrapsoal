import os
import shutil

for i in range(1, 100):
    modul_id = str(i)
    json_file = f"../../data/pembahasan/pembahasan_modul_{modul_id}.json"
    img_folder = f"../../data/gambar/gambar_pembahasan_modul_{modul_id}"
    
    # Periksa apakah ada file/folder yang perlu dipindahkan
    if os.path.exists(json_file) or os.path.exists(img_folder):
        target_folder = f"../../data/pembahasan/hasil_pembahasan_modul_{modul_id}"
        if not os.path.exists(target_folder):
            os.makedirs(target_folder)
            
        target_img_folder = os.path.join(target_folder, "gambar")
        if not os.path.exists(target_img_folder):
            os.makedirs(target_img_folder)
            
        # Pindahkan JSON
        if os.path.exists(json_file):
            shutil.move(json_file, os.path.join(target_folder, json_file))
            print(f"Memindahkan: {json_file} -> {target_folder}/")
            
        # Pindahkan isi folder gambar
        if os.path.exists(img_folder):
            for filename in os.listdir(img_folder):
                source = os.path.join(img_folder, filename)
                destination = os.path.join(target_img_folder, filename)
                shutil.move(source, destination)
            print(f"Memindahkan isi gambar dari: {img_folder}/ -> {target_img_folder}/")
            
            # Hapus folder gambar lama yang sudah kosong
            try:
                os.rmdir(img_folder)
            except OSError:
                print(f"Gagal menghapus folder lama {img_folder}")
                
print("Selesai reorganisasi file!")
