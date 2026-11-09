import tkinter as tk
import pyautogui
import datetime
import time

bcstate = False 
running = False

def start_task():
    global bcstate
    global running
    running = True
    entries_value = []
    entries = [entry1, entry2, entry3, entry4, entry5, entry6]
    
    for entry in entries:
        if entry:
            entries_value.append(entry.get())
            
    update_label(entries_value, bcstate, running)
    
    for entry in entries:
        if entry:
            target_time = entry.get()
            current_time = datetime.datetime.now().strftime("%H:%M")
            if current_time == target_time:
                if bcstate:
                    pyautogui.hotkey('alt', 'Tab')
                    freecs_win = pyautogui.getWindowsWithTitle("FreecShot(32비트)")
                    if freecs_win:  # 만약 해당 제목의 창이 있다면
                        freecs = freecs_win[0]  # 첫 번째 창을 가져옴
                        
                        # 창을 활성화
                        freecs.activate()
                    print("방송 종료")
                    pyautogui.hotkey('alt', 'e')
                    time.sleep(300)
                    pyautogui.hotkey('alt', 'b')
                    bcstate = False
                else:
                    pyautogui.hotkey('alt', 'Tab')
                    freecs_win = pyautogui.getWindowsWithTitle("FreecShot(32비트)")
                    if freecs_win:  # 만약 해당 제목의 창이 있다면
                        freecs = freecs_win[0]  # 첫 번째 창을 가져옴
                        
                        # 창을 활성화
                        freecs.activate()
                    print("방송 시작")
                    pyautogui.hotkey('alt', 'g')
                    pyautogui.hotkey('alt', 'b')
                    pyautogui.hotkey('alt', 'Tab')
                    bcstate = True
    
    if running:
        window.after(60000, start_task)

def update_label(entries_value, bcstate, running):
    # entries_value를 이용하여 Label 위젯의 text 속성 업데이트
    if running :
        label0.config(text="자동 방송 ON", fg="red")
    else :
        label0.config(text="자동 방송 OFF", fg="blue")
    
    if bcstate : 
        label1.config(text="방송 송출 중입니다.", fg="red")
    else :
        label1.config(text="방송 대기 중입니다.", fg="blue")
    label3.config(text='\n'.join(entries_value))
    
def stop_task():
    global running
    running = False

# GUI 생성
window = tk.Tk()
window.title("작업 시간 설정")
window.geometry("300x500+2000+150")
window.resizable(False, False)

# 레이블 생성)
label0 = tk.Label(window)
label0.pack(pady=3)

label1 = tk.Label(window)
label1.pack(pady=3)
    
label2 = tk.Label(window, text="작업 시간을 입력하세요. (24시간, 12:00)")
label2.pack(pady=5)


# 입력 필드 생성
entry1 = tk.Entry(window)
entry2 = tk.Entry(window)
entry3 = tk.Entry(window)
entry4 = tk.Entry(window)
entry5 = tk.Entry(window)
entry6 = tk.Entry(window)

entry1.pack(pady=5)
entry2.pack(pady=5)
entry3.pack(pady=5)
entry4.pack(pady=5)
entry5.pack(pady=5)
entry6.pack(pady=5)


# 시작 버튼 생성
start_button = tk.Button(window, text="작업 시작", command=start_task)
start_button.pack(pady=5)

stop_button = tk.Button(window, text="작업 중지", command=stop_task)
stop_button.pack(pady=5)

global label3
label3 = tk.Label(window)
label3.pack(pady=5)


update_label([], bcstate, running)
# GUI 실행
window.mainloop()