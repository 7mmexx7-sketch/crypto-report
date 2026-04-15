import requests

# 질문자님의 봇 토큰
TOKEN = "8548489549:AAHkc7-PZrGHWPk-7EpyhK7CpiD4ZOu8bQ4"

def hunt_for_chat_id():
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    res = requests.get(url).json()
    
    print("===================================")
    print("🕵️‍♂️ 봇이 기억하는 모든 방 번호 탐색 결과")
    print("===================================\n")
    
    found = False
    if res.get("ok"):
        for result in res.get("result", []):
            # 채널인 경우
            if "channel_post" in result:
                chat = result["channel_post"]["chat"]
                title = chat.get("title", "알 수 없는 채널")
                chat_id = chat.get("id")
                print(f"✅ [채널 발견] 이름: {title} / ID 번호: {chat_id}")
                found = True
            # 일반 대화방인 경우
            elif "message" in result:
                chat = result["message"]["chat"]
                title = chat.get("title", chat.get("first_name", "알 수 없는 방"))
                chat_id = chat.get("id")
                print(f"✅ [대화방 발견] 이름: {title} / ID 번호: {chat_id}")
                found = True
                
    if not found:
        print("⚠️ 아직 봇이 새 채널의 메시지를 읽지 못했습니다.")
        print("⚠️ 새 채널에 아무 글자나 하나 쓰고 1분 뒤에 다시 실행해보세요!")
        
    print("\n===================================")

hunt_for_chat_id()
