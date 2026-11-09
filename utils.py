from riotwatcher import LolWatcher, ApiError
from datetime import datetime
import json
import win32gui
import time
import requests
import subprocess
import psutil
import os
import json
import urllib.request
import cv2



#### 동작 함수
              
def version_opt(ver):
    def data_update(ver):
        champions = f"http://ddragon.leagueoflegends.com/cdn/{ver}/data/en_US/champion.json"
        spells = f"http://ddragon.leagueoflegends.com/cdn/{ver}/data/en_US/summoner.json"
        items = f"http://ddragon.leagueoflegends.com/cdn/{ver}/data/en_US/item.json"

        print(champions)
        print(spells)
        print(items)


    # 챔피언/스펠/아이템 데이터 업데이트        
        response = urllib.request.urlopen(champions)        
        data = response.read().decode('utf-8')
        champion_data = json.loads(data)["data"]
        
        response = urllib.request.urlopen(spells)        
        data = response.read().decode('utf-8')
        spell_data = json.loads(data)["data"]
            
        response = urllib.request.urlopen(items)        
        data = response.read().decode('utf-8')
        item_data = json.loads(data)["data"]
            
        with open("data/champion.json", 'w') as f:
            json.dump(champion_data, f)
            
        with open("data/summoner.json", 'w') as f:
            json.dump(spell_data, f)
                
        with open("data/item.json", 'w') as f:
            json.dump(item_data, f)
            
    def img_data_update(ver):
        img_item = "http://ddragon.leagueoflegends.com/cdn/{ver}/img/item/{item}.png"
        download_folder = "./data/images/items"

        with open("data/item.json", encoding='utf-8') as file:
            data = json.load(file)
            
        item_list = list(data)
            
        for item in item_list:
            img_url = img_item.format(ver=ver, item=item)
            img_num = f'{item}.png'
            full_path = os.path.join(download_folder, f'{item}.png')
            
            if os.path.exists(full_path):
                os.remove(full_path)  
                
            try:
                urllib.request.urlretrieve(img_url, full_path)
                print(f'{img_num} 다운로드 완료')
            except urllib.error.HTTPError as e:
                print(f'{img_num} 다운로드 실패: {e}')
                pass
            
    def resize_images(folder_path):
        target_folder = "./data/images/zipped"

        if not os.path.exists(target_folder):
            os.makedirs(target_folder)

        for filename in os.listdir(folder_path):
            image_path = os.path.join(folder_path, filename)
            output_path = os.path.join(target_folder, filename)

            if os.path.exists(output_path):
                os.remove(output_path)

            image = cv2.imread(image_path)
            resized_image = cv2.resize(image, (10, 10))
            gray_image = cv2.cvtColor(resized_image, cv2.COLOR_BGR2GRAY)

            cv2.imwrite(output_path, gray_image)
                
    print(ver)
            
    data_update(ver)
    img_data_update(ver)
    img_folder_path = "./data/images/items"
    resize_images(img_folder_path)

def read_datafile():
    with open("data/registered.json", encoding='utf-8') as file:
        data = json.load(file)
        
    formed_data = {}
    
    for gamer in data:
        gamer_name = gamer["gamer_name"]
        summoner_names = gamer["summoner_names"]
        favorite = gamer["favorite"]
        formed_data[gamer_name] = [summoner_names, favorite]
        
    return formed_data

def spectate(target):
    with open("settings.json", encoding='utf-8') as file:
        data = json.load(file)
        api_key = data["api"]
    
    watcher = LolWatcher(api_key)
    my_region = 'kr'
    gamer = watcher.summoner.by_name(my_region, target)
    
    try:
        spect = watcher.spectator.by_summoner(my_region, gamer['id'])
        gameId = str(spect["gameId"])
        encryptionKey = spect["observers"]["encryptionKey"]
        gameType = spect["gameType"]
        gameMode = spect["gameMode"]
        playing_champ = None
        spell1 = None
        spell2 = None
        participants = []
        for participant in spect['participants']:
            name = participant.get('summonerName')
            participants.append(name)
            if participant.get('summonerId') == gamer["id"]:
                playing_champ = str(participant.get('championId'))
                spell1 = str(participant.get("spell1Id"))
                spell2 = str(participant.get("spell2Id"))
        start_time = datetime.fromtimestamp(spect['gameStartTime'] / 1000)
        game_length = datetime.now() - start_time
        return True, game_length, playing_champ, spell1, spell2, gameId, encryptionKey, gameType, gameMode, participants
    
    except ApiError as e:
        if isinstance(e, ApiError) and e.response.status_code == 404:
            return False, "", "", "", "", None, None, None, None, []
        elif isinstance(e, requests.exceptions.HTTPError) and e.response.status_code == 404:
            return False, "", "", "", "", None, None, None, None, []
        else:
            print("소환사를 찾는 과정에서 오류가 발생했습니다.")

