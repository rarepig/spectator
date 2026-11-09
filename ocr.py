
import json
import uuid
import time
import requests
from google.cloud import vision
from google.cloud.vision_v1 import types
from PIL import Image, ImageFilter, ImageOps
from skimage.metrics import structural_similarity as ssim

def ocr_clova():
    with open("settings.json", encoding='utf-8') as file:
        data = json.load(file)
    ocr = data["ocr"]
    clova = data["clova"]

    request_json = {
        'images': [
            {
                'format': 'png',
                'name': 'screenshot',
                "templateIds": [25139]
            }
        ],
        'requestId': str(uuid.uuid4()),
        'version': 'V2',
        'timestamp': int(round(time.time() * 1000))
    }

    payload = {'message': json.dumps(request_json).encode('UTF-8')}
    files = [
    ('file', open("screenshot.png",'rb'))
    ]
    headers = {
    'X-OCR-SECRET': ocr
    }

    response = requests.request("POST", clova, headers=headers, data = payload, files = files)
    
    guess_name = []

    if response.status_code == 200:
        response_data = response.json()
        try:
            fields = response_data["images"][0]["fields"]
            with open("screenshot.json", "w", encoding="utf-8") as json_file:
                json.dump(fields, json_file, indent=4)
                
            for field in fields:
                guess_name.append(field["inferText"])  
        except KeyError:
            print("응답 데이터에서 필드를 찾을 수 없습니다.")
            return []

    else:
        print("API 요청 실패. 응답 코드:", response.status_code)
        
    return guess_name
            


def ocr_google():
    done = False
    count = 0
    while not done and count < 5:
        count += 1
        image = Image.open("screenshot.png")
        image_bw = image.convert("L")
        image_sharpened = image_bw.filter(ImageFilter.SHARPEN)
        image_inverted = ImageOps.invert(image_sharpened)
        threshold = 130
        image_inverted = image_inverted.point(lambda p: p > threshold and 255)
        crop_img1 = image_inverted.crop((0, 130, 180, 150))
        crop_img2 = image_inverted.crop((0, 233, 180, 253))
        crop_img3 = image_inverted.crop((0, 336, 180, 356))
        crop_img4 = image_inverted.crop((0, 439, 180, 459))
        crop_img5 = image_inverted.crop((0, 542, 180, 562))
        crop_img6 = image_inverted.crop((1740, 130, 1920, 150))
        crop_img7 = image_inverted.crop((1740, 233, 1920, 253))
        crop_img8 = image_inverted.crop((1740, 336, 1920, 356))
        crop_img9 = image_inverted.crop((1740, 439, 1920, 459))
        crop_img10 = image_inverted.crop((1740, 542, 1920, 562))
        combined = Image.new("L", (crop_img1.width, 10*crop_img1.height), 255)
        combined.paste(crop_img1, (0,0))
        combined.paste(crop_img2, (0,20))
        combined.paste(crop_img3, (0,40))
        combined.paste(crop_img4, (0,60))
        combined.paste(crop_img5, (0,80))
        combined.paste(crop_img6, (0,100))
        combined.paste(crop_img7, (0,120))
        combined.paste(crop_img8, (0,140))
        combined.paste(crop_img9, (0,160))
        combined.paste(crop_img10, (0,180))
        combined.save("screenshot_google.png")
        
        client = vision.ImageAnnotatorClient.from_service_account_json('data/platinum-hour-389310-1ddda0d2d7fb.json')

        with open('screenshot_google.png', 'rb') as image_file:
            content = image_file.read()

        image = types.Image(content=content)
        response = client.text_detection(image=image)
        texts = response.text_annotations

        result = []
        try:
            result = texts[0].description.split('\n')
        except KeyError:
            print("닉네임을 인식할 수 없습니다.")
        if len(result) == 10:
            done = True
        else:
            time.sleep(5)
    return result
