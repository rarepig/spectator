import json
import pygetwindow as gw
import pyautogui
import json
import time
import subprocess
import win32gui
import Levenshtein
from ocr import ocr_clova, ocr_google
from PIL import Image
from utils import spectate
import numpy as np
from skimage.metrics import structural_similarity as ssim

pyautogui.FAILSAFE = False


def calculate_similarity(str1, str2):
    distance = Levenshtein.distance(str1, str2)
    max_length = max(len(str1), len(str2))
    similarity = 1 - (distance / max_length)
    return similarity


def screenshot_temp():
    time.sleep(10)
    window = gw.getWindowsWithTitle("League of Legends (TM) Client")[0]

    x, y, width, height = window.left, window.top, window.width, window.height
    print(x, y, width, height)
    
    screenshot = pyautogui.screenshot(region=(x, y, width, height))
    
    if screenshot is not None:
        screenshot.save("screenshot.png")
        print("화면 캡처 완료")
        
def ocr_names(participants):
    guess_name = []   
    # guess_name = ocr_clova()
    guess_name = ocr_google()
    name_compare_similarity = []   

    for i in range(len(guess_name)):
        if guess_name[i] != "":
            for gamer in participants:
                name_compare_similarity.append(calculate_similarity(gamer, guess_name[i]))
            max_value = max(name_compare_similarity)
            max_index = name_compare_similarity.index(max_value)
            name_compare_similarity = []                    
            guess_name[i] = participants[max_index]
        else:
            guess_name[i] = "Who!"
                
    return guess_name   


def activate_program_window(win_name):
    windows = pyautogui.getWindowsWithTitle(win_name)
    if windows:  # 만약 해당 제목의 창이 있다면
        window = windows[0]  # 첫 번째 창을 가져옴
        
        # 창을 활성화
        window.activate()


def screen_setting():
    windows = pyautogui.getWindowsWithTitle("화상 키보드")
    if windows:  # 만약 해당 제목의 창이 있다면
        window = windows[0]  # 첫 번째 창을 가져옴
        
        # 창의 크기를 변경
        window.resizeTo(1000, 300)
        window.moveTo(500, 300)
    
    print("ing")
        
    pyautogui.moveTo(880, 450)
    pyautogui.click()

    pyautogui.moveTo(980, 450)
    pyautogui.click()
    
    print("done")


def camera_key(num):
    if 0 <= num <= 9:
        location = [
            [630, 400], [680, 400],
            [730, 400], [780, 400],
            [830, 400], [600, 450],
            [650, 450], [700, 450],
            [750, 450], [800, 450]]
        x = location[num][0]
        y = location[num][1]

        pyautogui.moveTo(x, y)
        pyautogui.click()
        pyautogui.click()
        pyautogui.moveTo(10, 10)
    print("camera ready")


