from flask import Flask, request, redirect
from utils import version_opt, run_spectate, read_datafile, spectate, update_datafile, delete_target, find_target, find_champ, find_spell, button_favorite, button_refresh, button_delete
from ingame import all_setting, checking_game_over
import pygetwindow as gw
import time
import random
import datetime
import json
import threading
import pyautogui
import win32gui
import subprocess

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 2

app = Flask(__name__)



### 템플릿

def title_table(link1, link2, link3):
    return f'''<!DOCTYPE html>
    <head>
    </head>
    <body>
        <p>&nbsp;</p>
        <table
        style="border-collapse: collapse; width: 60%; height: 40px; background-color: #3598db; margin-left: auto; margin-right: auto;"
        border="0">
        <tbody>
            <tr>
                <td style="text-align: center;"><h1><a href="/" text-decoration: none; color: black; >자동 관전 시스템</a></h1></td>
            </tr>
        </tbody>
    </table>
    <p>&nbsp;</p>
    <p style="text-align: right;">by. 엄마몰래관전</p>
    <table style="border-collapse: collapse; width: 100%; height: 40px; background-color: #c2e0f4; margin-left: auto; margin-right: auto;">
        <tbody>
            <tr>
                <td style="text-align: center; width: 30%; border: 5px solid white;"><a href="{link1}">관전하기</a></td>
                <td style="text-align: center; width: 30%; border: 5px solid white;"><a href="{link2}">자동 관전</a></td>
                <td style="text-align: center; width: 30%; border: 5px solid white;"><a href="{link3}">등록된 게이머</a></td>
            </tr>
        </tbody>
    </table>
'''

def registered_content(message):
    unsorted_gamers = read_datafile()
    gamers = sorted(unsorted_gamers.items(), key=lambda x: x[0])
    gamer_list = ""
    gamer_name_list = []
    for gamer in gamers:
        gamer_name_list.append(gamer[0])
        summoner_names = ', '.join(str(x) for x in gamer[1][0])
        gamer_list += f'''<tr style="border-bottom: 1px solid black;">
            <td style="text-align: center;">
            <input type="checkbox" onchange="toggleCheckbox('{gamer[0]}')" name="check_{gamer[0]}" value="{gamer[0]}"></td>
            <td style="text-align: center;">{gamer[0]}</td>
            <td style="text-align: center;">{button_favorite(gamer[1][1], gamer[0])}</td>
            <td style="text-align: center;">{button_refresh(gamer[0])}</td>
            <td style="text-align: center;">{button_delete(gamer[0])}</td>
            <td>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{summoner_names}</td></tr>'''

    return title_table("/manualspectate", "/autospectate", ".") + '''
        <p>&nbsp;</p>
        <h2>게이머 정보 업데이트</h2>
        <form method="POST" action=".">
            <input type="text" name="target" placeholder="활동 이름">&nbsp;
            <input type="submit" value="업데이트">
        </form>
        ''' + message + '''</br>
        (2000위까지 검색 @deeplol)
        <p>&nbsp;</p>
        <h2>등록된 게이머</h2>
    <table style="border-collapse: collapse; width: 100%; margin-left: auto; margin-right: auto;">
    <tr style="background-color: #c2e0f4; border-bottom: 1px solid black;">
        <th style="width: 5%;"><input type="checkbox" id="check_all" onchange="toggleCheckboxesAll()"></th>
        <th style="width: 20%;">활동 이름</th>
        <th style="width: 5%;">
            <span>
            <form method="POST" action="/registered/favorite_together">
            <button type="submit" name="together" value="{checked_gamers}">🧡</button></form>
            <form method="POST" action="/registered/unfavorite_together">
            <button type="submit" name="together" value="{checked_gamers}">&#128420;</button></form>
            </span>
                    </th>
        <th style="width: 5%;">
        <form method="POST" action="/registered/refresh_together">
        <button type="submit" name="together" value="{checked_gamers}">🔄</button></form>
        </th>
        <th style="width: 5%;">
        <form method="POST" action="/registered/delete_together">
        <button type="submit" name="together" value="{checked_gamers}">❌</button></form>
        </th>
        <th>소환사 이름</th>
    </tr>
        ''' + gamer_list + '''
    </table>

    <script>
var checked_gamers = []

function buttonValueSetting() {
    var buttons = document.getElementsByName("together");
    buttons.forEach(function(button) {button.value = checked_gamers});
}        
        
function toggleCheckboxesAll() {
    const checkboxes = document.querySelectorAll('input[name^="check_"]');
    const checkAllCheckbox = document.getElementById('check_all');
    checkboxes.forEach(function(checkbox) {
        if (checkAllCheckbox.checked) {
            checkbox.checked = checkAllCheckbox.checked;
            checked_gamers = ''' + str(gamer_name_list) + ''';
            buttonValueSetting();
        }
        else {
            checkbox.checked = checkAllCheckbox.checked;
            checked_gamers = [];
            buttonValueSetting();
        }
    });
}

function toggleCheckbox(name) {
    const checkbox = document.getElementsByName("check_"+name)[0];
    if (checkbox.checked) {
        checked_gamers.push(name);
        buttonValueSetting();
    }
    else {
        filtered_checked_gamers = checked_gamers.filter((item) => item != name);
        checked_gamers = filtered_checked_gamers
        buttonValueSetting();
    }
}
    </script>
    </body>
    <head><title>등록된 소환사</title></head>
    </html>'''



