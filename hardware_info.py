import sys
import platform
import psutil
import wmi
import subprocess
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QFrame, QScrollArea)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon, QPixmap, QPainter, QBrush
from PyQt5.QtCore import QSize

class HardwareInfoWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Информация о железе")
        self.setFixedSize(800, 600)
        self.setWindowIcon(self.create_icon())
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Основной layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Заголовок
        header = QLabel("📊 ХАРАКТЕРИСТИКИ КОМПЬЮТЕРА")
        header.setAlignment(Qt.AlignCenter)
        header.setFont(QFont("Segoe UI", 18, QFont.Bold))
        header.setStyleSheet("""
            QLabel {
                background-color: #2c3e50;
                color: white;
                padding: 15px;
            }
        """)
        main_layout.addWidget(header)
        
        # Скролл область для содержимого
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #ecf0f1;
            }
        """)
        
        # Контейнер для информации
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: #ecf0f1;")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(0)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Получаем информацию
        info = self.get_hardware_info()
        
        # Создаем карточки с информацией
        for key, value in info.items():
            card = self.create_info_card(key, value)
            content_layout.addWidget(card)
        
        # Добавляем растяжку внизу
        content_layout.addStretch()
        
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)
        
        # Таймер для обновления (опционально)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_info)
        # self.timer.start(5000)  # Обновление каждые 5 секунд (закомментировано)
    
    def create_icon(self):
        """Создаем иконку программно"""
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Круглый фон
        painter.setBrush(QBrush(QColor(52, 152, 219)))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(4, 4, 56, 56)
        
        # Монитор
        painter.setPen(QColor(255, 255, 255))
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(18, 18, 28, 20)
        painter.drawLine(24, 38, 32, 44)
        painter.drawLine(40, 38, 32, 44)
        
        # Чип на мониторе
        painter.drawRect(26, 24, 12, 8)
        
        # Линии передачи данных
        painter.drawLine(12, 32, 18, 32)
        painter.drawLine(46, 32, 52, 32)
        painter.drawLine(32, 18, 32, 12)
        painter.drawLine(32, 44, 32, 50)
        
        painter.end()
        return QIcon(pixmap)
    
    def create_info_card(self, title, value):
        """Создает красивую карточку с информацией"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                margin: 5px 15px;
                padding: 0px;
            }
            QFrame:hover {
                background-color: #f8f9fa;
                border: 1px solid #bdc3c7;
            }
        """)
        card.setFixedHeight(60)
        
        layout = QHBoxLayout(card)
        layout.setContentsMargins(20, 0, 20, 0)
        
        # Заголовок
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50; min-width: 180px;")
        title_label.setFixedWidth(180)
        
        # Разделитель
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background-color: #bdc3c7;")
        separator.setFixedWidth(1)
        
        # Значение
        value_label = QLabel(value)
        value_label.setFont(QFont("Segoe UI", 11))
        value_label.setStyleSheet("color: #34495e;")
        value_label.setWordWrap(True)
        
        layout.addWidget(title_label)
        layout.addWidget(separator)
        layout.addWidget(value_label)
        layout.addStretch()
        
        return card
    
    def get_hardware_info(self):
        """Собирает информацию о железе"""
        info = {}
        
        try:
            # Процессор
            info["Процессор"] = platform.processor() or "Intel/AMD Processor"
            
            # Оперативная память
            memory = psutil.virtual_memory()
            total_ram_gb = memory.total / (1024**3)
            info["Оперативная память"] = f"{total_ram_gb:.1f} GB"
            
            # Видеокарта (через WMI)
            try:
                c = wmi.WMI()
                for gpu in c.Win32_VideoController():
                    if gpu.Name and "microsoft" not in gpu.Name.lower() and "basic" not in gpu.Name.lower():
                        info["Видеокарта"] = gpu.Name
                        break
                if "Видеокарта" not in info:
                    info["Видеокарта"] = "Встроенная видеокарта"
            except:
                info["Видеокарта"] = "Не удалось определить"
            
            # Диски
            disks = psutil.disk_partitions()
            disk_info = []
            for disk in disks:
                if disk.device:
                    try:
                        usage = psutil.disk_usage(disk.mountpoint)
                        size_gb = usage.total / (1024**3)
                        disk_info.append(f"{disk.device} ({size_gb:.1f} GB)")
                    except:
                        pass
            
            if disk_info:
                info["Диски"] = "\n".join(disk_info[:2])  # Показываем первые 2 диска
            else:
                info["Диски"] = "Не найдено"
            
            # Материнская плата (через WMI)
            try:
                c = wmi.WMI()
                for board in c.Win32_BaseBoard():
                    if board.Product:
                        info["Материнская плата"] = f"{board.Manufacturer or ''} {board.Product}".strip()
                        break
                if "Материнская плата" not in info:
                    info["Материнская плата"] = "Неизвестно"
            except:
                info["Материнская плата"] = "Не удалось определить"
            
            # Операционная система
            info["ОС"] = f"{platform.system()} {platform.version()}"
            
            # Дополнительная информация
            info["Архитектура"] = platform.machine()
            
        except Exception as e:
            info["Ошибка"] = f"Не удалось получить данные: {str(e)}"
        
        return info
    
    def update_info(self):
        """Обновляет информацию (не используется в этой версии)"""
        pass

def main():
    app = QApplication(sys.argv)
    
    # Настройка стиля приложения
    app.setStyle('Fusion')
    
    # Настройка палитры
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(236, 240, 241))
    palette.setColor(QPalette.WindowText, QColor(44, 62, 80))
    app.setPalette(palette)
    
    window = HardwareInfoWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