def kill_assist(num, old, death_old): 
    if num:
        goodjob = False
        screenshot = pyautogui.screenshot(region=(0, 0, 1920, 1080))
        image = screenshot.convert("L")

        left = 805 + (num//5)*258
        top = 875 + (num%5)*44
        right = left + 65
        bottom = top + 5
        
        if old :
            point = image.crop((left, top, right, bottom))
            death = point.crop((28, 0, 38, 5))
        else:
            old = image.crop((left, top, right, bottom))
            death_old = old.crop((28, 0, 38, 5))
            return goodjob, old, death_old
            
        width, height = point.size
        point_change = False   
        for x in range(width):
            for y in range(height):
                pixel_point = point.getpixel((x, y))
                pixel_old = old.getpixel((x, y))
                if pixel_point != pixel_old:
                    point_change = True
                    break
            else:
                continue
            break
            
        if point_change:
            width, height = death.size
            for x in range(width):
                pixel_death = death.getpixel((x,y))
                pixel_death_old = death_old.getpixel((x,y))
                if pixel_death != pixel_death_old :
                    return goodjob, None, None
            goodjob = True
        return goodjob, point, death
    else:
        return False, None, None


def all_setting(participants, target):
    print("참가자 중 " + target+ " 찾는 중")
    count = 0
    found = False
    game_start = False
    game_start_count = 0
    while not game_start:
        screenshot_temp()
        image = Image.open("screenshot.png")
        crop_img1 = image.crop((900, 2, 1020, 30))
        crop_img1 = crop_img1.convert("L")
        crop_img2 = Image.open("cropped.png").convert("L")
        
        crop_img1_np = np.array(crop_img1)
        crop_img2_np = np.array(crop_img2)
        
        s = ssim(crop_img1_np, crop_img2_np)
        
        if s != 1.0:
            game_start = True
            while count < 2 and not found:
                screenshot_temp()
                guess_list = ocr_names(participants)
                num = None
                
                try:
                    num = guess_list.index(target)
                    print("참가자 순서:" + str(num))
                    found = True
                    screen_setting()
                    camera_key(num)
                except ValueError:
                    print(target + "을(를) 찾을 수 없습니다.")
                    
                time.sleep(5)
                count += 1
        else:
            print("게임이 시작되지 않았습니다. ", s)
            game_start_count += 1
            
            if game_start_count == 3:
                pyautogui.keyDown('alt')  # Alt 키를 누릅니다.
                pyautogui.press('f4')  # F4 키를 한 번 누릅니다.
                pyautogui.keyUp('alt')  # Alt 키를 떼어냅니다.
                return False
            
            time.sleep(10)   
  
    if not found:
        print(target + "을(를) 찾을 수 없습니다. 자동 카메라 모드로 관전을 시작합니다.")
        guess_list = ["", "", "", "", "", "", "", "", "", ""]
    else:
        print("카메라 세팅 완료")    

    with open("data/graphic_data.json", encoding='utf-8') as file:
        data = json.load(file)

    data['certain_list'] = guess_list
    data['target'] = target
    data['on'] = "on"
    data['num'] = num

    with open('data/graphic_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f)
    
    print("그래픽 표시")   
    return True
        
def checking_game_over(target):
    on = True
    old = None
    death_old = None
    print("게임 종료 확인 중...")
    while on:
        musictitle = win32gui.FindWindow(None, "musictitle")
        if musictitle == 0 :
            subprocess.Popen(["musictitle.exe"])
        overlay = win32gui.FindWindow(None, "Overlay")
        if overlay == 0 :
            subprocess.Popen(["overlay.exe"])
        spect = spectate(target)
        print(spect[0])
        if not spect[0]:
            time.sleep(240)
            print("게임 종료")
            time.sleep(1)
            pyautogui.moveTo(960, 640)
            pyautogui.click()
            pyautogui.click()
            pyautogui.moveTo(10, 10)

            with open("data/graphic_data.json", encoding='utf-8') as file:
                data = json.load(file)

            data['certain_list'] = ["", "", "", "", "", "", "", "", "", ""]
            data['target'] = ""
            data['on'] = "off"

            with open('data/graphic_data.json', 'w', encoding='utf-8') as f:
                json.dump(data, f)
                
            on = False
        else:
            print("현재 게임 중")
            with open("data/graphic_data.json", encoding='utf-8') as file:
                data = json.load(file)
            num = data['num']
            tracker = kill_assist(num, old, death_old)
            old = tracker[1]
            death_old = tracker[2]
            if tracker[0] :
                with open("data/graphic_data.json", encoding='utf-8') as file:
                    data = json.load(file)
                data['goodjob'] = 't'
                with open('data/graphic_data.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f)
                time.sleep(10)
                with open("data/graphic_data.json", encoding='utf-8') as file:
                    data = json.load(file)
                data['goodjob'] = 'f'
                with open('data/graphic_data.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f)
            time.sleep(5)
    return on



# screen_setting()

# camera_key(0)
# camera_key(1)
# camera_key(2)
# camera_key(3)
# camera_key(4)
# camera_key(5)
# camera_key(6)
# camera_key(7)
# camera_key(8)
# camera_key(9)

