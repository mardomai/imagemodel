import cv2
import pytesseract
import os
import json
import shutil
import logging
from tqdm import tqdm
from pathlib import Path
import argparse


pytesseract.pytesseract.tesseract_cmd = r'path_to_your_tesseract.exe'


logging.basicConfig(filename='image_orientation.log', level=logging.INFO, 
                    format='%(asctime)s %(levelname)s:%(message)s')

def load_config(config_file):
    with open(config_file, 'r') as f:
        return json.load(f)

def rotate_image(img, angle):
    if angle == 90:
        return cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
    elif angle == 180:
        return cv2.rotate(img, cv2.ROTATE_180)
    elif angle == 270:
        return cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
    return img

def check_and_correct_image_orientation(source_folder, correct_rotated_folder, correct_not_rotated_folder):
   
    Path(correct_rotated_folder).mkdir(parents=True, exist_ok=True)
    Path(correct_not_rotated_folder).mkdir(parents=True, exist_ok=True)
    
    images = [f for f in os.listdir(source_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    total_images = len(images)
    
    with tqdm(total=total_images, desc='Processing Images', unit='image') as pbar:
        for filename in images:
            file_path = os.path.join(source_folder, filename)
            try:
                img = cv2.imread(file_path)
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                osd = pytesseract.image_to_osd(gray, output_type=pytesseract.Output.DICT)
                
             
                if osd['rotate'] in [90, 180, 270]:
                    img = rotate_image(img, osd['rotate'])
                    correct_folder = correct_rotated_folder
                    cv2.imwrite(file_path, img)  
                else:
                    correct_folder = correct_not_rotated_folder
                
                if os.path.abspath(source_folder) != os.path.abspath(correct_folder):
                    new_path = os.path.join(correct_folder, filename)
                    shutil.move(file_path, new_path)
                    logging.info(f'Moved {filename} to {correct_folder}')
            
            except Exception as e:
                logging.error(f'Error processing {filename}: {e}')
            
            pbar.update(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Check and correct image orientation.')
    parser.add_argument('--config', type=str, default='config.json', help='Path to the configuration file.')
    args = parser.parse_args()
    
    config = load_config(args.config)
    
    base_path = config['base_path']
    rotated_folder = os.path.join(base_path, config['rotated_folder'])
    not_rotated_folder = os.path.join(base_path, config['not_rotated_folder'])
    
   
    check_and_correct_image_orientation(base_path, rotated_folder, not_rotated_folder)