def case_insensitive_search(a, b):
    if a.lower() == b.lower():
        return True
    else:
        return False

def update_datafile(gamer_name, summoner_names, favorite):
    with open("data/registered.json", encoding='utf-8') as file:
        data = json.load(file)
    
    found = False
    
    for gamer in data:
        if gamer["gamer_name"] == gamer_name:
            if summoner_names != None:
                gamer["summoner_names"] = summoner_names
            if favorite != None:
                gamer["favorite"] = favorite
            found = True
            break
        if case_insensitive_search(gamer["gamer_name"], gamer_name):
            gamer["gamer_name"] = gamer_name
            if summoner_names != None:
                gamer["summoner_names"] = summoner_names
            if favorite != None:
                gamer["favorite"] = favorite
            found = True
            break
            
    if not found:
        data.append({
            "gamer_name": gamer_name,
            "summoner_names": summoner_names,
            "favorite": 0})

    with open("data/registered.json", 'w') as f:
        json.dump(data, f)
     
def delete_target(target):
    with open("data/registered.json", encoding="utf-8") as file:
        data = json.load(file)

    for i, gamer in enumerate(data):
        if gamer["gamer_name"] == target or case_insensitive_search(gamer["gamer_name"], target) :
            del data[i]
            
    with open("data/registered.json", 'w') as f:
        json.dump(data, f)
        
def find_target(target):
    page_num = 1
    in_rank = False
    target_summoner_names = []

    for page_num in range(1,21):
        url = f"https://b2c-api-cdn.deeplol.gg/summoner/summoner-rank?platform_id=KR&lane=All&page={page_num}"
        response = requests.get(url)
        temp_data = response.json()
        for gamer in temp_data["summoner_rank_list"]:
            if gamer["team_as"] == "":
                if gamer["name"].lower() == target.lower():
                    target_summoner_names.append(gamer["summoner_name"])
                    gamer_name = gamer["name"]
                    in_rank = True
            else :
                if (gamer["team_as"].lower() +" " + gamer["name"].lower()) == target.lower():
                    target_summoner_names.append(gamer["summoner_name"])
                    gamer_name = gamer["team_as"] + " " + gamer["name"]
                    in_rank = True
                
    if in_rank:
        update_datafile(gamer_name, target_summoner_names, None)
        message = "해당 게이머의 소환사 이름을 업데이트 하였습니다."
    else :
        message = "랭크 내에서 해당 게이머를 찾을 수 없습니다."
        
    return message

