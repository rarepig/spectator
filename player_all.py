import json
import requests

def update_all_summoners():
    data = []
    gamer_list = []
    for page_num in range(1,21):
        url = f"https://b2c-api-cdn.deeplol.gg/summoner/summoner-rank?platform_id=KR&lane=All&page={page_num}"
        response = requests.get(url)
        temp_data = response.json()
        for gamer in temp_data["summoner_rank_list"]:
            if gamer["pro_streamer"] != "":
                if gamer["team_as"] == "":
                    gamer_name = gamer["name"]
                else:
                    gamer_name = gamer["team_as"] + " " + gamer["name"]
                summoner_name = gamer["summoner_name"]
                if gamer_name in gamer_list:
                    for gamer_dict in data:
                        if gamer_dict["gamer_name"] == gamer_name:
                            gamer_dict["summoner_names"].append(summoner_name)
                            break
                else:
                    data.append({
                    "gamer_name": gamer_name,
                    "summoner_names": [summoner_name],
                    "favorite": 0})
                    gamer_list.append(gamer_name)
    with open("data/registered.json", "w") as json_file:
        json.dump(data, json_file)
        
update_all_summoners()
print("딥롤로부터 2000위까지의 소환사 정보 다운로드 완료\n즐겨찾기 재설정이 필요합니다.")