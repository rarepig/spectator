import sys
import json
from PyQt5.QtWidgets import QApplication, QLabel, QWidget
from PyQt5.QtGui import QFont, QFontDatabase
from PyQt5.QtCore import Qt, QTimer


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(5000)

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(0, 0, 310, 120)  # 윈도우의 위치를 (0, 0)으로, 크기를 (1920, 1080)으로 설정
        self.setWindowTitle("Timer")

        font_id = QFontDatabase.addApplicationFont("data/DungGeunMo.ttf")  # 폰트를 추가
        font_str = QFontDatabase.applicationFontFamilies(font_id)[0]
        self.font = QFont(font_str)
        self.font.setPointSize(19)
        
        self.text_labels = [QLabel(self) for _ in range(4)]

        self.show()
        
    def update_data(self):
        with open('data/graphic_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        start = data["start"]
        end = data["end"]
    
        text_data = [
                ("시작:", (15, 0)),
                ("종료:", (15, 40)),
                (start, (85, 0)),
                (end, (85, 40))
            ]


        for i in range(len(text_data)):
                self.add_text(self.text_labels[i], text_data[i][0], text_data[i][1])


    def add_text(self, label, text, position):
        if text:
            label.setFont(self.font)
            label.setText(text)
            label.setStyleSheet("color: white")

            label_width = len(text) * 20  # 한 글자당 20픽셀로 가정
            label_height = 80

            label_x = position[0]
            label_y = position[1]

            label.setGeometry(label_x, label_y, label_width, label_height)
            label.show()

def open_timer():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    app.exec_()
    

open_timer()