# 요청

@app.route('/')
def index():
    global auto, view, end_time
    end_time = None
    auto = False
    view = False
    with open("settings.json", encoding='utf-8') as file:
        data = json.load(file)
    ver = data["ver"]
    api = data["api"]
    ocr = data["ocr"]
    clova = data["clova"]
    path = data["path"]
    return '''<!DOCTYPE html>
<head><title>자동 관전 시스템</title>
<body>
    <p>&nbsp;</p>
    '''+ title_table("/manualspectate", "/autospectate", "/registered") + '''
    <p>&nbsp;</p>
    <h2>환경 설정</h2>
    <p>버전 정보: '''+ str(ver) +'''</p>
    <p>Riot Api: '''+ str(api) +'''</p>
    <p>Clova OCR: '''+ str(ocr) +'''</p>
    <p>Clova url: '''+ str(clova) +'''</p>
    <p>League of Legend.exe 경로: '''+ str(path) +'''</p>
    <form method="POST" action="/update">
        <input type="text" name="ver" placeholder="버전 정보">&nbsp;
        <input type="submit" value="최적화">    (약 5분 소요)</form> 
    <form method="POST" action="/api">
        <input type="text" name="api" placeholder="Api Key">&nbsp;
        <input type="submit" value="입력">
        </form>
    <form method="POST" action="/ocr">
        <input type="text" name="ocr" placeholder="Clova OCR">&nbsp;
        <input type="submit" value="입력">
        </form>
    <form method="POST" action="/clova">
        <input type="text" name="clova" placeholder="Clova Api url">&nbsp;
        <input type="submit" value="입력">
        </form>
    <form method="POST" action="/path">
        <input type="text" name="path" placeholder="League of Legend.exe 경로">&nbsp;
        <input type="submit" value="입력">
        </form>
        <p><참고> <a href="https://ddragon.leagueoflegends.com/api/versions.json">모든 버전 정보</a></p>
</html>'''


@app.route('/update', methods=['POST'])
def update():
    ver = request.form['ver']
    with open("settings.json", encoding='utf-8') as file:
        data = json.load(file)
        data["ver"] = ver
        
    with open("settings.json", 'w') as f:
        json.dump(data, f)
        
    version_opt(ver)

    return redirect("/")

@app.route('/api', methods=['POST'])
def api():
    api = request.form['api']
    with open("settings.json", encoding='utf-8') as file:
        data = json.load(file)
        data["api"] = api
        
    with open("settings.json", 'w') as f:
        json.dump(data, f)
        
    return redirect("/")

@app.route('/ocr', methods=['POST'])
def ocr():
    ocr = request.form['ocr']
    with open("settings.json", encoding='utf-8') as file:
        data = json.load(file)
        data["ocr"] = ocr
        
    with open("settings.json", 'w') as f:
        json.dump(data, f)
        
    return redirect("/")

