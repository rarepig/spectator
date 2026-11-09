import sys
import json
import random
import time
from PyQt5.QtWidgets import QApplication, QLabel, QWidget
from PyQt5.QtGui import QPixmap, QFont, QFontDatabase, QFontMetrics, QMovie
from PyQt5.QtCore import Qt, QTimer
from utils import read_datafile, case_insensitive_search


def find_gamer_by_summoner(data, summoner_name):
    for gamer, summoners in data.items():
        if summoner_name in summoners[0]:
            return gamer
    return None


def labelling(certain_list, target):
    data = read_datafile()
    gamer_list = []
    label_list = []
    text_list = []
    who_target = ""
    for gamer, summoners in data.items():
        if target in summoners[0]:
            if case_insensitive_search(gamer, "KDF DuDu"):
                who_target = "data/images/dudu.png"
            elif case_insensitive_search(gamer, "KDF Youngjae"):
                who_target = "data/images/youngjae.png"
            elif case_insensitive_search(gamer, "KDF bulldog"):
                who_target = "data/images/bulldog.png"
            elif case_insensitive_search(gamer, "KDF taeyoon"):
                who_target = "data/images/taeyoon.png"
            elif case_insensitive_search(gamer, "KDF jun"):
                who_target = "data/images/jun.png"
            elif case_insensitive_search(gamer, "KDF moham"):
                who_target = "data/images/moham.png" 
            elif case_insensitive_search(gamer, "KDF cvMax"):
                who_target = "data/images/cvmax.png" 
    for summoner in certain_list:
        gamer_list.append(find_gamer_by_summoner(data, summoner))
    print(gamer_list)
    for i in range(0, 5):
        if gamer_list[i] :
            if gamer_list[i].startswith("KDF"):
                ###################게이머 라벨 그래픽 입력부분(1~5)####################
                if case_insensitive_search(gamer_list[i], "KDF DuDu"):
                    label_list.append("data/images/LT.png")
                    text_list.append(None)
                elif case_insensitive_search(gamer_list[i], "KDF youngjae"):
                    label_list.append("data/images/LJ.png")
                    text_list.append(None)
                elif case_insensitive_search(gamer_list[i], "KDF bulldog"):
                    label_list.append("data/images/LM.png")
                    text_list.append(None)
                elif case_insensitive_search(gamer_list[i], "KDF taeyoon"):
                    label_list.append("data/images/LA.png")
                    text_list.append(None)
                elif case_insensitive_search(gamer_list[i], "KDF jun"):
                    label_list.append("data/images/LS1.png")
                    text_list.append(None)
                elif case_insensitive_search(gamer_list[i], "KDF moham"):
                    label_list.append("data/images/LS2.png")
                    text_list.append(None)
                else:
                    label_list.append("data/images/L.png")
                    text_list.append(gamer_list[i])
            else:
                label_list.append(None)
                text_list.append(gamer_list[i])
        else:
            label_list.append(None)
            text_list.append(None)
    for i in range(5, 10):
        if gamer_list[i] :
            if gamer_list[i].startswith("KDF"):
                ###################게이머 라벨 그래픽 입력부분(6~10)####################
                if case_insensitive_search(gamer_list[i], "KDF DuDu"):
                    label_list.append("data/images/RT.png")
                    text_list.append(None)
                elif case_insensitive_search(gamer_list[i], "KDF youngjae"):
                    label_list.append("data/images/RJ.png")
                    text_list.append(None)
                elif case_insensitive_search(gamer_list[i], "KDF bulldog"):
                    label_list.append("data/images/RM.png")
                    text_list.append(None)
                elif case_insensitive_search(gamer_list[i], "KDF taeyoon"):
                    label_list.append("data/images/RA.png")
                    text_list.append(None)
                elif case_insensitive_search(gamer_list[i], "KDF jun"):
                    label_list.append("data/images/RS1.png")
                    text_list.append(None)
                elif case_insensitive_search(gamer_list[i], "KDF moham"):
                    label_list.append("data/images/RS2.png")
                    text_list.append(None)
                else:
                    label_list.append("data/images/R.png")
                    text_list.append(gamer_list[i])
            else:
                label_list.append(None)
                text_list.append(gamer_list[i])
        else:
            label_list.append(None)
            text_list.append(None)
    label_list.append(who_target)
    label_list.append("data/images/live.png")
    label_list.append("data/images/label.png")
    return label_list, text_list


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(10000)

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(0, 0, 1920, 1080)  # 윈도우의 위치를 (0, 0)으로, 크기를 (1920, 1080)으로 설정
        self.setWindowTitle("Overlay")

        font_id = QFontDatabase.addApplicationFont("data/DungGeunMo.ttf")  # 폰트를 추가
        font_str = QFontDatabase.applicationFontFamilies(font_id)[0]
        self.font = QFont(font_str)
        self.font.setPointSize(18)

        self.image_labels = [QLabel(self) for _ in range(14)]
        self.text_labels_1 = [QLabel(self) for _ in range(5)]
        self.text_labels_2 = [QLabel(self) for _ in range(9)]
        self.movie = QMovie("data/images/react/0.png")
        
        self.show()
        

    def remove_image(self, label):
        label.clear()

    def remove_text(self, label):
        label.clear()
        
    def update_data(self):
        with open('data/graphic_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        certain_list = data['certain_list']
        target = data['target']
        on = data['on']
        goodjob = data['goodjob']
        img_gj = "data/images/react/0.png"
        if goodjob == "t":
            random_number = random.randint(1, 9)
            img_gj = f"data/images/react/{random_number}.gif"

            
        label = labelling(certain_list, target)
        image_data = [
                (label[0][0], (0, 150), 220, 80),
                (label[0][1], (0, 253), 220, 80),
                (label[0][2], (0, 356), 220, 80),
                (label[0][3], (0, 459), 220, 80),
                (label[0][4], (0, 562), 220, 80),
                (label[0][5], (1700, 150), 220, 80),
                (label[0][6], (1700, 253), 220, 80),
                (label[0][7], (1700, 356), 220, 80),
                (label[0][8], (1700, 459), 220, 80),
                (label[0][9], (1700, 562), 220, 80),
                (label[0][10], (1335, 850), 305, 230),
                (label[0][11], (1790, 30), 160, 50),
                (label[0][12], (0, 962), 307, 118),
                (img_gj, (1335, 850), 305, 230)                
            ]

        text_data_1 = [
                (label[1][0], (10, 10)),
                (label[1][1], (10, 10)),
                (label[1][2], (10, 10)),
                (label[1][3], (10, 10)),
                (label[1][4], (10, 10))
            ]

        text_data_2 = [
                (label[1][5], (200, 10)),
                (label[1][6], (200, 10)),
                (label[1][7], (200, 10)),
                (label[1][8], (200, 10)),
                (label[1][9], (200, 10)),
                ("", (200, 10)),
                ("", (200, 10)),
                ("", (200, 10)),
                ("", (200, 10))
            ]
        if on == "on":
            for i, (image_path, position, width, height) in enumerate(image_data):
                self.add_image(self.image_labels[i], image_path, position, width, height)
                if i < 5:
                    self.add_text(self.text_labels_1[i], text_data_1[i], position, 1)
                else:
                    self.add_text(self.text_labels_2[i - 5], text_data_2[i - 5], position, 2)
            self.movie.setFileName(image_path)
            self.image_labels[13].setMovie(self.movie)
            self.movie.start()
            if goodjob == "f" :
                self.movie.stop()
        else :
            for i, (image_path, position, width, height) in enumerate(image_data):
                if i == 12:
                    self.add_image(self.image_labels[i], image_path, position, width, height)
                else:
                    self.remove_image(self.image_labels[i])
                self.movie.stop()
                if i < 5:
                    self.remove_text(self.text_labels_1[i])
                else:
                    self.remove_text(self.text_labels_2[i-5])
            
    def add_image(self, label, image_path, position, width, height):
        if image_path:
            pixmap = QPixmap(image_path)
            pixmap = pixmap.scaled(width, height, Qt.KeepAspectRatio)
            label.setPixmap(pixmap)
            label.setGeometry(position[0], position[1], pixmap.width(), pixmap.height())

    def add_text(self, label, text, position, group):
        font_id = QFontDatabase.addApplicationFont("data/DungGeunMo.ttf")
        font_data = QFontDatabase.applicationFontFamilies(font_id)[0]
        font = QFont(font_data)  # 폰트 생성
        font.setPointSize(18)
        
        font_metrics = QFontMetrics(font)
        
        if text[0]:
            label.setFont(self.font)
            label.setText(text[0])
            label.setStyleSheet("color: white")

            label_width = font_metrics.horizontalAdvance(text[0])
            label_height = 80

            if group == 1:
                label_x = position[0] + 105
                label_y = position[1]

            else:
                label_x = position[0] - label_width + 115
                label_y = position[1]

            label.setGeometry(label_x, label_y, label_width, label_height)
            label.show()


def open_graphics():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    sys.exit(app.exec_())
    

open_graphics()





