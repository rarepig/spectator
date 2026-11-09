import spotipy
import json
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from spotipy.oauth2 import SpotifyOAuth

class TransparentWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set initial value of graphic_data file
        self.on = None

        # Get currently playing music information from Spotify API
        self.song_title = "Loading..."
        self.artist_names = ""

        font_id = QFontDatabase.addApplicationFont("data/DungGeunMo.ttf")
        font_data = QFontDatabase.applicationFontFamilies(font_id)[0]
        self.font = QFont(font_data)  # create font
        self.font.setPointSize(15)
        
        # set transparent window
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowFlags(Qt.FramelessWindowHint)

        # Add a label and configure the initial settings for the label.
        self.label = QLabel("🎵 " + self.song_title + " - " + self.artist_names, self)
        self.setGeometry(0, 0, 310, 240)
        self.label.setStyleSheet("color: white; background-color: transparent")
        self.label.adjustSize()

        # set timer for updating song info
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_song_info)
        self.update_timer.start(5000)  # update song info every 5 seconds

        # set timer for moving text
        self.move_timer = QTimer()
        self.move_timer.timeout.connect(self.move_text)
        self.move_timer.start(100)  # move text every 0.1 second


    def get_currently_playing_title(self):
        client_id = "" # Enter your Spotify client ID.
        client_secret = "" # Enter your Spotify client secret.
        redirect_uri = "http://localhost:8888/callback" # Enter the redirect URI of the Spotify application.

        scope = "user-read-currently-playing"
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, scope=scope))

        try:
            current_track = sp.current_user_playing_track()
            if current_track is not None:
                song_title = current_track["item"]["name"]
                artists = current_track["item"]["artists"]
                artist_names = [artist["name"] for artist in artists]
                return song_title, artist_names
            else:
                print("Could not get the currently playing music.")
                return "", []
        except spotipy.exceptions.SpotifyException as e:
            print("An error occurred accessing the Spotify API:", str(e))

    def update_song_info(self):
        # Update currently playing title
        self.song_title, self.artist_names = self.get_currently_playing_title()
        
        # Update font settings
        with open('data/graphic_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.on = data['on']  # get 'on' value from data

        font_id = QFontDatabase.addApplicationFont("data/DungGeunMo.ttf")
        font_data = QFontDatabase.applicationFontFamilies(font_id)[0]
        self.font = QFont(font_data)  # create font
        if self.on == 'on':
            self.font.setPointSize(15)
            self.label.move(self.label.pos().x(), 20)  # update label Y position

        else:
            self.font.setPointSize(20)
            self.label.move(self.label.pos().x(), 160)  # update label Y position


        # Update label font
        self.label.setFont(self.font)

        # Update label text
        artist_names_str = ', '.join(self.artist_names)
        self.label.setText("🎵 " + self.song_title + " - " + artist_names_str)
        self.label.adjustSize()

    def move_text(self):
        # move the position of the label to the left
        self.label.move(self.label.pos().x() - 5, self.label.pos().y())
        # If the label is completely out of the window, move it back to the far right by the window's width
        if self.label.pos().x() + self.label.width() < 0:
            self.label.move(self.width(), self.label.pos().y())
            
        # Update font settings
        with open('data/graphic_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.on = data['on']  # get 'on' value from data
        
        # Update Y position
        if self.on == 'on':
            self.label.move(self.label.pos().x(), 20)  # update label Y position
        else:
            self.label.move(self.label.pos().x(), 150)  # update label Y position


                                
if __name__ == "__main__":
    app = QApplication([])
    window = TransparentWindow()
    window.show()
    app.exec_()