@app.route('/clova', methods=['POST'])
def clova():
    clova = request.form['clova']
    with open("settings.json", encoding='utf-8') as file:
        data = json.load(file)
        data["clova"] = clova
        
    with open("settings.json", 'w') as f:
        json.dump(data, f)
        
    return redirect("/")

@app.route('/path', methods=['POST'])
def path():
    path = request.form['path']
    with open("settings.json", encoding='utf-8') as file:
        data = json.load(file)
        data["path"] = path
        
    with open("settings.json", 'w') as f:
        json.dump(data, f)
        
    return redirect("/")

@app.route('/manualspectate')
def manualspectate():
    global auto, view, end_time
    end_time = None
    auto = False
    view = False
    unsorted_gamers = read_datafile()
    gamers = sorted(unsorted_gamers.items(), key=lambda x: x[0])
    gamer_list = ""
    favored_gamer_summoners = []     
    for gamer in gamers:
        if gamer[1][1] == 1:
            for summoner in gamer[1][0]:
                favored_gamer_summoners.append(summoner)
                state = spectate(summoner)

                playing_champ = f"http://ddragon.leagueoflegends.com/cdn/13.11.1/img/champion/{find_champ(state[2])}.png"
                spell1 = f"http://ddragon.leagueoflegends.com/cdn/13.11.1/img/spell/{find_spell(state[3])}.png"
                spell2 = f"http://ddragon.leagueoflegends.com/cdn/13.11.1/img/spell/{find_spell(state[4])}.png"
                gameId = state[5]
                encryptionKey = state[6]
                
                if state[0] and state[7]=="MATCHED_GAME" and state[8]=="CLASSIC":
                    button_spectate = f'''<form method="POST" action="/spectate">
                    <input type="hidden" name="gameId" value="{gameId}">
                    <input type="hidden" name="encryptionKey" value="{encryptionKey}">
                    <button type="submit">👀</button>
                </form>'''
                else:
                    button_spectate = "&nbsp;"
                    
                if state[0]:
                    view_state = "게임 중"
                    total_seconds = int(state[1].total_seconds())
                else:
                    view_state = ""
                    total_seconds = 0
                    
                gamer_list += f'''<tr style="border-bottom: 1px solid black;">
            <td style="text-align: center;">{gamer[0]}</td>
            <td style="text-align: center;">{summoner}</td>
            <td style="text-align: center;">
            <img src={playing_champ} alt="" style="width: 20%;">
            <img src={spell1} alt="" style="width: 10%;">
            <img src={spell2} alt="" style="width: 10%;">
            </td>
            <td style="text-align: center;">{view_state}</td>
            <td style="text-align: center;"><span id="game_time_{summoner}" datatotalseconds="{total_seconds}"></span></td>
            <td style="text-align: center;">{button_spectate}</td></tr>'''

    return '''<!DOCTYPE html>
<head><title>관전하기</title>
<body>
    <p>&nbsp;</p>
    '''+ title_table("/manualspectate", "/autospectate", "/registered") + '''
    <p>&nbsp;</p>
    <h2>관전하기</h2>
    <table style="border-collapse: collapse; width: 100%; margin-left: auto; margin-right: auto;">
    <tr style="background-color: #c2e0f4; border-bottom: 1px solid black;">
        <th style="width: 20%;">활동 이름</th>
        <th>소환사 이름</th>
        <th style="width: 20%;">&nbsp;</th>
        <th style="width: 10%;">상태</th>
        <th style="width: 20%;">게임 시간</th>
        <th style="width: 10%;">관전하기</th>
    </tr>''' + gamer_list + '''</table>
    <script>var count = 0
function updateGameTime() {
    count++
    const favored_gamer_summoners = ''' + str(favored_gamer_summoners) + ''';
    console.log(favored_gamer_summoners);
       console.log("흐른 시간:" + count);
    favored_gamer_summoners.forEach(function(summoner) {
        const elementId = "game_time_" + summoner;
            console.log(elementId);
        const element = document.getElementById(elementId);
                    console.log(element);
        const startGameTime = parseInt(element.getAttribute("datatotalseconds"));
        if (startGameTime == 0) {
            element.innerHTML = "";
        }
        else {
            const currentGameTime = formatTime(startGameTime+count);
            element.innerHTML = currentGameTime;
            console.log(startGameTime);
            console.log(currentGameTime);
            console.log(count)};
    });
}
    function formatTime(time) {
    const minutes = Math.floor(time / 60);
    const seconds = time % 60;
    const formattedTime = padZero(minutes) + ":" + padZero(seconds);
    return formattedTime;
}
function padZero(num) {
    return num.toString().padStart(2, "0");
}

setInterval(updateGameTime, 1000);</script>
</body>
</html>'''

