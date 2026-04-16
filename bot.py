import requests
from datetime import datetime
import os
import xml.etree.ElementTree as ET

# --- [정보 입력] ---
TELEGRAM_TOKEN = "8548489549:AAHkc7-PZrGHWPk-7EpyhK7CpiD4ZOu8bQ4"
# 원래 발송하시던 단일 방 번호로 복구되었습니다.
CHAT_IDS = ["-1003807258780"] 

CMC_API_KEY = "c59e814980984b0c9fdd8c1429c70fcd"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") 
# ------------------

def fetch_rss_news(url, limit=5):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code != 200:
            return ""
        root = ET.fromstring(res.content)
        news_text = ""
        for item in root.findall('.//item')[:limit]:
            title = item.find('title').text
            link = item.find('link').text
            news_text += f"Title: {title}\nLink: {link}\n\n"
        return news_text
    except:
        return ""

def get_market_briefing():
    """외신 소식을 분석하여 개별 요약, 시장 전체 동향, 그리고 트리거 퀘스천을 생성합니다."""
    if not OPENAI_API_KEY:
        return "분석 엔진 동기화가 진행 중입니다. 잠시 후 다시 확인해 주세요."
    
    ct_news = fetch_rss_news("https://cointelegraph.com/rss", limit=5)
    cd_news = fetch_rss_news("https://www.coindesk.com/arc/outboundfeeds/rss/", limit=5)
    
    combined_news = f"[Source: CoinTelegraph]\n{ct_news}\n[Source: CoinDesk]\n{cd_news}"

    if not ct_news and not cd_news:
        return "현재 글로벌 외신망 동기화 지연으로 인해 데이터를 불러올 수 없습니다."

    prompt = (
        "당신은 가상자산 리서치 수석 분석가입니다. 제공된 뉴스 목록을 바탕으로 세 가지 섹션을 작성하십시오. "
        "모든 답변에서 'AI' 또는 '인공지능'이라는 단어를 절대 사용하지 마십시오.\n\n"
        "섹션 1. 주요 뉴스 요약:\n"
        "가장 중요한 소식 6개를 선정하여 요약하십시오. 반드시 CoinTelegraph에서 3개, CoinDesk에서 3개를 선정하십시오. "
        "제목은 <b>제목</b> 형태로 작성하고, 뉴스 끝에 <a href=\"URL\">[상세 리포트 원문]</a> 링크를 포함하십시오.\n\n"
        "섹션 2. 시장 종합 분석 및 전망:\n"
        "위 6개 뉴스를 토대로 현재 가상자산 시장의 전체적인 동향과 핵심 트렌드를 3~4문장으로 요약하여 브리핑하십시오. "
        "전문적이고 객관적인 시각을 유지하십시오.\n\n"
        "섹션 3. 오늘의 토론 주제 (트리거 퀘스천):\n"
        "오늘의 시장 상황과 가장 밀접하게 연관된, 투자자들의 토론을 유도할 수 있는 예리한 질문을 하나 작성하십시오. "
        "예: '현재 비트코인의 단기 조정 국면에서, 여러분은 알트코인 비중을 늘릴 시점이라고 보십니까?'\n\n"
        "【준수 사항】\n"
        "1. 모든 이모티콘을 절대 사용하지 마십시오.\n"
        "2. 격식 있고 전문적인 문체로 작성하십시오.\n"
        "3. Markdown 기호 대신 텔레그램 HTML 태그(<b>, <a>)만 사용하십시오.\n\n"
        f"분석 데이터:\n{combined_news}"
    )
    
    try:
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.4
        }
        
        response = requests.post("
