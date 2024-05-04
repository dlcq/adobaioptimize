import json
from PIL import Image
import os
import tkinter as tk
from tkinter import filedialog
from concurrent.futures import ThreadPoolExecutor

def load_config():
    with open('config.json', 'r') as f:
        config = json.load(f)
    return config['quality'], config['colors'], config['threads']

def compress_image(input_path, output_path, quality, colors):
    try:
        img = Image.open(input_path)
        format = img.format
        
        if format == 'JPEG':
            img.save(output_path, format=format, quality=quality, optimize=True)
        elif format == 'PNG':
            img = img.convert('P', palette=Image.ADAPTIVE, colors=colors)
            img.save(output_path, format=format, optimize=True)
        else:
            print(f"Unsupported format: {format}")
            return False
        print(f"Compression and optimization completed for {input_path}")
        return True
    except Exception as e:
        print(f"Error processing {input_path}: {e}")
        return False

def compress_images_in_folder():
    quality, colors, threads = load_config()
    
    folder_path = filedialog.askdirectory(title="Select the folder containing images")
    if not folder_path:
        print("No folder selected.")
        return
    
    files = os.listdir(folder_path)
    image_files = [f for f in files if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    
    # 既に処理された画像のリストを初期化
    processed_images = []
    
    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = []
        for image_file in image_files:
            input_path = os.path.join(folder_path, image_file)
            output_path = input_path  # 出力パスは入力パスと同じ
            
            # 既に処理された画像かどうかをチェック
            if input_path not in processed_images:
                futures.append(executor.submit(compress_image, input_path, output_path, quality, colors))
                processed_images.append(input_path)
        
        for future in futures:
            if not future.result():
                print("An error occurred during compression.")

# GUIの実行
root = tk.Tk()
root.withdraw()  # メインウィンドウを非表示に
compress_images_in_folder()

# ユーザーがEnterキーを押すまでコンソールを閉じない
input("Press Enter to exit...")