def run_spectate(gameId, encryptionKey):
    with open("settings.json", encoding='utf-8') as file:
        data = json.load(file)
    path = data["path"]
    print(path)
    print(gameId)
    print(encryptionKey)
    content = '''rem OP.GG Spectate
SETLOCAL enableextensions enabledelayedexpansion
@echo off

echo -----------------------
echo Spectate by op.gg
echo -----------------------

set RADS_PATH="C:\Riot Games\League of Legends"

if exist "%RADS_PATH%\Game" (
	cd /d "!RADS_PATH!\Config"
	for /F "delims=" %%a in ('find "        locale: " LeagueClientSettings.yaml') do set "locale=%%a"
	for /F "tokens=2 delims=: " %%a in ("!locale!") do set "locale=%%a"

	SET RADS_PATH="!RADS_PATH!\Game"
	@cd /d !RADS_PATH!

	if exist "League of Legends.exe" (
		@start "" "League of Legends.exe" "spectator spectator-consumer.kr.lol.pvp.net:80 '''+encryptionKey+''' '''+gameId+''' KR" "-UseRads" "-Locale=!locale!" "-GameBaseDir=.."
		goto :eof
	)
)

if exist "%RADS_PATH%\RADS" (
	SET RADS_PATH="!RADS_PATH!\RADS"
	@cd /d !RADS_PATH!

	@cd /d "!RADS_PATH!\projects"
	for /d %%D in (league_client_*) do (
	    for /F "tokens=3,4 delims=_ " %%a in ("%%~nxD") do (
	        set locale=%%a_%%b
	    )
	)

	for /l %%a in (1,1,100) do if "!RADS_PATH:~-1!"==" " set RADS_PATH=!RADS_PATH:~0,-1!
	@cd /d "!RADS_PATH!\solutions\lol_game_client_sln\releases"

	set /a v0=0, v1=0, v2=0, v3=0
	set init=0
	for /d %%A in ("!RADS_PATH!\solutions\lol_game_client_sln\releases\*") do (
		set currentDirectory=%%~nxA

		for /F "tokens=1,2,3,4 delims=." %%i in ("!currentDirectory!") do (
			set /a test=%%i*1, test2=%%j*1, test3=%%k*1, test4=%%l*1

			if !init! equ 0 (
				set /a init=1, flag=1
			) else (
				set flag=0

				if !test! gtr !v0! (
					set flag=1
				) else (
					if !test2! gtr !v1! (
						set flag=1
					) else (
						if !test3! gtr !v2! (
							set flag=1
						) else (
							if !test4! gtr !v3! (
								set flag=1
							)
						)
					)
				)
			)

			if !flag! gtr 0 (
				set /a v0=!test!, v1=!test2!, v2=!test3!, v3=!test4!
			)
		)
	)

	if !init! equ 0 goto cannotFind
	set lolver=!v0!.!v1!.!v2!.!v3!

	@cd /d "!RADS_PATH!\solutions\lol_game_client_sln\releases\!lolver!\deploy"
	if exist "League of Legends.exe" (
		@start "" "League of Legends.exe" "spectator spectator-consumer.kr.lol.pvp.net:80 '''+encryptionKey+''' '''+gameId+''' KR" "-UseRads" "-Locale=!locale!" "-GameBaseDir=.."
		goto :eof
	)
)

echo ===================
echo KR: LOL
echo EN: Cannot found LOL directory path for automatic. Please see our spectate help page: http://www.op.gg/help/observer
echo ===================
@pause

:eof'''

    with open('spectate.bat', 'w') as file:
        file.write(content)

    print("spectate.bat 파일이 생성되었습니다.")
    
    bat_path = "spectate.bat"

    client = False
    while not client :
        subprocess.run(bat_path, check=True)
        time.sleep(15)
        window_handle = win32gui.FindWindow(None, "League of Legends (TM) Client")
        if window_handle != 0:
            client = True
        else :
            client = False
       
def is_process_running():
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == 'League of Legends.exe':
            return True
    return False



### 데이터 활용 함수

def find_champ(championId):
    with open("data/champion.json", encoding='utf-8') as file:
        data = json.load(file)
    
    for champion in data:
        if data[champion]["key"] == championId:
            chp_name = data[champion]["id"]
            return chp_name
            
    return None

def find_spell(spellId):
    with open("data/summoner.json", encoding='utf-8') as file:
        data = json.load(file)
        
    for spell in data:
        if data[spell]["key"] == spellId:
            spell_name = spell
            return spell_name
            
    return None



### 버튼

def button_favorite(favor, gamer_name):
    if favor == 1:
        return f'''<form method="POST" action="/registered/favorite">
                    <button type="submit" name="favorite" value="0, {gamer_name}">🧡</button>
                </form>'''
    else:
        return f'''<form method="POST" action="/registered/favorite">
                    <button type="submit" name="favorite" value="1, {gamer_name}">&#128420;</button>
                </form>'''

def button_refresh(gamer_name):
    return f'''<form method="POST" action="/registered/refresh">
                    <button type="submit" name="refresh" value="{gamer_name}">🔄</button>
                </form>'''               

def button_delete(gamer_name):
    return f'''<form method="POST" action="/registered/delete">
                    <button type="submit" name="delete" value="{gamer_name}">❌</button>
                </form>'''


