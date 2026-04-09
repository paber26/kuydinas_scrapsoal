import os
import shutil
import re

def get_range(num, size=50):
    if num == 0:
        return "0" # Should not happen based on listing
    lower = ((num - 1) // size) * size + 1
    upper = lower + size - 1
    return f"{lower}-{upper}"

def reorganize(base_path, pattern):
    print(f"Checking directory: {base_path}")
    if not os.path.exists(base_path):
        print(f"Path does not exist: {base_path}")
        return

    items = os.listdir(base_path)
    for item in items:
        item_path = os.path.join(base_path, item)
        
        # Skip directories that look like ranges
        if os.path.isdir(item_path) and re.match(r'^\d+-\d+$', item):
            continue
            
        # Extract number
        match = re.search(r'_(\d+)', item)
        if match:
            num = int(match.group(1))
            range_folder = get_range(num)
            target_dir = os.path.join(base_path, range_folder)
            
            if not os.path.exists(target_dir):
                print(f"Creating folder: {target_dir}")
                os.makedirs(target_dir)
            
            target_path = os.path.join(target_dir, item)
            print(f"Moving {item} -> {range_folder}/")
            shutil.move(item_path, target_path)
        else:
            print(f"Could not find module number in: {item}")

if __name__ == "__main__":
    base_dir = r"D:\KuyDinas2026\masukkansoal\data"
    
    # Reorganize 'soal'
    reorganize(os.path.join(base_dir, "soal"), r"soal_tryout_modul_(\d+)")
    
    # Reorganize 'pembahasan'
    reorganize(os.path.join(base_dir, "pembahasan"), r"modul_(\d+)")