@app.route('/autospectate', methods=['GET', 'POST'])
def autospectate():
    global auto, view, end_time
    end_time = None
    if request.method == 'GET':
        auto = False
        view = False
        button = '''<form method="POST" action="/autospectate" style="text-align: center;">
            <input type="text" name="endtime" placeholder="관전 시간 입력(단위:시간)"></br></br>
                    <button type="submit" name="auto" value="on" style="button; font-size: 2em; width: 300px; height: 80px; text-align: center;">
                    자동 관전 시작</button></div>
                    </form>
                <div style="text-align: center;">
                    <p>⌨ 시작 전에 화상 키보드를 열어주세요. (창 활성화 상태)</p>
                    <p>⚠ 주의 - 자동 관전 중에 다른 페이지로 이동하지 마세요.</p>
            </div>'''
    else :
        if request.form["auto"] == "off":
            auto = False
            view = False
            button = '''<form method="POST" action="/autospectate" style="text-align: center;">
                        <input type="text" name="endtime" placeholder="관전 시간 입력(단위:시간)"></br></br>
                    <button type="submit" name="auto" value="on" style="button; font-size: 2em; width: 300px; height: 80px; text-align: center;">
                    자동 관전 시작</button></div>
                    </form>
                <div style="text-align: center;">
                    <p>⌨ 시작 전에 화상 키보드를 열어주세요.</p>
                    <p>⚠ 주의 - 자동 관전 중에 다른 페이지로 이동하지 마세요.</p>
            </div>'''
        else :
            with open('data/graphic_data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            time_stamp = datetime.datetime.now()
            end_time = time_stamp + datetime.timedelta(hours=int(request.form["endtime"]))
            time_stamp_str = time_stamp.strftime("%Y-%m-%d %H:%M")
            end_time_str2 = end_time.strftime("%Y-%m-%d %H:%M")
            
            data['start'] = time_stamp_str
            data['end'] = end_time_str2
            
            with open('data/graphic_data.json', 'w', encoding='utf-8') as f:
                json.dump(data, f)
        
            auto = True
            view = False
            button = '''<form method="POST" action="/autospectate" style="text-align: center;">
                종료시간 : ''' + end_time_str2 + '''</br></br>
                <button type="submit" name="auto" value="off" style="button; font-size: 2em; width: 300px; height: 80px; text-align: center;">
                자동 관전 중지</button></div>
                </form>
                <div style="text-align: center;">
                    <p>🕑 1분 간격으로 관전 가능한 게임을 검색합니다.</p>
                    <p>⚠ 주의 - 자동 관전 중에 다른 페이지로 이동하지 마세요.</p>
            </div>'''

    unsorted_gamers = read_datafile()
    gamers = sorted(unsorted_gamers.items(), key=lambda x: x[0])
    gamer_list = ""
    order = []
    for gamer in gamers:
        if gamer[1][1] == 1:
            order.append(gamer[1])
            for summoner in gamer[1][0]:
                gamer_list += f'''<tr style="border-bottom: 1px solid black;">
                <td style="text-align: center;">{gamer[0]}</td>
                <td style="text-align: center;">{summoner}</td>'''

    def spectate_loop():
        global view
        available_list = []
        interval = 60
        global count_game_search
        count_game_search = 0
        old = []
        global air
        air = False
        while auto and datetime.datetime.now() < end_time:
            musictitle = win32gui.FindWindow(None, "musictitle")
            if musictitle == 0 :
                subprocess.Popen(["musictitle.exe"])
            overlay = win32gui.FindWindow(None, "Overlay")
            if overlay == 0 :
                subprocess.Popen(["overlay.exe"])
            if not view:
                # 순회하며 게임 리스트 만들기
                for gamer in order:
                    for summoner in gamer[0]:
                        print(summoner)
                        state = spectate(summoner)
                        if state[0] and 270 < state[1].total_seconds() < 4000 and state[7]=="MATCHED_GAME" and state[8]=="CLASSIC":
                            available_list.append([state[1].total_seconds(), state[5], state[6], state[9], summoner])
                # 비교하여 가장 시간 짧은 것 열기
                sorted_list = sorted(available_list, key=lambda x: x[0]) 
                sorted_list_ordered = []
                if len(sorted_list) >= 2 :
                    temp_list = [sorted_list[0]]
                    for i in range(1, len(sorted_list)):
                        if -30 <= sorted_list[i][0] - sorted_list[i-1][0] <= 30:
                            temp_list.append(sorted_list[i])
                        else :
                            random.shuffle(temp_list)
                            sorted_list_ordered.extend(temp_list)
                            temp_list = [sorted_list[i]]
                    random.shuffle(temp_list)
                    sorted_list_ordered.extend(temp_list)
                    sorted_list = sorted_list_ordered
                if sorted_list :
                    for i in range(len(sorted_list)) :
                        if not sorted_list[i][1] in old :
                            print("==== 관전 게임 정보 ====")
                            print("gameId:" + sorted_list[i][1])
                            print("encryptionKey:" + sorted_list[i][2])
                            print("참가자 목록:" + str(sorted_list[i][3]))
                            print("관전게이머:" + sorted_list[i][4])
                            view = True
                            count_game_search = 0
                            current_time = datetime.datetime.now().time()
                            # 스크림 시간 제외
                            if not (datetime.time(13, 00) <= current_time <= datetime.time(17, 0) or datetime.time(18, 30) <= current_time <= datetime.time(22, 30)):
                                if not air :
                                    try :   
                                        pyautogui.keyDown('ctrl')
                                        pyautogui.press('o')
                                        pyautogui.keyUp('ctrl')   
                                            
                                    except KeyError:
                                        pass  
                                    air = True
                            if air:
                                run_spectate(sorted_list[i][1], sorted_list[i][2])
                                game_start = all_setting(sorted_list[i][3], sorted_list[i][4]) ############## 게임이 실행되면 작동하는 함수
                                if game_start :
                                    print("화면 세팅 완료")
                                    checking_game_over(sorted_list[i][4])
                                view = False
                                old.append(sorted_list[i][1])
                                break
                            else:
                                break
            count_game_search += 1
            current_time = datetime.datetime.now().time()
            if air:
                print("현재 방송 중...")
                if (datetime.time(13, 00) <= current_time <= datetime.time(17, 0) or datetime.time(18, 30) <= current_time <= datetime.time(22, 30)):
                    try :    
                        pyautogui.keyDown('ctrl')
                        pyautogui.press('e')
                        pyautogui.keyUp('ctrl')
                        time.sleep(60)
                        
                        pyautogui.keyDown('ctrl')
                        pyautogui.press('o')
                        pyautogui.keyUp('ctrl')
                        time.sleep(3)   
                        
                        pyautogui.moveTo(3130, 730)
                        pyautogui.click()
                        pyautogui.click()
                        pyautogui.moveTo(10, 10)
                        time.sleep(3) 
                        
                        pyautogui.keyDown('ctrl')
                        pyautogui.press('g')
                        pyautogui.keyUp('ctrl')  
                    except KeyError:
                        pass  
                    air = False
                    count_game_search = 0
                else:
                    if count_game_search == 15:
                        try :   
                            pyautogui.keyDown('ctrl')
                            pyautogui.press('e')
                            pyautogui.keyUp('ctrl')
                            time.sleep(60)
                            
                            pyautogui.keyDown('ctrl')
                            pyautogui.press('o')
                            pyautogui.keyUp('ctrl')  
                            time.sleep(3)  
                            
                            pyautogui.moveTo(3130, 730)
                            pyautogui.click()
                            pyautogui.click()
                            pyautogui.moveTo(10, 10)
                            time.sleep(3) 
                            
                            pyautogui.keyDown('ctrl')
                            pyautogui.press('g')
                            pyautogui.keyUp('ctrl')  
                        except KeyError:
                            pass  
                        air = False
                        count_game_search = 0
            else:
                print("방송 대기 중..")
            view = False
            print("1분 후 새로운 게임 검색, " + str(count_game_search)) 
            time.sleep(interval)

    my_thread = threading.Thread(target=spectate_loop)
    my_thread.start()
    
    return '''<!DOCTYPE html>
        <head><title>자동 관전</title></head>
        <body>
            <p>&nbsp;</p>
            '''+ title_table("/manualspectate", "/autospectate", "/registered") + '''
            <p>&nbsp;</p>
            <div style="display: flex; justify-content: center; align-items: center;">
            ''' + button + '''
            <h2>관전하는 소환사</h2>
            <table style="border-collapse: collapse; width: 100%; margin-left: auto; margin-right: auto;">
            <tr style="background-color: #c2e0f4; border-bottom: 1px solid black;">
                <th style="width: 20%;">활동 이름</th>
                <th>소환사 이름</th>
            </tr>''' + gamer_list + '''</table>
        </body>
        </html>'''

@app.route('/registered/', methods=['GET', 'POST'])
def registered():
    global auto, view, end_time
    end_time = None
    auto = False
    view = False
    if request.method == 'GET':
        message = "게이머를 검색하세요."
        return registered_content(message)
    else :
        target = request.form['target']
        if target == "":
            return "다시 입력해주세요."
        else:
            message = find_target(target)
            return registered_content(message)

@app.route('/spectate', methods=['POST'])
def start_spectate():
    gameId = request.form['gameId']
    encryptionKey = request.form['encryptionKey']
    run_spectate(gameId, encryptionKey)
    
    return redirect("/manualspectate")

@app.route('/registered/favorite', methods=['POST'])
def favorite():
    toggle_favorite = request.form['favorite']
    gamer_name = toggle_favorite.split(", ")[1]
    favor = int(toggle_favorite.split(", ")[0])
    update_datafile(gamer_name, None, favor)
    return redirect("/registered")
    
@app.route('/registered/favorite_together', methods=['POST'])
def favorite_together():
    toggle_favorite = request.form['together']
    if toggle_favorite != "{checked_gamers}":
        fmd_toggle_favorite = toggle_favorite.split(",")
        for gamer in fmd_toggle_favorite:
            update_datafile(gamer, None, 1)
    return redirect("/registered")

@app.route('/registered/unfavorite_together', methods=['POST'])
def unfavorite_together():
    toggle_unfavorite = request.form['together']
    if toggle_unfavorite != "{checked_gamers}":
        fmd_toggle_unfavorite = toggle_unfavorite.split(",")
        for gamer in fmd_toggle_unfavorite:
            update_datafile(gamer, None, 0)
    return redirect("/registered")
    
@app.route('/registered/refresh', methods=['POST'])
def refresh():
    target = request.form['refresh']
    find_target(target)
    return redirect("/registered")

@app.route('/registered/refresh_together', methods=['POST'])
def refresh_together():
    refresh_gamers = request.form['together']
    if refresh_gamers != "{checked_gamers}":
        fmd_refresh_gamers = refresh_gamers.split(",")
        for gamer in fmd_refresh_gamers:
            find_target(gamer)
    return redirect("/registered")
  
@app.route('/registered/delete', methods=['POST'])
def delete():
    target = request.form['delete']
    delete_target(target)
    return redirect("/registered")

@app.route('/registered/delete_together', methods=['POST'])
def delete_together():
    delete_gamers = request.form['together']
    if delete_gamers != "{checked_gamers}":
        fmd_delete_gamers = delete_gamers.split(",")
        for gamer in fmd_delete_gamers:
            delete_target(gamer)
    return redirect("/registered")



# 실행

app.run(port=5000)