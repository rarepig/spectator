import subprocess
import webbrowser
import json

server_process = subprocess.Popen(["musictitle.exe"])
server_process = subprocess.Popen(["overlay.exe"])

with open('data/graphic_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

data['on'] = "off"

with open('data/graphic_data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f)
    
 
url = "http://127.0.0.1:5000/"

# 크롬 브라우저를 사용하여 URL 열기
webbrowser.register('chrome', None, webbrowser.BackgroundBrowser("C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"))
webbrowser.get('chrome').open(url)

# server.py 실행
server_process = subprocess.Popen(["python", "server.py"])

# 서버 프로세스의 실행이 완료될 때까지 대기
server_process.wait()





