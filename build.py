import PyInstaller.__main__
import os
import sys

# Путь к иконке создается программно
icon_path = "app_icon.ico"

# Создаем простую иконку через Python
from PIL import Image, ImageDraw, ImageFont

def create_icon():
    size = 256
    image = Image.new('RGB', (size, size), color=(52, 152, 219))
    draw = ImageDraw.Draw(image)
    
    # Рисуем монитор
    draw.rectangle([70, 70, 186, 150], outline='white', width=8)
    draw.line([90, 150, 128, 180], fill='white', width=8)
    draw.line([166, 150, 128, 180], fill='white', width=8)
    
    # Рисуем чип
    draw.rectangle([100, 100, 156, 128], outline='white', width=6)
    
    # Линии данных
    draw.line([30, 110, 70, 110], fill='white', width=6)
    draw.line([186, 110, 226, 110], fill='white', width=6)
    draw.line([128, 70, 128, 30], fill='white', width=6)
    draw.line([128, 180, 128, 226], fill='white', width=6)
    
    image.save(icon_path, format='ICO', sizes=[(size, size)])

# Создаем иконку
create_icon()

# Собираем .exe
PyInstaller.__main__.run([
    'hardware_info.py',
    '--name=HardwareInfo',
    '--onefile',
    '--windowed',
    '--icon=' + icon_path,
    '--add-data=' + icon_path + ';.',
    '--hidden-import=PyQt5.sip',
    '--hidden-import=psutil',
    '--hidden-import=wmi',
    '--hidden-import=pywin32',
    '--noconsole',
    '--clean'
])

# Удаляем временную иконку
os.remove(icon_path)
