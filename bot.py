import requests
from datetime import datetime
import os

# --- [정보 입력] ---
TELEGRAM_TOKEN = "8548489549:AAHkc7-PZrGHWPk-7EpyhK7CpiD4ZOu8bQ4"

# ⭐ 드디어 완성된 완벽한 배달 명부!
CHAT_IDS = [
    "-1003807258780", # 기존 마이코인 리포트 방 (2,800명)
    "-1002443665222"  # 질문자님이 직접 캐낸 새 채널 방!
] 

CMC_API_KEY = "c59e814980984b0c9fdd8c1429c70fcd"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# ------------------

def get_ai_news_briefing():
    """해외 핫 이슈를 가져와 AI가 한국어로 요약합니다."""
    if not OPENAI_API_KEY:
        return "⚠️ OpenAI API 키가 설정되지 않아 뉴스를 가져올 수 없습니다."
    
    try:
        news_url = "https://cryptopanic.com/api/v1/posts/?auth_token=PUBLIC&filter=hot"
        news_data = requests.get(news_url).json()
        raw_news = ""
        for post in news_data['results'][:12]:
            raw_news += f"Title: {post['title']}\nLink: {post['url']}\n\n"

        prompt = f"당신은 가상자산 전문가입니다. 아래 뉴스를 한국어로 핵심만 5~7개 요약하세요. 제목은 굵게 처리하고 이모지를 사용하세요. 각 뉴스 끝에 [원문] 링크를 포함하세요.\n\n{raw_news}"
        
        headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
        payload = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.5
        }
        
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"뉴스 요약 중 오류 발생: {e}"

def get_crypto_report():
    try:
        # 데이터 수집 (시총, 도미넌스, 가격, 김프, 공탐지수)
        cmc_url = "https://pro-api.coinmarketcap.com/v1/global-metrics/quotes/latest"
        cmc_res = requests.get(cmc_url, headers={"X-CMC_PRO_API_KEY": CMC_API_KEY}).json()
        btc_dom = cmc_res['data']['btc_dominance']
        total_mcap = cmc_res['data']['quote']['USD']['total_market_cap']

        upbit_res = requests.get("https://api.upbit.com/v1/ticker?markets=KRW-BTC").json()
        upbit_price = float(upbit_res[0]['trade_price'])
        
        binance_res = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT").json()
        bin
